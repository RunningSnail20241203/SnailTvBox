/**
 * SearchPage - Search page logic
 * Virtual keyboard input, search history (localStorage), mock search results
 */
class SearchPage {
  constructor() {
    this.query = '';
    this.searchHistory = [];
    this.results = [];
    this.isShiftActive = false;
    this.container = null;
    this.maxHistory = 20;
    this.storageKey = 'tvbox_search_history';

    this._init();
  }

  _init() {
    this.container = document.getElementById('search-page');
    if (!this.container) return;

    this._loadHistory();
    this._renderKeyboard();
    this._renderHistory();
    this._bindEvents();
  }

  _loadHistory() {
    try {
      const data = localStorage.getItem(this.storageKey);
      this.searchHistory = data ? JSON.parse(data) : [];
    } catch (e) {
      this.searchHistory = [];
    }
  }

  _saveHistory() {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.searchHistory));
    } catch (e) {
      // Storage full or unavailable
    }
  }

  _renderKeyboard() {
    const keyboard = this.container.querySelector('.virtual-keyboard');
    if (!keyboard) return;

    keyboard.innerHTML = '';

    const rows = [
      ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
      ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
      ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
      ['SHIFT', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', 'DEL'],
      ['SEARCH', 'SPACE', 'CLEAR']
    ];

    rows.forEach(row => {
      const rowEl = document.createElement('div');
      rowEl.className = 'keyboard-row';

      row.forEach(key => {
        const keyEl = document.createElement('div');
        keyEl.className = 'key-item';
        keyEl.setAttribute('data-focusable', 'true');

        switch (key) {
          case 'SHIFT':
            keyEl.classList.add('wide', 'accent');
            keyEl.textContent = 'Shift';
            keyEl.dataset.key = 'shift';
            break;
          case 'DEL':
            keyEl.classList.add('wide', 'accent');
            keyEl.textContent = '删除';
            keyEl.dataset.key = 'del';
            break;
          case 'SPACE':
            keyEl.classList.add('wide');
            keyEl.textContent = '空格';
            keyEl.dataset.key = 'space';
            break;
          case 'SEARCH':
            keyEl.classList.add('wide', 'accent');
            keyEl.textContent = '搜索';
            keyEl.dataset.key = 'search';
            break;
          case 'CLEAR':
            keyEl.classList.add('wide');
            keyEl.textContent = '清空';
            keyEl.dataset.key = 'clear';
            break;
          default:
            keyEl.textContent = this.isShiftActive ? key : key.toLowerCase();
            keyEl.dataset.key = 'char';
            keyEl.dataset.char = this.isShiftActive ? key : key.toLowerCase();
            break;
        }

        keyEl.addEventListener('click', () => this._handleKey(keyEl.dataset.key, keyEl.dataset.char));
        rowEl.appendChild(keyEl);
      });

      keyboard.appendChild(rowEl);
    });
  }

  _handleKey(keyType, char) {
    const input = this.container.querySelector('.search-input');

    switch (keyType) {
      case 'char':
        this.query += char;
        break;
      case 'space':
        this.query += ' ';
        break;
      case 'del':
        this.query = this.query.slice(0, -1);
        break;
      case 'shift':
        this.isShiftActive = !this.isShiftActive;
        this._renderKeyboard();
        return;
      case 'clear':
        this.query = '';
        break;
      case 'search':
        this._doSearch();
        return;
    }

    if (input) input.value = this.query;
  }

  _renderHistory() {
    const historyList = this.container.querySelector('.history-list');
    if (!historyList) return;

    historyList.innerHTML = '';

    if (this.searchHistory.length === 0) {
      historyList.innerHTML = '<div style="text-align:center;color:var(--text-tertiary);font-size:var(--font-size-sm);padding:var(--space-xl);">暂无搜索记录</div>';
      return;
    }

    this.searchHistory.forEach(term => {
      const item = document.createElement('div');
      item.className = 'history-item';
      item.setAttribute('data-focusable', 'true');
      item.innerHTML = `<span class="history-icon">&#128337;</span><span>${term}</span>`;
      item.addEventListener('click', () => {
        this.query = term;
        const input = this.container.querySelector('.search-input');
        if (input) input.value = term;
        this._doSearch();
      });
      historyList.appendChild(item);
    });
  }

  _doSearch() {
    const trimmed = this.query.trim();
    if (!trimmed) return;

    // Add to history
    this._addHistory(trimmed);

    // Generate mock results
    this.results = this._generateMockResults(trimmed);

    // Render results
    this._renderResults();
  }

  _addHistory(term) {
    // Remove duplicates
    this.searchHistory = this.searchHistory.filter(h => h !== term);
    // Add to front
    this.searchHistory.unshift(term);
    // Limit count
    if (this.searchHistory.length > this.maxHistory) {
      this.searchHistory = this.searchHistory.slice(0, this.maxHistory);
    }
    this._saveHistory();
    this._renderHistory();
  }

  _clearHistory() {
    this.searchHistory = [];
    this._saveHistory();
    this._renderHistory();
  }

  _generateMockResults(query) {
    const results = [];
    const baseTitles = [
      `${query}第一季`, `${query}第二季`, `${query}电影版`, `新${query}`,
      `${query}归来`, `${query}之巅峰对决`, `${query}前传`, `${query}外传`,
      `${query}番外篇`, `${query}特别篇`, `终极${query}`, `${query}重生`,
      `${query}崛起`, `${query}传奇`, `${query}新世界`, `${query}风云再起`,
      `${query}之龙腾四海`, `${query}决战`, `${query}英雄传`, `我的${query}`
    ];

    const directors = ['陈思诚', '郭帆', '饺子', '吴京', '张艺谋', '徐克', '乌尔善', '宁浩', '韩寒', '贾玲'];
    const years = ['2024', '2023', '2022', '2021', '2020'];
    const regions = ['中国大陆', '中国香港', '美国', '韩国', '日本'];

    for (let i = 0; i < baseTitles.length; i++) {
      results.push({
        id: i,
        title: baseTitles[i],
        director: directors[i % directors.length],
        year: years[i % years.length],
        region: regions[i % regions.length],
        description: `关于"${query}"的精彩故事，剧情跌宕起伏，扣人心弦。`,
        thumb: `https://picsum.photos/seed/search${i + 1}/200/300`
      });
    }

    return results;
  }

  _renderResults() {
    const resultsList = this.container.querySelector('.results-list');
    const resultsHeader = this.container.querySelector('.results-header');

    if (resultsHeader) {
      resultsHeader.textContent = `搜索结果 (${this.results.length}个)`;
    }

    if (!resultsList) return;

    resultsList.innerHTML = '';

    if (this.results.length === 0) {
      resultsList.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">&#128269;</div>
          <div class="empty-text">未找到相关结果</div>
        </div>
      `;
      return;
    }

    this.results.forEach(result => {
      const item = document.createElement('div');
      item.className = 'search-result-item card-item';
      item.setAttribute('data-focusable', 'true');

      item.innerHTML = `
        <div class="result-thumb">
          <img src="${result.thumb}" alt="${result.title}" loading="lazy" onerror="this.style.display='none'">
        </div>
        <div class="result-info">
          <div class="result-title">${result.title}</div>
          <div class="result-meta">${result.year} · ${result.region} · ${result.director}</div>
          <div class="result-desc">${result.description}</div>
        </div>
      `;

      item.addEventListener('click', () => {
        if (window.app) {
          window.app.showPlayer({
            ...result,
            cast: '未知',
            update: '全1集',
            quality: '1080P'
          });
        }
      });

      resultsList.appendChild(item);
    });
  }

  _bindEvents() {
    // Clear history button
    const clearBtn = this.container.querySelector('.history-clear-btn');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => this._clearHistory());
    }

    // Clear input button
    const clearInputBtn = this.container.querySelector('.search-clear-btn');
    if (clearInputBtn) {
      clearInputBtn.addEventListener('click', () => {
        this.query = '';
        const input = this.container.querySelector('.search-input');
        if (input) input.value = '';
      });
    }

    // Search input - allow direct keyboard input
    const input = this.container.querySelector('.search-input');
    if (input) {
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          this._doSearch();
        }
      });

      // Sync query from input
      input.addEventListener('input', () => {
        this.query = input.value;
      });
    }

    // Listen for tab changes
    document.addEventListener('app:tabchange', (e) => {
      if (e.detail.tabName === 'search') {
        this._renderHistory();
        if (window.focusManager) {
          const first = this.container.querySelector('.search-input-wrap [data-focusable]') ||
            this.container.querySelector('[data-focusable]');
          if (first) window.focusManager.setFocus(first, 'keyboard');
        }
      }
    });
  }

  refresh() {
    this._renderKeyboard();
    this._renderHistory();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.searchPage = new SearchPage();
});
