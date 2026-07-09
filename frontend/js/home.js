/**
 * HomePage - Home page logic
 * Source switching, category sub-tabs, mock video data, card click -> player detail
 */
class HomePage {
  constructor() {
    this.currentSource = 'jsm';
    this.currentCategory = '推荐';
    this.sources = [
      { id: 'jsm', name: '极光影视' },
      { id: 'fty', name: '饭太硬' },
      { id: 'R18', name: '18+' }
    ];
    this.categories = ['推荐', '电影', '电视剧', '综艺', '动漫', '纪录片'];
    this.videoData = [];
    this.dropdownOpen = false;
    this.container = null;

    this._init();
  }

  _init() {
    this.container = document.getElementById('home-page');
    if (!this.container) return;

    this._renderSourceBar();
    this._renderCategoryBar();
    this._loadVideoData();
    this._bindEvents();
  }

  _renderSourceBar() {
    const bar = this.container.querySelector('.source-bar');
    if (!bar) return;

    const selector = bar.querySelector('.source-selector');
    if (selector) {
      selector.innerHTML = `
        <span class="source-name">${this._getSourceName()}</span>
        <span class="source-arrow">&#9660;</span>
      `;
    }

    // Remove old dropdown
    const oldDropdown = bar.querySelector('.source-dropdown');
    if (oldDropdown) oldDropdown.remove();

    const dropdown = document.createElement('div');
    dropdown.className = 'source-dropdown hidden';
    dropdown.setAttribute('data-focus-zone', 'source-dropdown');

    this.sources.forEach(source => {
      const item = document.createElement('div');
      item.className = 'source-dropdown-item' + (source.id === this.currentSource ? ' active' : '');
      item.setAttribute('data-focusable', 'true');
      item.textContent = source.name;
      item.dataset.sourceId = source.id;
      item.addEventListener('click', (e) => {
        e.stopPropagation();
        this._switchSource(source.id);
      });
      dropdown.appendChild(item);
    });

    // Position the source selector as relative
    const selectorWrap = bar.querySelector('.source-selector-wrap');
    if (selectorWrap) {
      selectorWrap.style.position = 'relative';
      selectorWrap.appendChild(dropdown);
    }
  }

  _renderCategoryBar() {
    const categoryBar = this.container.querySelector('.category-bar .sub-tab-bar');
    if (!categoryBar) return;

    categoryBar.innerHTML = '';

    this.categories.forEach(cat => {
      const tab = document.createElement('div');
      tab.className = 'sub-tab-item' + (cat === this.currentCategory ? ' active' : '');
      tab.setAttribute('data-focusable', 'true');
      tab.textContent = cat;
      tab.addEventListener('click', () => {
        this._switchCategory(cat);
      });
      categoryBar.appendChild(tab);
    });
  }

  _loadVideoData() {
    this.videoData = this._generateMockData(this.currentCategory);
    this._renderVideoGrid();
  }

  _generateMockData(category) {
    const titles = [
      '流浪地球3', '三体', '满江红', '长津湖', '你好李焕英', '哪吒之魔童降世',
      '战狼2', '我和我的祖国', '中国机长', '攀登者', '金刚川', '八佰',
      '刺杀小说家', '唐人街探案3', '送你一朵小红花', '你好世界', '悬崖之上',
      '革命者', '铁道英雄', '狙击手', '独行月球', '外太空的莫扎特', '明日战记',
      '封神第一部', '消失的她', '孤注一掷', '八角笼中', '长安三万里', '热烈',
      '坚如磐石', '前任4', '志愿军', '无名', '检察风云', '人生路不熟',
      '超能一家人', '三大队', '年会不能停', '飞驰人生2', '第二十条',
      '热辣滚烫', '熊出没·逆转时空', '周处除三害', '功夫熊猫4', '沙丘2',
      '哥斯拉大战金刚2', '异形：夺命舰', '死侍与金刚狼', '头脑特工队2',
      '小丑2', '角斗士2', '海洋奇缘2', '疯狂动物城2'
    ];

    const directors = ['郭帆', '张艺谋', '陈凯歌', '贾玲', '饺子', '吴京', '宁浩', '徐克', '乌尔善', '韩寒'];
    const years = ['2024', '2023', '2022', '2021', '2020', '2024', '2023', '2024', '2023', '2024'];
    const regions = ['中国大陆', '中国香港', '美国', '韩国', '日本', '英国', '法国'];
    const updates = ['更新至24集', '更新至12集', '全24集', 'HD', 'TC', '全12集', '更新至36集', '蓝光', '4K'];
    const qualities = ['1080P', '4K', '720P', 'HD'];

    const items = [];
    const count = 50 + Math.floor(Math.random() * 10);

    for (let i = 0; i < count; i++) {
      items.push({
        id: i,
        title: titles[i % titles.length] + (i >= titles.length ? ` ${Math.floor(i / titles.length) + 1}` : ''),
        director: directors[i % directors.length],
        cast: '刘德华 / 梁朝伟 / 周迅',
        year: years[i % years.length],
        region: regions[i % regions.length],
        update: updates[i % updates.length],
        quality: qualities[i % qualities.length],
        description: '这是一部精彩的影视作品，讲述了一个关于勇气与智慧的故事。主演阵容强大，剧情跌宕起伏，值得一看。',
        category: category,
        thumb: `https://picsum.photos/seed/tv${i + 1}/300/450`
      });
    }

    return items;
  }

