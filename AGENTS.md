# Agents - TvBox 架构代理系统

## 项目概述

本项目（TvBox_WZ）是 TvBox 播放器架构的 Python 实现版本，用于学习和研究 TvBox 的核心设计思想。

### 参考项目

**TVBoxOS** - TvBox 官方 Android Java 实现，可作为源代码参考。

- **参考路径**: `C:\MyTools\TvBox\TVBoxOS`
- **语言**: Java (Android)
- **核心包**: `com.github.tvbox.osc` / `com.github.catvod.crawler`
- **爬虫引擎**: 支持 JS / Jar / Python 三种爬虫加载方式

---

## Agent 架构总览

TvBox 采用**插件化代理架构**，所有核心功能都通过标准化的 Agent 接口实现，上层代码无需关心底层细节。

```
┌─────────────────────────────────────────────────────────────┐
│                        上层 UI 层                             │
│                    (CLI / Web / Android)                     │
├───────────────┬───────────────┬───────────────┬─────────────┤
│  Spider Agent │  Parser Agent │  Player Agent │ Config Agent│
│  (数据获取)    │  (地址解析)    │  (视频播放)    │ (配置管理)   │
└───────────────┴───────────────┴───────────────┴─────────────┘
```

### 核心设计原则

1. **面向接口编程**: 所有 Agent 都有统一的基类接口
2. **开闭原则**: 新增 Agent 类型无需修改上层代码
3. **配置驱动**: 通过 JSON 配置动态创建 Agent 实例
4. **链式调用**: 支持 Agent 之间的协作（如解析器链式解析）

---

## 1. Spider Agent（爬虫代理）

Spider Agent 负责从各种数据源获取视频数据，是 TvBox 中最核心、最灵活的 Agent。

### 接口规范

