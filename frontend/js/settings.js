/**
 * SettingsPage - Settings page logic
 * Source CRUD, playback settings, UI settings, about
 */
class SettingsPage {
  constructor() {
    this.currentSection = 'source';
    this.container = null;
    this.sources = [
      { id: 'src_1', name: '极光影视', url: 'https://api.jiguang.tv/api', active: true },
      { id: 'src_2', name: '饭太硬', url: 'https://fantaiying.com/api', active: false },
      { id: 'src_3', name: '18+资源', url: 'https://adult-source.com/api', active: false }
    ];
    this.settings = {
      defaultPlayer: 'internal',
      quality: '1080p',
      hardwareDecode: true,
      autoPlay: true,
      theme: 'dark',
      language: 'zh-CN',
      fontSize: 'medium'
    };

    this._init();
  }

  _init() {
    this.container = document.getElementById('settings-page');
    if (!this.container) return;

    this._renderMenu();
    this._renderSection();
    this._bindEvents();
  }

  _renderMenu() {
    const menu = this.container.querySelector('.settings-menu');
    if (!menu) return;

    const menuItems = [
      { id: 'source', icon: '&#128250;', label: '源管理', badge: this.sources.length },
      { id: 'playback', icon: '&#9654;', label: '播放设置' },
      { id: 'ui', icon: '&#127912;', label: '界面设置' },
      { id: 'about', icon: '&#8505;', label: '关于' }
    ];

    // Keep title, clear rest
    const title = menu.querySelector('.settings-menu-title');
    menu.innerHTML = '';
    if (title) menu.appendChild(title);

    menuItems.forEach(item => {
      const el = document.createElement('div');
      el.className = 'menu-item' + (item.id === this.currentSection ? ' active' : '');
      el.setAttribute('data-focusable', 'true');
      el.dataset.section = item.id;

      let badgeHtml = item.badge ? `<span class="menu-badge">${item.badge}</span>` : '';

      el.innerHTML = `
        <span class="menu-icon">${item.icon}</span>
        <span class="menu-label">${item.label}</span>
        ${badgeHtml}
      `;

      el.addEventListener('click', () => {
        this._switchSection(item.id);
      });

      menu.appendChild(el);
    });
  }

  _switchSection(sectionId) {
    this.currentSection = sectionId;
    this._renderMenu();
    this._renderSection();
  }

  _renderSection() {
    const detail = this.container.querySelector('.settings-detail');
    if (!detail) return;

    // Hide all sections
    const sections = detail.querySelectorAll('.settings-section');
    sections.forEach(s => s.classList.remove('active'));

    switch (this.currentSection) {
      case 'source':
        this._renderSourceSection(detail);
        break;
      case 'playback':
        this._renderPlaybackSection(detail);
        break;
      case 'ui':
        this._renderUISection(detail);
        break;
      case 'about':
        this._renderAboutSection(detail);
        break;
    }
  }

  _renderSourceSection(detail) {
    let section = detail.querySelector('#section-source');
    if (!section) {
      section = document.createElement('div');
      section.className = 'settings-section';
      section.id = 'section-source';
      detail.appendChild(section);
    }

    section.innerHTML = `
      <div class="section-header">
        <div class="section-title">源管理</div>
        <div class="section-desc">管理视频数据源，添加、编辑或删除数据源配置</div>
      </div>
      <div class="form-group">
        <div class="form-group-title">数据源列表</div>
        <div id="source-list"></div>
        <div class="add-source-btn btn" data-focusable="true" id="add-source-btn">
          <span>+ 添加数据源</span>
        </div>
      </div>
    `;

    this._renderSourceList();
    this._bindSourceEvents();
  }

  _renderSourceList() {
    const list = this.container.querySelector('#source-list');
    if (!list) return;

    list.innerHTML = '';

    this.sources.forEach(source => {
      const item = document.createElement('div');
      item.className = 'source-list-item';

      item.innerHTML = `
        <div class="source-name">${source.name}${source.active ? ' <span style="color:var(--accent-primary);font-size:var(--font-size-xs);">●</span>' : ''}</div>
        <div class="source-url">${source.url}</div>
        <div class="source-actions">
          <button class="source-action-btn btn" data-focusable="true" data-action="edit" data-id="${source.id}" title="编辑">&#9998;</button>
          <button class="source-action-btn btn danger" data-focusable="true" data-action="delete" data-id="${source.id}" title="删除">&#128465;</button>
        </div>
      `;

      list.appendChild(item);
    });
  }

