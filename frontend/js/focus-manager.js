/**
 * FocusManager - Unified focus navigation for mouse, remote, and touch
 * Handles spatial navigation, focus zones, and keyboard event routing
 */
class FocusManager {
  constructor() {
    this.currentFocus = null;
    this.zones = new Map();
    this.activeZone = null;
    this.isTouchDevice = window.matchMedia('(hover: none)').matches;
    this.isCoarsePointer = window.matchMedia('(pointer: coarse)').matches;
    this.enabled = true;

    this._init();
  }

  _init() {
    // Keyboard events for remote/keyboard navigation
    document.addEventListener('keydown', (e) => this._handleKeyDown(e));

    // Mouse events - auto focus on hover
    document.addEventListener('mouseover', (e) => this._handleMouseOver(e));

    // Touch detection
    window.matchMedia('(hover: none)').addEventListener('change', (e) => {
      this.isTouchDevice = e.matches;
    });

    // Prevent default for arrow keys to avoid scrolling
    document.addEventListener('keydown', (e) => {
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
        const focused = document.querySelector('[data-focusable].focused');
        if (focused) e.preventDefault();
      }
    });
  }

  _handleKeyDown(e) {
    if (!this.enabled) return;

    switch (e.key) {
      case 'ArrowUp':
        this._moveFocus('up');
        break;
      case 'ArrowDown':
        this._moveFocus('down');
        break;
      case 'ArrowLeft':
        this._moveFocus('left');
        break;
      case 'ArrowRight':
        this._moveFocus('right');
        break;
      case 'Enter':
      case ' ':
        this._activateFocused(e);
        break;
      case 'Escape':
      case 'Backspace':
        this._handleBack(e);
        break;
      case 'Tab':
        this._handleTab(e);
        break;
    }
  }

  _handleMouseOver(e) {
    if (this.isTouchDevice) return;

    const focusable = e.target.closest('[data-focusable]');
    if (focusable) {
      this.setFocus(focusable, 'mouse');
    }
  }

  _moveFocus(direction) {
    const current = document.querySelector('[data-focusable].focused');
    if (!current) {
      // No focus yet - focus first element in active zone
      const first = this._getFirstFocusable();
      if (first) this.setFocus(first, 'keyboard');
      return;
    }

    const candidates = this._getNavigationCandidates(current, direction);
    if (candidates.length > 0) {
      const target = candidates[0];
      this.setFocus(target, 'keyboard');
      this._scrollIntoViewIfNeeded(target, direction);
    }
  }

  _getNavigationCandidates(current, direction) {
    const rect = current.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;

    const allFocusable = Array.from(
      current.closest('[data-focus-zone]')?.querySelectorAll('[data-focusable]') ||
      document.querySelectorAll('[data-focusable]:not(.hidden)')
    ).filter(el => {
      if (el === current) return false;
      if (el.closest('.overlay-hidden') || el.offsetParent === null) return false;
      return true;
    });

    const scored = allFocusable.map(el => {
      const r = el.getBoundingClientRect();
      const ex = r.left + r.width / 2;
      const ey = r.top + r.height / 2;

      let score = Infinity;
      let valid = false;

      switch (direction) {
        case 'up':
          if (ey < cy - 5) {
            valid = true;
            score = Math.abs(cx - ex) * 2 + Math.abs(cy - ey);
          }
          break;
        case 'down':
          if (ey > cy + 5) {
            valid = true;
            score = Math.abs(cx - ex) * 2 + Math.abs(cy - ey);
          }
          break;
        case 'left':
          if (ex < cx - 5) {
            valid = true;
            score = Math.abs(cy - ey) * 2 + Math.abs(cx - ex);
          }
          break;
        case 'right':
          if (ex > cx + 5) {
            valid = true;
            score = Math.abs(cy - ey) * 2 + Math.abs(cx - ex);
          }
          break;
      }

      return { el, score, valid };
    });

    return scored.filter(s => s.valid).sort((a, b) => a.score - b.score).map(s => s.el);
  }

  _activateFocused(e) {
    const focused = document.querySelector('[data-focusable].focused');
    if (focused) {
      focused.click();
      if (e) e.preventDefault();
    }
  }

  _handleBack(e) {
    // Dispatch custom event for back navigation
    document.dispatchEvent(new CustomEvent('app:back', { bubbles: true }));
    if (e) e.preventDefault();
  }

  _handleTab(e) {
    e.preventDefault();
    // Tab cycles through focus zones
    const zones = Array.from(document.querySelectorAll('[data-focus-zone]:not(.hidden)'));
    if (zones.length === 0) return;

    const currentZone = document.querySelector('[data-focusable].focused')?.closest('[data-focus-zone]');
    const currentIdx = currentZone ? zones.indexOf(currentZone) : -1;
    const nextIdx = e.shiftKey
      ? (currentIdx - 1 + zones.length) % zones.length
      : (currentIdx + 1) % zones.length;

    const firstInZone = zones[nextIdx].querySelector('[data-focusable]');
    if (firstInZone) this.setFocus(firstInZone, 'keyboard');
  }

  setFocus(el, source) {
    if (!el || el.offsetParent === null) return;

    // Remove previous focus
    const prev = document.querySelector('[data-focusable].focused');
    if (prev) prev.classList.remove('focused');

    el.classList.add('focused');
    this.currentFocus = el;

    // Update active zone
    const zone = el.closest('[data-focus-zone]');
    if (zone) this.activeZone = zone.dataset.focusZone;

    // Dispatch focus change event
    el.dispatchEvent(new CustomEvent('focus:changed', {
      bubbles: true,
      detail: { source, previous: prev }
    }));
  }

  clearFocus() {
    const focused = document.querySelector('[data-focusable].focused');
    if (focused) focused.classList.remove('focused');
    this.currentFocus = null;
  }

  _getFirstFocusable() {
    const zone = this.activeZone
      ? document.querySelector(`[data-focus-zone="${this.activeZone}"]`)
      : document.querySelector('[data-focus-zone]');

    if (zone) return zone.querySelector('[data-focusable]');
    return document.querySelector('[data-focusable]');
  }

  _scrollIntoViewIfNeeded(el, direction) {
    const container = el.closest('.scroll-container') || el.parentElement;
    if (!container) return;

    const rect = el.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();

    if (direction === 'up' && rect.top < containerRect.top) {
      container.scrollTop -= (containerRect.top - rect.top + 20);
    } else if (direction === 'down' && rect.bottom > containerRect.bottom) {
      container.scrollTop += (rect.bottom - containerRect.bottom + 20);
    } else if (direction === 'left' && rect.left < containerRect.left) {
      container.scrollLeft -= (containerRect.left - rect.left + 20);
    } else if (direction === 'right' && rect.right > containerRect.right) {
      container.scrollLeft += (rect.right - containerRect.right + 20);
    }
  }

  registerZone(name, element) {
    this.zones.set(name, element);
  }

  setZone(name) {
    this.activeZone = name;
    const first = this._getFirstFocusable();
    if (first) this.setFocus(first, 'keyboard');
  }

  enable() { this.enabled = true; }
  disable() { this.enabled = false; }
}

// Global singleton
window.focusManager = new FocusManager();