基类: [base_spider.py](file:///c:/MyTools/TvBox_WZ/spiders/base_spider.py) - `BaseSpider`

| 方法 | 作用 |
|------|------|
| `init(site)` | 初始化爬虫，传入 SourceBean 配置 |
| `home_content(filter)` | 获取首页内容（分类 + 推荐） |
| `home_video_content()` | 仅获取首页推荐视频 |
| `category_content(tid, pg, filter, extend)` | 获取分类视频列表 |
| `detail_content(ids)` | 获取视频详情 |
| `search_content(key, quick, pg)` | 搜索视频 |
| `player_content(flag, id, vip_flags)` | 获取播放地址 |

### 已实现的 Spider Agent

| Agent 类 | 类型值 | 文件 | 说明 |
|----------|--------|------|------|
| `MockSpider` | - | [mock_spider.py](file:///c:/MyTools/TvBox_WZ/spiders/mock_spider.py) | 模拟数据，用于测试演示 |
| `JsonSpider` | 1 | [json_spider.py](file:///c:/MyTools/TvBox_WZ/spiders/json_spider.py) | JSON 接口爬虫（苹果CMS/海洋CMS格式） |

### 参考项目对应实现

TVBoxOS 中的 Spider 体系更加完整，位于 `com.github.catvod.crawler` 包：

| Java 类 | 路径 | 说明 |
|---------|------|------|
| `Spider` | [Spider.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/catvod/crawler/Spider.java) | Spider 基类，定义标准接口 |
| `SpiderApi` | [SpiderApi.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/catvod/crawler/SpiderApi.java) | Spider 管理器，统一调度 |
| `SpiderNull` | [SpiderNull.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/catvod/crawler/SpiderNull.java) | 空实现，占位用 |
| `SpiderDebug` | [SpiderDebug.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/catvod/crawler/SpiderDebug.java) | 调试模式 Spider |
| `JsLoader` | [JsLoader.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/catvod/crawler/JsLoader.java) | JS 爬虫加载器（QuickJS） |
| `JarLoader` | [JarLoader.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/catvod/crawler/JarLoader.java) | Jar 包爬虫加载器 |
| `IPyLoader` | [IPyLoader.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/catvod/crawler/python/IPyLoader.java) | Python 爬虫加载器接口 |

### Spider 类型对照表

| 类型值 | 名称 | TVBoxOS 支持 | 本项目支持 |
|--------|------|-------------|-----------|
| 0 | XML | ✅ | ❌ |
| 1 | JSON | ✅ | ✅ JsonSpider |
| 2 | 混合 | ✅ | ❌ |
| 3 | Spider (JS/Jar) | ✅ | ✅ MockSpider (模拟) |
| 4 | Remote | ✅ | ❌ |

---

## 2. Parser Agent（解析器代理）

Parser Agent 负责将各种格式的播放地址转换为播放器可直接播放的真实视频地址。

### 接口规范

基类: [base_parser.py](file:///c:/MyTools/TvBox_WZ/parsers/base_parser.py) - `BaseParser`

| 方法 | 作用 |
|------|------|
| `can_parse(url)` | 判断是否能解析该地址 |
| `parse(url)` | 解析播放地址，返回真实地址 |
| `priority` | 解析器优先级，数字越小优先级越高 |

### 已实现的 Parser Agent

| Agent 类 | 文件 | 说明 |
|----------|------|------|
| `DirectParser` | [direct_parser.py](file:///c:/MyTools/TvBox_WZ/parsers/direct_parser.py) | 直链解析器（直接返回视频地址） |
| `JsVariableParser` | [js_variable_parser.py](file:///c:/MyTools/TvBox_WZ/parsers/js_variable_parser.py) | JS 变量解析器（从 HTML 提取播放地址） |
| `WebSniffParser` | [web_sniff_parser.py](file:///c:/MyTools/TvBox_WZ/parsers/web_sniff_parser.py) | Web 嗅探解析器（type=0） |
| `JsonApiParser` | [json_api_parser.py](file:///c:/MyTools/TvBox_WZ/parsers/json_api_parser.py) | JSON 接口解析器（type=1） |
| `SpiderParseParser` | [spider_parse_parser.py](file:///c:/MyTools/TvBox_WZ/parsers/spider_parse_parser.py) | Spider 解析器（type=3） |

### 解析器管理器

[parser_manager.py](file:///c:/MyTools/TvBox_WZ/parsers/parser_manager.py) - `ParserManager`

- 自动选择合适的解析器
- 支持**链式解析**（一个地址经过多层解析）
- 根据优先级排序解析器

### Parses 系统（配置驱动的解析器）

参考 TvBox 的 `parses` 配置数组，实现了配置驱动的解析器加载机制。

数据模型: [parse_bean.py](file:///c:/MyTools/TvBox_WZ/models/parse_bean.py) - `ParseBean`

加载器: [parses_loader.py](file:///c:/MyTools/TvBox_WZ/utils/parses_loader.py) - `ParsesLoader`

#### flag 匹配机制

每个解析源通过 `ext.flag` 声明支持的平台关键词，视频播放线路有对应的 `flag`，通过 flag 匹配选择解析器。

```
视频 flag = "qq"
    ↓
查找 ext.flag 包含 "qq" 的解析源
    ↓
匹配成功 → 使用该解析器
```

#### Parses 类型对照表

| 类型值 | 名称 | 对应解析器 |
|--------|------|-----------|
| 0 | Web 嗅探 | WebSniffParser |
| 1 | JSON 接口 | JsonApiParser |
| 3 | Spider 解析 | SpiderParseParser |

### 参考项目对应实现

TVBoxOS 中解析相关代码:

| Java 类 | 路径 | 说明 |
|---------|------|------|
| `VideoParseRuler` | [VideoParseRuler.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/util/VideoParseRuler.java) | 视频解析规则 |
| `ParseBean` | [ParseBean.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/bean/ParseBean.java) | 解析源数据模型 |

---

## 3. Player Agent（播放器代理）

Player Agent 负责调用系统播放器播放视频。

### 接口规范

实现: [video_player.py](file:///c:/MyTools/TvBox_WZ/player/video_player.py) - `VideoPlayer`

| 方法 | 作用 |
|------|------|
| `detect_players()` | 检测系统可用的播放器 |
| `play(url, title)` | 播放视频 |
| `get_default_player()` | 获取默认播放器 |

### 支持的播放器

| 播放器 | 说明 | 推荐度 |
|--------|------|--------|
| VLC | 功能最全，支持格式最多 | ⭐⭐⭐⭐⭐ |
| mpv | 轻量高效，启动快 | ⭐⭐⭐⭐ |
| 系统默认 | 调用系统默认播放器 | ⭐⭐⭐ |

### 参考项目对应实现

TVBoxOS 播放器内核位于 `com.github.tvbox.osc.player` 包和独立的 `player` 模块：

| Java 类 | 路径 | 说明 |
|---------|------|------|
| `IjkMediaPlayer` | [IjkMediaPlayer.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/player/IjkMediaPlayer.java) | IJK 播放器（基于 FFmpeg） |
| `ExoPlayer` | [ExoPlayer.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/player/ExoPlayer.java) | Exo 播放器（Google 官方） |
| `MyVideoView` | [MyVideoView.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/player/MyVideoView.java) | 视频视图封装 |
| `ExoMediaPlayerFactory` | [ExoMediaPlayerFactory.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/player/ExoMediaPlayerFactory.java) | Exo 播放器工厂 |
| `LivePlayerManager` | [LivePlayerManager.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/bean/LivePlayerManager.java) | 直播播放器管理 |

#### 播放器类型对照表

| 类型值 | 名称 | 说明 |
|--------|------|------|
| 0 | 系统播放器 | Android 原生 MediaPlayer |
| 1 | IJK | IJKPlayer（基于 FFmpeg，功能最全） |
| 2 | EXO | ExoPlayer（Google 官方） |

---

## 4. Config Agent（配置代理）

Config Agent 负责加载和管理 TvBox 配置文件。

### 配置加载器

实现: [config_loader.py](file:///c:/MyTools/TvBox_WZ/utils/config_loader.py) - `ConfigLoader`

| 方法 | 作用 |
|------|------|
| `load(path_or_url)` | 从本地文件或 URL 加载配置 |
| `get_sites()` | 获取视频源列表 |
| `get_parses()` | 获取解析源列表 |
| `get_lives()` | 获取直播源列表 |

### 配置文件格式

标准 TvBox 配置文件结构（JSON）:

```json
{
  "spider": "./your.jar",
  "wallpaper": "./api/img",
  "sites": [
    {
      "key": "唯一标识",
      "name": "视频源名称",
      "type": 3,
      "api": "接口地址",
      "searchable": 1,
      "ext": ""
    }
  ],
  "parses": [
    {
      "name": "解析器名称",
      "type": 1,
      "url": "解析接口地址",
      "ext": { "flag": ["qq", "iqiyi"] }
    }
  ],
  "lives": [],
  "rules": [],
  "hosts": [],
  "doh": []
}
```

### 参考项目对应实现

| Java 类 | 路径 | 说明 |
|---------|------|------|
| `ApiConfig` | [ApiConfig.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/api/ApiConfig.java) | API 配置管理 |
| `DefaultConfig` | [DefaultConfig.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/util/DefaultConfig.java) | 默认配置 |
| `SourceBean` | [SourceBean.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/bean/SourceBean.java) | 视频源数据模型 |

---

## 5. 数据模型（Data Models）

所有 Agent 之间传递的数据都有标准模型。

### 核心数据模型

| 模型类 | 文件 | 对应 TVBoxOS | 说明 |
|--------|------|-------------|------|
| `SourceBean` | [source_bean.py](file:///c:/MyTools/TvBox_WZ/models/source_bean.py) | [SourceBean.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/bean/SourceBean.java) | 视频源配置 |
| `VodInfo` | [vod_info.py](file:///c:/MyTools/TvBox_WZ/models/vod_info.py) | [VodInfo.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/bean/VodInfo.java) | 视频详情 |
| `ParseBean` | [parse_bean.py](file:///c:/MyTools/TvBox_WZ/models/parse_bean.py) | [ParseBean.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/bean/ParseBean.java) | 解析源配置 |

### 其他 Bean（TVBoxOS 中）

| Bean 类 | 路径 | 说明 |
|---------|------|------|
| `AbsJson` | [AbsJson.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/bean/AbsJson.java) | JSON 数据抽象基类 |
| `Movie` | [Movie.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/bean/Movie.java) | 视频信息 |
| `MovieSort` | [MovieSort.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/bean/MovieSort.java) | 分类信息 |
| `LiveChannelItem` | [LiveChannelItem.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/bean/LiveChannelItem.java) | 直播频道 |

---

## 6. 辅助 Agent

### Mock API Server（模拟 API 服务器）

实现: [mock_api_server.py](file:///c:/MyTools/TvBox_WZ/server/mock_api_server.py) - `MockApiServer`

提供苹果CMS格式的本地模拟 API，用于开发和测试。

| 接口 | URL | 说明 |
|------|-----|------|
| 首页 | `/api.php?ac=list` | 分类 + 推荐 |
| 分类列表 | `/api.php?ac=detail&t=1&pg=1` | 分类视频列表 |
| 详情 | `/api.php?ac=detail&ids=1,2,3` | 视频详情 |
| 搜索 | `/api.php?ac=detail&wd=关键词` | 搜索视频 |
| 分享页 | `/share/{vid}` | 模拟视频分享页 |
| m3u8 | `/vod/{vid}.m3u8` | m3u8 播放列表 |

### 参考项目中的服务器

TVBoxOS 中有远程控制服务 `RemoteServer`，位于:
[RemoteServer.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/server/RemoteServer.java)

---

## 7. Agent 开发指南

### 新增 Spider Agent

1. 继承 `BaseSpider` 基类
2. 实现需要的方法（至少实现 `home_content`、`category_content`、`detail_content`）
3. 在工厂方法中注册新的 Spider 类型

示例模板:

```python
from spiders.base_spider import BaseSpider

class MySpider(BaseSpider):
    def init(self, site):
        self.api = site.api
        self.ext = site.ext

    def home_content(self, filter):
        return {"class": [], "list": []}

    def category_content(self, tid, pg, filter, extend):
        return {"page": 1, "pagecount": 1, "list": []}

    def detail_content(self, ids):
        return {"list": []}
```

### 新增 Parser Agent

1. 继承 `BaseParser` 基类
2. 实现 `can_parse` 和 `parse` 方法
3. 设置合适的 `priority`

示例模板:

```python
from parsers.base_parser import BaseParser

class MyParser(BaseParser):
    priority = 10

    def can_parse(self, url):
        return "example.com" in url

    def parse(self, url):
        # 解析逻辑
        return {"url": real_url, "parse": 0}
```

---

## 8. 测试 Agent

项目包含完整的测试套件，位于 [Tests/](file:///c:/MyTools/TvBox_WZ/Tests/) 目录。

| 测试文件 | 测试对象 |
|----------|---------|
| [test_models.py](file:///c:/MyTools/TvBox_WZ/Tests/test_models.py) | 数据模型 |
| [test_json_spider.py](file:///c:/MyTools/TvBox_WZ/Tests/test_json_spider.py) | JsonSpider |
| [test_mock_api.py](file:///c:/MyTools/TvBox_WZ/Tests/test_mock_api.py) | Mock API 服务器 |
| [test_parsers.py](file:///c:/MyTools/TvBox_WZ/Tests/test_parsers.py) | 解析器架构 |
| [test_js_parser.py](file:///c:/MyTools/TvBox_WZ/Tests/test_js_parser.py) | JS 变量解析器 |
| [test_player.py](file:///c:/MyTools/TvBox_WZ/Tests/test_player.py) | 播放器模块 |
| [test_parses_system.py](file:///c:/MyTools/TvBox_WZ/Tests/test_parses_system.py) | Parses 系统 |
| [test_integration.py](file:///c:/MyTools/TvBox_WZ/Tests/test_integration.py) | 端到端集成 |
| [test_full_flow.py](file:///c:/MyTools/TvBox_WZ/Tests/test_full_flow.py) | 完整播放流程 |
| [test_parses_integration.py](file:///c:/MyTools/TvBox_WZ/Tests/test_parses_integration.py) | Parses 集成 |

运行测试:

```bash
python Tests/test_xxx.py
```

---

## 9. 参考源码索引

### TVBoxOS 核心目录结构

```
C:\MyTools\TvBox\TVBoxOS\
├── app/
│   └── src/
│       └── main/
│           ├── java/com/github/
│           │   ├── catvod/crawler/     ← Spider 引擎核心
│           │   └── tvbox/osc/
│           │       ├── api/            ← API 配置
│           │       ├── bean/           ← 数据模型
│           │       ├── player/         ← 播放器
│           │       ├── server/         ← 远程控制服务
│           │       ├── util/           ← 工具类
│           │       └── viewmodel/      ← ViewModel
│           └── assets/js/lib/          ← JS 爬虫库
├── player/                             ← 独立播放器模块
│   └── src/main/java/xyz/doikki/videoplayer/
├── pyramid/                            ← Python 爬虫模块
│   └── src/main/python/
└── quickjs/                            ← QuickJS 引擎
    └── src/main/java/com/whl/quickjs/
```

### 关键学习路径

1. **入门**: `Spider.java` → `SpiderApi.java` → `SourceBean.java`
2. **进阶**: `JsLoader.java` → `JarLoader.java` → 各种 Spider 实现
3. **播放**: `IjkMediaPlayer.java` → `ExoPlayer.java` → `MyVideoView.java`
4. **解析**: `VideoParseRuler.java` → `ParseBean.java`
5. **配置**: `ApiConfig.java` → `DefaultConfig.java`

---

## 10. 架构演进路线

### 已完成 ✅

- [x] Spider 基类与接口规范
- [x] MockSpider 模拟爬虫
- [x] JsonSpider (type=1) JSON 接口爬虫
- [x] 播放地址解析器架构
- [x] DirectParser 直链解析
- [x] JsVariableParser JS 变量解析
- [x] Parses 解析器系统（type 0/1/3）
- [x] flag 匹配机制
- [x] 播放器模块（VLC/mpv）
- [x] 配置加载器
- [x] 命令行 UI

### 待实现 📋

- [ ] type=0 XML 接口爬虫
- [ ] type=3 真实 Spider 爬虫（HTML 解析）
- [ ] type=4 Remote 远程爬虫
- [ ] 直播源支持 (lives)
- [ ] 弹幕功能 (DanmakuApi)
- [ ] 字幕引擎
- [ ] 缓存机制 (CacheManager)
- [ ] 历史记录与收藏
- [ ] Web UI 界面
- [ ] 搜索聚合
