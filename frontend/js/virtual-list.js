/**
 * VirtualList - Infinite virtual list with DOM recycling
 * Fixed item height, scroll listener, placeholder rendering
 */
class VirtualList {
  constructor(container, options) {
    this.container = typeof container === 'string'
      ? document.querySelector(container)
      : container;

    if (!this.container) {
      console.error('VirtualList: container not found');
      return;
    }

    this.itemHeight = options.itemHeight || 200;
    this.renderItem = options.renderItem || (() => '');
    this.itemCount = options.itemCount || 0;
    this.bufferSize = options.bufferSize || 5;
    this.className = options.className || '';

    this.items = [];
    this.spacer = null;
    this.contentEl = null;
    this.pool = [];
    this.visibleStart = 0;
    this.visibleEnd = 0;
    this.isScrolling = false;
    this.scrollTimeout = null;

    this._init();
  }

  _init() {
    // Create structure
    this.spacer = document.createElement('div');
    this.spacer.className = 'virtual-list-spacer';
    this.container.appendChild(this.spacer);

    this.contentEl = document.createElement('div');
    this.contentEl.className = 'virtual-list-content';
    this.container.appendChild(this.contentEl);

    // Bind scroll
    this.container.addEventListener('scroll', () => this._onScroll());
  }

  _onScroll() {
    if (this.isScrolling) return;
    this.isScrolling = true;

    requestAnimationFrame(() => {
      this._updateVisibleRange();
      this.isScrolling = false;
    });

    clearTimeout(this.scrollTimeout);
    this.scrollTimeout = setTimeout(() => {
      this._recycle();
    }, 150);
  }

  _updateVisibleRange() {
    const scrollTop = this.container.scrollTop;
    const containerHeight = this.container.clientHeight;

    const start = Math.max(0, Math.floor(scrollTop / this.itemHeight) - this.bufferSize);
    const end = Math.min(
      this.itemCount,
      Math.ceil((scrollTop + containerHeight) / this.itemHeight) + this.bufferSize
    );

    if (start === this.visibleStart && end === this.visibleEnd) return;

    this.visibleStart = start;
    this.visibleEnd = end;

    this._render();
  }

  _render() {
    // Update spacer height
    this.spacer.style.height = (this.itemCount * this.itemHeight) + 'px';

    // Position content
    this.contentEl.style.transform = `translateY(${this.visibleStart * this.itemHeight}px)`;

    // Get existing DOM nodes
    const existingNodes = Array.from(this.contentEl.children);
    const existingMap = new Map();
    existingNodes.forEach(node => {
      existingMap.set(node.dataset.index, node);
    });

    const fragment = document.createDocumentFragment();
    const newMap = new Map();

    for (let i = this.visibleStart; i < this.visibleEnd; i++) {
      const indexStr = String(i);
      if (existingMap.has(indexStr)) {
        // Reuse existing node
        const node = existingMap.get(indexStr);
        newMap.set(indexStr, node);
        fragment.appendChild(node);
      } else {
        // Create new node
        const node = document.createElement('div');
        node.className = this.className;
        node.dataset.index = indexStr;
        node.style.height = this.itemHeight + 'px';
        node.style.overflow = 'hidden';
        node.innerHTML = this.renderItem(i, this.items[i]);
        fragment.appendChild(node);
        newMap.set(indexStr, node);
      }
    }

    // Recycle unused nodes
    existingNodes.forEach(node => {
      if (!newMap.has(node.dataset.index)) {
        this.pool.push(node);
      }
    });

    // Append fragment
    this.contentEl.innerHTML = '';
    this.contentEl.appendChild(fragment);
  }

  _recycle() {
    // Clean up pool to prevent memory leaks
    if (this.pool.length > 50) {
      this.pool.splice(0, this.pool.length - 20);
    }
  }

  setData(items) {
    this.items = items;
    this.itemCount = items.length;
    this.visibleStart = 0;
    this.visibleEnd = 0;
    this.container.scrollTop = 0;
    this.contentEl.innerHTML = '';
    this._updateVisibleRange();
  }

  getItemCount() {
    return this.itemCount;
  }

  appendItems(newItems) {
    const oldCount = this.itemCount;
    this.items = this.items.concat(newItems);
    this.itemCount = this.items.length;
    this._updateVisibleRange();
    return oldCount;
  }

  prependItems(newItems) {
    this.items = newItems.concat(this.items);
    this.itemCount = this.items.length;
    const scrollTop = this.container.scrollTop;
    this.container.scrollTop = scrollTop + (newItems.length * this.itemHeight);
    this._updateVisibleRange();
  }

  refresh() {
    this.visibleStart = 0;
    this.visibleEnd = 0;
    this.contentEl.innerHTML = '';
    this._updateVisibleRange();
  }

  scrollToIndex(index) {
    if (index < 0 || index >= this.itemCount) return;
    this.container.scrollTop = index * this.itemHeight;
    this._updateVisibleRange();
  }

  destroy() {
    this.container.removeEventListener('scroll', () => this._onScroll());
    this.contentEl.innerHTML = '';
    this.spacer.remove();
    this.contentEl.remove();
    this.items = [];
    this.pool = [];
  }
}

window.VirtualList = VirtualList;
