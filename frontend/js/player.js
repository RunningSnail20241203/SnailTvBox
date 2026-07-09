/**
 * PlayerPage - Player detail overlay logic
 * Mock player controls, route tab switching, episode grid, fullscreen, back button
 */
class PlayerPage {
  constructor() {
    this.videoData = null;
    this.currentRoute = 0;
    this.currentEpisode = 0;
    this.isPlaying = false;
    this.isMuted = false;
    this.progress = 35;
    this.container = null;
    this.routes = [];

    this._init();
  }

  _init() {
    this.container = document.getElementById('player-overlay');
    if (!this.container) return;

    this._bindEvents();
  }

  _bindEvents() {
    // Back button
    const backBtn = this.container.querySelector('.player-back-btn');
    if (backBtn) {
      backBtn.addEventListener('click', () => {
        if (window.app) window.app.closePlayer();
      });
    }

    // Play/pause
    const playBtn = this.container.querySelector('.control-btn.play-pause');
    if (playBtn) {
      playBtn.addEventListener('click', () => this._togglePlay());
    }

    // Mute
    const muteBtn = this.container.querySelector('.control-btn.mute-btn');
    if (muteBtn) {
      muteBtn.addEventListener('click', () => this._toggleMute());
    }

    // Fullscreen button in info panel
    const fullscreenBtn = this.container.querySelector('.info-fullscreen-btn');
    if (fullscreenBtn) {
      fullscreenBtn.addEventListener('click', () => this._toggleFullscreen());
    }

    // Progress bar click
    const progressBar = this.container.querySelector('.progress-bar');
    if (progressBar) {
      progressBar.addEventListener('click', (e) => {
        const rect = progressBar.getBoundingClientRect();
        const ratio = (e.clientX - rect.left) / rect.width;
        this.progress = Math.max(0, Math.min(100, ratio * 100));
        this._updateProgress();
      });
    }
  }

  open(videoData) {
    this.videoData = videoData;
    this.currentRoute = 0;
    this.currentEpisode = 0;
    this.isPlaying = false;
    this.progress = 0;

    this.routes = this._generateMockRoutes();

    this._renderHeader();
    this._renderInfo();
    this._renderRoutes();
    this._renderEpisodes();
    this._updatePlayState();

    // Set first focusable
    setTimeout(() => {
      if (window.focusManager) {
        const firstFocusable = this.container.querySelector('[data-focusable]');
        if (firstFocusable) window.focusManager.setFocus(firstFocusable, 'keyboard');
      }
    }, 100);
  }

  _generateMockRoutes() {
    return [
      { name: '线路一', episodes: this._generateEpisodes(24) },
      { name: '线路二', episodes: this._generateEpisodes(40) },
      { name: '线路三', episodes: this._generateEpisodes(12) }
    ];
  }

  _generateEpisodes(count) {
    const episodes = [];
    for (let i = 1; i <= count; i++) {
      episodes.push({
        index: i,
        url: `https://mock-stream.example.com/ep${i}.m3u8`,
        title: `第${i}集`
      });
    }
    return episodes;
  }

  _renderHeader() {
    const headerTitle = this.container.querySelector('.player-header-title');
    if (headerTitle && this.videoData) {
      headerTitle.textContent = this.videoData.title;
    }
  }

  _renderInfo() {
    const panel = this.container.querySelector('.player-info-panel');
    if (!panel || !this.videoData) return;

    const v = this.videoData;

    panel.innerHTML = `
      <div class="info-section">
        <div class="info-title">${v.title}</div>
      </div>
      <div class="info-section">
        <div class="info-section-title">详细信息</div>
        <div class="info-meta-grid">
          <span class="info-meta-label">导演</span>
          <span class="info-meta-value">${v.director || '未知'}</span>
          <span class="info-meta-label">主演</span>
          <span class="info-meta-value">${v.cast || '未知'}</span>
          <span class="info-meta-label">年份</span>
          <span class="info-meta-value">${v.year || '未知'}</span>
          <span class="info-meta-label">地区</span>
          <span class="info-meta-value">${v.region || '未知'}</span>
          <span class="info-meta-label">更新</span>
          <span class="info-meta-value">${v.update || '未知'}</span>
        </div>
      </div>
      <div class="info-section">
        <div class="info-section-title">简介</div>
        <div class="info-description">${v.description || '暂无简介'}</div>
      </div>
      <div class="info-section">
        <button class="info-fullscreen-btn btn" data-focusable="true">
          <span>&#9974;</span>
          <span>全屏播放</span>
        </button>
      </div>
    `;

    // Re-bind fullscreen button
    const fullscreenBtn = panel.querySelector('.info-fullscreen-btn');
    if (fullscreenBtn) {
      fullscreenBtn.addEventListener('click', () => this._toggleFullscreen());
    }
  }