  _renderVideoGrid() {
    const grid = this.container.querySelector('.video-grid');
    if (!grid) return;

    grid.innerHTML = '';

    if (this.videoData.length === 0) {
      grid.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <div class="empty-icon">&#128249;</div>
          <div class="empty-text">暂无内容</div>
        </div>
      `;
      return;
    }

    this.videoData.forEach((video, index) => {
      const card = document.createElement('div');
      card.className = 'card-item';
      card.setAttribute('data-focusable', 'true');
      card.style.animationDelay = `${Math.min(index * 0.02, 0.26)}s`;

      card.innerHTML = `
        <div class="card-thumb">
          <img src="${video.thumb}" alt="${video.title}" loading="lazy" onerror="this.style.display='none'">
          <span class="card-quality">${video.quality}</span>
        </div>
        <div class="card-info">
          <div class="card-title">${video.title}</div>
          <div class="card-meta">${video.update}</div>
        </div>
      `;

      card.addEventListener('click', () => {
        this._openPlayer(video);
      });

      grid.appendChild(card);
    });
  }

  _openPlayer(videoData) {
    if (window.app) {
      window.app.showPlayer(videoData);
    }
  }

  _switchSource(sourceId) {
    if (sourceId === this.currentSource) {
      this._toggleDropdown(false);
      return;
    }

    this.currentSource = sourceId;
    this._toggleDropdown(false);
    this._renderSourceBar();
    this._loadVideoData();
  }

  _switchCategory(category) {
    if (category === this.currentCategory) return;

    this.currentCategory = category;
    this._renderCategoryBar();
    this._loadVideoData();
  }

  _toggleDropdown(open) {
    this.dropdownOpen = typeof open === 'boolean' ? open : !this.dropdownOpen;

    const dropdown = this.container.querySelector('.source-dropdown');
    const selector = this.container.querySelector('.source-selector');

    if (dropdown) {
      dropdown.classList.toggle('hidden', !this.dropdownOpen);
    }
    if (selector) {
      selector.classList.toggle('open', this.dropdownOpen);
    }
  }

  _bindEvents() {
    // Source selector click
    const selector = this.container.querySelector('.source-selector');
    if (selector) {
      selector.addEventListener('click', (e) => {
        e.stopPropagation();
        this._toggleDropdown();
      });
    }

    // Close dropdown on outside click
    document.addEventListener('click', (e) => {
      if (this.dropdownOpen && !e.target.closest('.source-selector-wrap')) {
        this._toggleDropdown(false);
      }
    });

    // Listen for tab changes
    document.addEventListener('app:tabchange', (e) => {
      if (e.detail.tabName === 'home') {
        this.refresh();
      }
    });
  }

  _getSourceName() {
    const source = this.sources.find(s => s.id === this.currentSource);
    return source ? source.name : '未知来源';
  }

  refresh() {
    this._renderSourceBar();
    this._renderCategoryBar();
    this._loadVideoData();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.homePage = new HomePage();
});
