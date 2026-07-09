/**
 * App - Main application logic
 * Tab switching, player overlay, back navigation, swipe gestures, route management
 */
class App {
  constructor() {
    this.currentTabIndex = 0;
    this.totalTabs = 4; // home, search, favorites, settings
    this.isPlayerOpen = false;
    this.pageContainer = null;
    this.tabItems = [];
    this.playerOverlay = null;
    this.playerBackdrop = null;
    this.swipeStartX = 0;
    this.swipeStartY = 0;
    this.swipeStartTime = 0;
    this.isSwiping = false;

    this._init();
  }

  _init() {
    this.pageContainer = document.getElementById('page-container');
    this.playerOverlay = document.getElementById('player-overlay');
    this.playerBackdrop = document.getElementById('player-backdrop');
    this.tabItems = Array.from(document.querySelectorAll('.tab-bar .tab-item'));

    this._bindTabEvents();
    this._bindBackEvent();
    this._bindSwipeGesture();
    this._bindPlayerEvents();
  }

  _bindTabEvents() {
    this.tabItems.forEach((tab, index) => {
      tab.addEventListener('click', () => {
        this.switchTab(index);
      });
    });
  }

  _bindBackEvent() {
    document.addEventListener('app:back', () => {
      if (this.isPlayerOpen) {
        this.closePlayer();
      }
    });
  }

  _bindSwipeGesture() {
    const content = this.pageContainer;
    if (!content) return;

    content.addEventListener('touchstart', (e) => {
      this.swipeStartX = e.touches[0].clientX;
      this.swipeStartY = e.touches[0].clientY;
      this.swipeStartTime = Date.now();
      this.isSwiping = true;
    }, { passive: true });

    content.addEventListener('touchend', (e) => {
      if (!this.isSwiping) return;
      this.isSwiping = false;

      const dx = e.changedTouches[0].clientX - this.swipeStartX;
      const dy = e.changedTouches[0].clientY - this.swipeStartY;
      const dt = Date.now() - this.swipeStartTime;

      // Only horizontal swipes > 80px in < 400ms
      if (Math.abs(dx) > 80 && Math.abs(dx) > Math.abs(dy) * 1.5 && dt < 400) {
        if (dx < 0 && this.currentTabIndex < this.totalTabs - 1) {
          this.switchTab(this.currentTabIndex + 1);
        } else if (dx > 0 && this.currentTabIndex > 0) {
          this.switchTab(this.currentTabIndex - 1);
        }
      }
    }, { passive: true });
  }

  _bindPlayerEvents() {
    if (this.playerBackdrop) {
      this.playerBackdrop.addEventListener('click', () => {
        this.closePlayer();
      });
    }
  }

  switchTab(index) {
    if (index < 0 || index >= this.totalTabs) return;
    if (index === this.currentTabIndex) return;

    this.currentTabIndex = index;

    // Update tab bar active state
    this.tabItems.forEach((tab, i) => {
      tab.classList.toggle('active', i === index);
    });

    // Slide page container
    if (this.pageContainer) {
      this.pageContainer.style.transform = `translateX(-${index * 100}%)`;
    }

    // Notify page modules
    document.dispatchEvent(new CustomEvent('app:tabchange', {
      detail: { index, tabName: this._getTabName(index) }
    }));

    // Clear focus and set first focusable in new zone
    if (window.focusManager) {
      window.focusManager.clearFocus();
      const zones = ['home', 'search', 'favorites', 'settings'];
      window.focusManager.setZone(zones[index]);
    }
  }

  _getTabName(index) {
    const names = ['home', 'search', 'favorites', 'settings'];
    return names[index] || 'home';
  }

  showPlayer(videoData) {
    if (!this.playerOverlay || !this.playerBackdrop) return;

    this.isPlayerOpen = true;

    // Show backdrop
    this.playerBackdrop.classList.remove('hidden');
    this.playerBackdrop.classList.remove('overlay-backdrop-exit');
    this.playerBackdrop.classList.add('overlay-backdrop-enter');

    // Show overlay
    this.playerOverlay.classList.remove('hidden');
    this.playerOverlay.classList.remove('overlay-exit');
    this.playerOverlay.classList.add('overlay-enter');

    // Notify player module
    if (window.playerPage) {
      window.playerPage.open(videoData);
    }

    // Set focus to player zone
    if (window.focusManager) {
      window.focusManager.setZone('player');
    }
  }

  closePlayer() {
    if (!this.playerOverlay || !this.playerBackdrop) return;
    if (!this.isPlayerOpen) return;

    // Animate out
    this.playerOverlay.classList.remove('overlay-enter');
    this.playerOverlay.classList.add('overlay-exit');

    this.playerBackdrop.classList.remove('overlay-backdrop-enter');
    this.playerBackdrop.classList.add('overlay-backdrop-exit');

    // Hide after animation
    setTimeout(() => {
      this.playerOverlay.classList.add('hidden');
      this.playerOverlay.classList.remove('overlay-exit');
      this.playerBackdrop.classList.add('hidden');
      this.playerBackdrop.classList.remove('overlay-backdrop-exit');

      this.isPlayerOpen = false;

      // Reset focus to current tab zone
      if (window.focusManager) {
        window.focusManager.setZone(this._getTabName(this.currentTabIndex));
      }
    }, 300);
  }

  goBack() {
    if (this.isPlayerOpen) {
      this.closePlayer();
    }
  }

  getCurrentTab() {
    return this.currentTabIndex;
  }

  getTabName() {
    return this._getTabName(this.currentTabIndex);
  }
}

// Initialize app on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.app = new App();
});