  _bindSourceEvents() {
    const addBtn = this.container.querySelector('#add-source-btn');
    if (addBtn) {
      addBtn.addEventListener('click', () => {
        this._addSource();
      });
    }

    // Edit / Delete buttons
    const actionBtns = this.container.querySelectorAll('.source-action-btn');
    actionBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const action = btn.dataset.action;
        const id = btn.dataset.id;
        if (action === 'delete') {
          this._deleteSource(id);
        } else if (action === 'edit') {
          this._editSource(id);
        }
      });
    });
  }

  _addSource() {
    const newSource = {
      id: 'src_' + Date.now(),
      name: '新数据源',
      url: 'https://example.com/api',
      active: false
    };
    this.sources.push(newSource);
    this._renderMenu();
    this._renderSourceSection(this.container.querySelector('.settings-detail'));
  }

  _deleteSource(id) {
    this.sources = this.sources.filter(s => s.id !== id);
    this._renderMenu();
    this._renderSourceSection(this.container.querySelector('.settings-detail'));
  }

  _editSource(id) {
    const source = this.sources.find(s => s.id === id);
    if (!source) return;

    // Simple inline edit via prompt replacement - toggle active
    this.sources.forEach(s => s.active = false);
    source.active = true;
    this._renderMenu();
    this._renderSourceSection(this.container.querySelector('.settings-detail'));
  }

  _renderPlaybackSection(detail) {
    let section = detail.querySelector('#section-playback');
    if (!section) {
      section = document.createElement('div');
      section.className = 'settings-section';
      section.id = 'section-playback';
      detail.appendChild(section);
    }

    section.innerHTML = `
      <div class="section-header">
        <div class="section-title">播放设置</div>
        <div class="section-desc">配置默认播放器、画质、解码等播放相关选项</div>
      </div>
      <div class="form-group">
        <div class="form-group-title">播放器</div>
        <div class="form-row">
          <div>
            <div class="form-label">默认播放器</div>
          </div>
          <select class="form-select" data-setting="defaultPlayer">
            <option value="internal" ${this.settings.defaultPlayer === 'internal' ? 'selected' : ''}>内置播放器</option>
            <option value="external" ${this.settings.defaultPlayer === 'external' ? 'selected' : ''}>外部播放器</option>
            <option value="vlc" ${this.settings.defaultPlayer === 'vlc' ? 'selected' : ''}>VLC播放器</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <div class="form-group-title">画质</div>
        <div class="form-row">
          <div>
            <div class="form-label">默认画质</div>
          </div>
          <select class="form-select" data-setting="quality">
            <option value="4k" ${this.settings.quality === '4k' ? 'selected' : ''}>4K</option>
            <option value="1080p" ${this.settings.quality === '1080p' ? 'selected' : ''}>1080P</option>
            <option value="720p" ${this.settings.quality === '720p' ? 'selected' : ''}>720P</option>
            <option value="480p" ${this.settings.quality === '480p' ? 'selected' : ''}>480P</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <div class="form-group-title">解码</div>
        <div class="form-row">
          <div>
            <div class="form-label">硬件解码</div>
            <div class="form-label-desc">使用GPU加速视频解码</div>
          </div>
          <label class="toggle">
            <input type="checkbox" data-setting="hardwareDecode" ${this.settings.hardwareDecode ? 'checked' : ''}>
            <span class="toggle-slider"></span>
          </label>
        </div>
        <div class="form-row">
          <div>
            <div class="form-label">自动播放</div>
            <div class="form-label-desc">进入详情页自动播放视频</div>
          </div>
          <label class="toggle">
            <input type="checkbox" data-setting="autoPlay" ${this.settings.autoPlay ? 'checked' : ''}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
    `;

    this._bindSettingEvents(section);
  }

  _renderUISection(detail) {
    let section = detail.querySelector('#section-ui');
    if (!section) {
      section = document.createElement('div');
      section.className = 'settings-section';
      section.id = 'section-ui';
      detail.appendChild(section);
    }

    section.innerHTML = `
      <div class="section-header">
        <div class="section-title">界面设置</div>
        <div class="section-desc">调整主题、语言、字体大小等界面显示选项</div>
      </div>
      <div class="form-group">
        <div class="form-group-title">主题</div>
        <div class="form-row">
          <div>
            <div class="form-label">应用主题</div>
          </div>
          <select class="form-select" data-setting="theme">
            <option value="dark" ${this.settings.theme === 'dark' ? 'selected' : ''}>深色模式</option>
            <option value="light" ${this.settings.theme === 'light' ? 'selected' : ''}>浅色模式</option>
            <option value="auto" ${this.settings.theme === 'auto' ? 'selected' : ''}>跟随系统</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <div class="form-group-title">语言</div>
        <div class="form-row">
          <div>
            <div class="form-label">显示语言</div>
          </div>
          <select class="form-select" data-setting="language">
            <option value="zh-CN" ${this.settings.language === 'zh-CN' ? 'selected' : ''}>简体中文</option>
            <option value="zh-TW" ${this.settings.language === 'zh-TW' ? 'selected' : ''}>繁体中文</option>
            <option value="en" ${this.settings.language === 'en' ? 'selected' : ''}>English</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <div class="form-group-title">字体</div>
        <div class="form-row">
          <div>
            <div class="form-label">字体大小</div>
          </div>
          <select class="form-select" data-setting="fontSize">
            <option value="small" ${this.settings.fontSize === 'small' ? 'selected' : ''}>小</option>
            <option value="medium" ${this.settings.fontSize === 'medium' ? 'selected' : ''}>中</option>
            <option value="large" ${this.settings.fontSize === 'large' ? 'selected' : ''}>大</option>
            <option value="xlarge" ${this.settings.fontSize === 'xlarge' ? 'selected' : ''}>特大</option>
          </select>
        </div>
      </div>
    `;

    this._bindSettingEvents(section);
  }

  _renderAboutSection(detail) {
    let section = detail.querySelector('#section-about');
    if (!section) {
      section = document.createElement('div');
      section.className = 'settings-section';
      section.id = 'section-about';
      detail.appendChild(section);
    }

    section.innerHTML = `
      <div class="section-header">
        <div class="section-title">关于</div>
        <div class="section-desc">应用版本及设备信息</div>
      </div>
      <div class="about-info">
        <div class="about-item">
          <span class="about-label">应用名称</span>
          <span class="about-value">TVBox</span>
        </div>
        <div class="about-item">
          <span class="about-label">版本号</span>
          <span class="about-value">v1.0.0</span>
        </div>
        <div class="about-item">
          <span class="about-label">构建日期</span>
          <span class="about-value">2026-07-09</span>
        </div>
        <div class="about-item">
          <span class="about-label">运行环境</span>
          <span class="about-value">Windows / Chromium</span>
        </div>
        <div class="about-item">
          <span class="about-label">设备分辨率</span>
          <span class="about-value">${window.innerWidth} x ${window.innerHeight}</span>
        </div>
        <div class="about-item">
          <span class="about-label">用户代理</span>
          <span class="about-value" style="font-size:var(--font-size-xs);max-width:300px;text-align:right;word-break:break-all;">${navigator.userAgent.slice(0, 80)}...</span>
        </div>
      </div>
    `;
  }

  _bindSettingEvents(section) {
    const selects = section.querySelectorAll('.form-select[data-setting]');
    selects.forEach(select => {
      select.addEventListener('change', () => {
        const key = select.dataset.setting;
        this.settings[key] = select.value;
      });
    });

    const toggles = section.querySelectorAll('input[type="checkbox"][data-setting]');
    toggles.forEach(toggle => {
      toggle.addEventListener('change', () => {
        const key = toggle.dataset.setting;
        this.settings[key] = toggle.checked;
      });
    });
  }

  _bindEvents() {
    // Menu items are already bound in _renderMenu

    // Listen for tab changes
    document.addEventListener('app:tabchange', (e) => {
      if (e.detail.tabName === 'settings') {
        this._renderMenu();
        this._renderSection();
        if (window.focusManager) {
          const first = this.container.querySelector('.menu-item[data-focusable]');
          if (first) window.focusManager.setFocus(first, 'keyboard');
        }
      }
    });
  }

  refresh() {
    this._renderMenu();
    this._renderSection();
  }

  getSettings() {
    return { ...this.settings };
  }

  getSources() {
    return [...this.sources];
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.settingsPage = new SettingsPage();
});