  _renderRoutes() {
    const routeBar = this.container.querySelector('.route-tab-bar');
    if (!routeBar) return;

    routeBar.innerHTML = '';

    this.routes.forEach((route, index) => {
      const tab = document.createElement('div');
      tab.className = 'route-tab-item' + (index === this.currentRoute ? ' active' : '');
      tab.setAttribute('data-focusable', 'true');
      tab.textContent = route.name;
      tab.addEventListener('click', () => {
        this._switchRoute(index);
      });
      routeBar.appendChild(tab);
    });
  }

  _renderEpisodes() {
    const grid = this.container.querySelector('.episode-grid');
    if (!grid) return;

    grid.innerHTML = '';

    const route = this.routes[this.currentRoute];
    if (!route) return;

    route.episodes.forEach((ep) => {
      const item = document.createElement('div');
      item.className = 'episode-item' + (ep.index === this.currentEpisode + 1 ? ' active' : '');
      item.setAttribute('data-focusable', 'true');
      item.textContent = ep.title;
      item.addEventListener('click', () => {
        this._playEpisode(ep.index);
      });
      grid.appendChild(item);
    });
  }

  _switchRoute(index) {
    if (index === this.currentRoute) return;
    this.currentRoute = index;
    this.currentEpisode = 0;
    this._renderRoutes();
    this._renderEpisodes();
    this._updatePlayState();
  }

  _playEpisode(episodeNum) {
    this.currentEpisode = episodeNum - 1;
    this.progress = 0;
    this.isPlaying = true;
    this._renderEpisodes();
    this._updatePlayState();
  }

  _togglePlay() {
    this.isPlaying = !this.isPlaying;
    this._updatePlayState();
  }

  _toggleMute() {
    this.isMuted = !this.isMuted;
    const muteBtn = this.container.querySelector('.control-btn.mute-btn');
    if (muteBtn) {
      muteBtn.innerHTML = this.isMuted ? '&#128263;' : '&#128266;';
    }
  }

  _updatePlayState() {
    const playBtn = this.container.querySelector('.control-btn.play-pause');
    if (playBtn) {
      playBtn.innerHTML = this.isPlaying ? '&#9646;&#9646;' : '&#9654;';
    }

    const placeholder = this.container.querySelector('.player-placeholder');
    if (placeholder) {
      placeholder.innerHTML = this.isPlaying
        ? `<div class="play-icon">&#9646;&#9646;</div><div>播放中...</div>`
        : `<div class="play-icon">&#9654;</div><div>点击播放</div>`;
    }
  }

  _updateProgress() {
    const fill = this.container.querySelector('.progress-fill');
    if (fill) {
      fill.style.width = this.progress + '%';
    }

    const timeDisplay = this.container.querySelector('.time-display');
    if (timeDisplay) {
      const currentSec = Math.floor(this.progress * 4.2);
      const totalSec = 420;
      const cm = String(Math.floor(currentSec / 60)).padStart(2, '0');
      const cs = String(currentSec % 60).padStart(2, '0');
      const tm = String(Math.floor(totalSec / 60)).padStart(2, '0');
      const ts = String(totalSec % 60).padStart(2, '0');
      timeDisplay.textContent = `${cm}:${cs} / ${tm}:${ts}`;
    }
  }

  _toggleFullscreen() {
    const screen = this.container.querySelector('.player-screen');
    if (!screen) return;

    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      screen.requestFullscreen().catch(() => {
        // Fallback: toggle CSS fullscreen
        if (screen.requestFullscreen) {
          screen.requestFullscreen();
        }
      });
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.playerPage = new PlayerPage();
});
