# TvBox Learn - TvBox 架构学习项目

## 项目简介

这是一个用于学习 TvBox 播放器架构的 Python 教学项目。通过从零开始实现 TvBox 的核心概念，帮助你理解其工作原理。

### 学习目标

- 理解 TvBox 的整体架构和数据流转
- 掌握视频源配置文件的格式和作用
- 理解 Spider 爬虫接口的设计思想
- 能够编写自定义的 Spider 爬虫源
- 熟悉 TvBox 的数据模型和返回格式
- 掌握播放地址解析器的插件化设计
- 学会调用系统播放器播放视频

### 本项目特点

- **完全独立实现**：不依赖 TvBox 项目的任何代码
- **纯 Python 实现**：使用 Python 3 开发，易于理解和扩展
- **命令行界面**：通过 CLI 交互体验完整的使用流程
- **模拟数据**：内置 MockSpider，无需真实数据源即可体验全部功能
- **详细注释**：代码中包含大量解释性注释，说明设计思路

---

## 项目结构

```
Learn/
├── main.py                  # 项目入口文件，启动命令行界面
├── demo_play.py             # 播放流程演示脚本
├── demo_parses.py           # Parses 解析器系统演示
├── Tests/                   # 测试用例目录
│   ├── test_models.py       # 数据模型单元测试
│   ├── test_mock_api.py     # 模拟API服务器测试
│   ├── test_json_spider.py  # JsonSpider 单元测试
│   ├── test_integration.py  # 端到端集成测试
│   ├── test_parsers.py      # 解析器架构测试
│   ├── test_js_parser.py    # JS变量解析器测试
│   ├── test_player.py       # 播放器模块测试
│   ├── test_full_flow.py    # 完整播放流程测试
│   ├── test_parses_system.py # Parses 系统测试
│   └── test_parses_integration.py # Parses 端到端集成测试
├── fty.json                 # TvBox 配置文件（48个视频源）
├── requirements.txt         # Python 依赖
├── README.md                # 项目说明文档
├── models/                  # 数据模型模块
│   ├── __init__.py
│   ├── source_bean.py       # 视频源数据模型（SourceBean）
│   ├── vod_info.py          # 视频信息数据模型（VodInfo）
│   └── parse_bean.py        # 解析源数据模型（ParseBean）
├── spiders/                 # 爬虫模块
│   ├── __init__.py
│   ├── base_spider.py       # Spider 基类，定义标准接口
│   ├── mock_spider.py       # 模拟数据源，用于测试和演示
│   └── json_spider.py       # JSON接口爬虫（type=1，苹果CMS格式）
├── parsers/                 # 播放地址解析器模块
│   ├── __init__.py
│   ├── base_parser.py       # 解析器基类，定义标准接口
│   ├── direct_parser.py     # 直链解析器（直接返回视频地址）
│   ├── js_variable_parser.py # JS变量解析器（从HTML提取播放地址）
│   ├── parser_manager.py    # 解析器管理器（自动选择+链式解析）
│   ├── web_sniff_parser.py  # Web嗅探解析器（type=0）
│   ├── json_api_parser.py   # JSON接口解析器（type=1）
│   └── spider_parse_parser.py # Spider解析器（type=3）
├── player/                  # 播放器模块
│   ├── __init__.py
│   └── video_player.py      # 视频播放器（调用VLC/mpv等系统播放器）
├── server/                  # 服务器模块
│   ├── __init__.py
│   └── mock_api_server.py   # 本地模拟API服务器（苹果CMS格式）
├── utils/                   # 工具类模块
│   ├── __init__.py
│   ├── config_loader.py     # 配置加载器，解析 TvBox 配置
│   └── parses_loader.py     # Parses 解析器加载器
└── ui/                      # 用户界面模块
    ├── __init__.py
    └── cli_app.py           # 命令行交互界面
```

### 各文件作用说明

| 文件 | 作用 |
|------|------|
| `main.py` | 程序入口，解析命令行参数，启动 CliApp |
| `Tests/test_models.py` | 数据模型单元测试，验证 SourceBean 和 VodInfo 的功能 |
| `Tests/test_mock_api.py` | 模拟API服务器测试，验证各接口返回格式是否正确 |
| `Tests/test_json_spider.py` | JsonSpider 单元测试，验证 JSON 接口爬虫各功能 |
| `Tests/test_integration.py` | 端到端集成测试，验证爬虫与界面的完整交互 |
| `Tests/test_parses_system.py` | Parses 系统测试，验证解析器基类、各类型解析器及 flag 匹配 |
| `Tests/test_parses_integration.py` | Parses 端到端集成测试，验证 ParsesLoader 加载与解析完整流程 |
| `demo_parses.py` | Parses 解析器系统演示脚本，展示三种解析器的使用 |
| `source_bean.py` | 定义视频源的数据结构，对应配置文件中的 sites 数组元素 |
| `vod_info.py` | 定义视频详情的数据结构，包含播放线路解析功能 |
| `parse_bean.py` | 定义解析源的数据结构，对应配置文件中的 parses 数组元素 |
| `base_spider.py` | Spider 接口规范，定义了所有爬虫需要实现的方法 |
| `mock_spider.py` | 模拟爬虫实现，生成测试数据，用于演示和开发 |
| `json_spider.py` | JSON接口爬虫（type=1），对接苹果CMS、海洋CMS等标准接口 |
| `mock_api_server.py` | 本地模拟API服务器，提供苹果CMS格式的测试接口 |
| `web_sniff_parser.py` | Web嗅探解析器（type=0），通过网页嗅探获取真实播放地址 |
| `json_api_parser.py` | JSON接口解析器（type=1），调用远程 JSON 解析接口获取播放地址 |
| `spider_parse_parser.py` | Spider解析器（type=3），通过爬虫代码执行获取播放地址 |
| `parses_loader.py` | Parses 解析器加载器，自动将配置中的 parses 数组加载为解析器实例 |
| `config_loader.py` | 配置文件加载器，支持从本地文件或 URL 加载配置 |
| `cli_app.py` | 命令行应用，使用栈结构管理页面导航 |

---

## 快速开始

### 环境要求

- Python 3.6 及以上版本
- 操作系统：Windows / macOS / Linux

### 安装依赖

JSON 接口爬虫功能需要 `requests` 库来发送 HTTP 请求：

```bash
pip install -r requirements.txt
```

> 💡 MockSpider 和模拟服务器使用 Python 标准库，无需额外依赖。
> 但要体验真实的 JSON 接口爬虫，必须安装 requests。

### 运行项目

```bash
# 使用默认配置文件（fty.json）
python main.py

# 指定配置文件路径
python main.py /path/to/config.json

# 指定配置 URL
python main.py https://example.com/config.json
```

> 💡 **提示：** 运行后，视频源列表的**第1个源**（"🆕本地测试API站"）就是真实的 JSON 接口源。
> 需要先启动本地模拟 API 服务器才能使用，具体见"第二阶段"章节。

### 运行测试

本项目包含多组测试，从不同层面验证功能：

```bash
# 1. 数据模型测试（验证 SourceBean 和 VodInfo）
python Tests/test_models.py

# 2. 模拟 API 服务器测试（验证本地服务器接口）
python Tests/test_mock_api.py

# 3. JsonSpider 单元测试（验证 JSON 接口爬虫）
python Tests/test_json_spider.py

# 4. 端到端集成测试（验证完整流程）
python Tests/test_integration.py
```

**建议按顺序运行，逐步验证各个模块的功能。**

---

## 功能说明

### 四个页面

项目实现了四个核心页面，完整模拟了 TvBox 的使用流程：

#### 1. 视频源列表页（首页）

- 显示所有可用的视频源（共 48 个）
- 每个视频源显示编号、名称、类型（xml/json/spider）
- 选择视频源后进入该源的首页

#### 2. 视频源首页

- 显示该视频源的分类列表（5个分类）
- 显示首页推荐视频（6个）
- 可以选择分类进入分类列表，或选择推荐视频进入详情页

#### 3. 分类视频列表页

- 显示当前分类下的视频列表
- 支持分页浏览（每页 6 个，共 2 页）
- 选择视频进入详情页

#### 4. 视频详情页

- 显示视频的完整信息：名称、年份、地区、导演、主演、简介
- 显示所有播放线路（2-3条线路）
- 选择线路后显示该线路的所有剧集列表

### 导航方式

使用**栈结构**管理页面导航，类似于手机 App 的页面跳转：

- 进入新页面 → 压入栈
- 返回上一页 → 弹出栈
- 退出程序 → 清空栈

---

## 第二阶段：JSON接口爬虫（type=1）

经过第一阶段的学习，我们已经理解了 TvBox 的整体架构和 Spider 接口规范。第二阶段我们来学习最常见的数据源类型——**JSON 接口源（type=1）**。

### 什么是 type=1 JSON 接口

type=1 是 TvBox 中最常用的视频源类型之一，它对接的是**苹果CMS、海洋CMS**等建站系统的标准 API 接口。这些 CMS 系统提供了一套统一的 JSON 格式接口，TvBox 只需通过 HTTP 请求就能获取视频数据。

**常见的 CMS 系统：**
- **苹果CMS**：最流行的影视 CMS 系统，接口格式被广泛采用
- **海洋CMS**：另一种常见的影视 CMS，接口格式与苹果CMS类似
- **其他变种**：很多站点基于这些 CMS 二次开发，接口格式基本兼容

### 工作原理

JSON 接口爬虫的工作原理非常简单直接：

```
┌─────────────┐   HTTP请求    ┌─────────────┐
│  JsonSpider │ ────────────▶ │  API 服务器  │
│  (TvBox)    │ ◀──────────── │  (苹果CMS)   │
└─────────────┘   JSON数据    └─────────────┘
        │
        ▼
  解析JSON → 转换为TvBox标准格式 → 展示给用户
```

**核心流程：**
1. 构造请求 URL（带上必要的参数）
2. 发送 HTTP GET 请求
3. 接收 JSON 格式的响应数据
4. 解析并转换为 TvBox 内部标准格式
5. 返回给上层调用

### JsonSpider 的实现要点

`spiders/json_spider.py` 中的 `JsonSpider` 类实现了完整的 type=1 爬虫功能，有以下几个值得学习的实现要点：

#### 1. 使用 requests 库发送 HTTP 请求

```python
import requests

# 创建 Session，复用连接
self.session = requests.Session()
# 设置浏览器 User-Agent，避免被反爬虫拦截
self.session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."
})
# 设置超时时间，防止请求挂起
self.timeout = 10
```

**为什么用 Session？**
- 复用 TCP 连接，提高请求速度
- 自动管理 Cookie，保持会话状态
- 统一配置请求头，代码更简洁

#### 2. JSON / JSONP 兼容解析

很多站点为了支持跨域请求，会返回 JSONP 格式（`callback({...})`）。`JsonSpider` 做了兼容处理：

```python
def _parse_json(self, text):
    # 1. 先尝试直接解析 JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 2. 尝试匹配 JSONP 格式，提取花括号部分
    match = re.search(r'\w*\((\{.*\})\)\w*$', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    return None
```

#### 3. 自动编码识别

不同站点可能使用不同的字符编码（UTF-8、GBK 等），如果编码不对会导致中文乱码。

```python
# 让 requests 自动检测响应编码
resp.encoding = resp.apparent_encoding
```

`resp.apparent_encoding` 会根据响应内容自动猜测编码，比简单使用 `resp.encoding` 更可靠。

#### 4. 完善的错误处理

网络请求随时可能失败，好的爬虫必须有完善的错误处理：

| 错误类型 | 处理方式 |
|----------|----------|
| 请求超时 | 捕获 `Timeout` 异常，打印日志，返回空结构 |
| 连接失败 | 捕获 `ConnectionError` 异常，打印日志 |
| 其他异常 | 捕获通用 `Exception`，避免程序崩溃 |
| JSON 解析失败 | 返回 None，上层继续处理 |

**设计原则：** 即使接口失败，也要返回正确格式的空结构，不能让上层代码崩溃。

### 本地模拟 API 服务器

为了方便学习和测试，我们提供了一个**本地模拟 API 服务器** `server/mock_api_server.py`。

**为什么需要本地服务器？**

1. **学习调试方便**：不用依赖外部网络，随时可以测试
2. **数据可控**：可以自定义返回数据，方便测试各种边界情况
3. **不影响真实站点**：学习阶段不会对真实网站造成请求压力
4. **快速验证**：修改代码后可以立即验证效果

**模拟服务器提供的接口：**

| 接口 | URL 示例 | 作用 |
|------|----------|------|
| 首页接口 | `/api.php?ac=list` | 返回分类列表和首页推荐 |
| 分类列表 | `/api.php?ac=detail&t=1&pg=1` | 返回指定分类的视频列表（支持分页） |
| 详情接口 | `/api.php?ac=detail&ids=1,2,3` | 返回一个或多个视频的详情 |
| 搜索接口 | `/api.php?ac=detail&wd=关键词` | 根据关键词搜索视频 |

服务器使用 Python 标准库 `http.server` 实现，**无需安装第三方依赖**。

### 如何运行和测试

#### 1. 测试模拟 API 服务器

```bash
python Tests/test_mock_api.py
```

这个脚本会：
- 自动启动本地服务器（端口 8899）
- 依次测试首页、分类列表、详情、搜索接口
- 验证返回数据格式是否正确
- 测试完成后自动关闭服务器

#### 2. 测试 JsonSpider 单元

```bash
python Tests/test_json_spider.py
```

这个脚本会：
- 启动本地 API 服务器
- 创建 JsonSpider 实例
- 测试 `home_content`、`category_content`、`detail_content`、`search_content`、`player_content` 五个核心接口
- 测试空 API URL 的容错处理
- 统计测试通过率

#### 3. 端到端集成测试

```bash
python Tests/test_integration.py
```

这个脚本验证从配置加载到爬虫创建再到数据获取的完整流程，包括：
- 配置文件加载和视频源类型识别
- JsonSpider 完整流程测试（首页→分类→详情→搜索）
- 根据视频源类型自动创建对应爬虫（工厂模式）
- 错误处理能力测试

#### 4. 在命令行界面中体验

先启动模拟服务器（单独一个终端）：
```bash
python -m server.mock_api_server
```

然后运行主程序：
```bash
python main.py
```

在视频源列表中选择**第1个**（"🆕本地测试API站"），这就是一个真实的 JSON 接口源，所有数据都来自本地模拟服务器。

---

## 第三阶段：播放地址解析与视频播放

经过前两个阶段的学习，我们已经能从数据源获取视频信息了。第三阶段我们来学习**播放地址解析**和**视频播放**，打通从"选视频"到"看视频"的最后一步。

### 为什么需要播放地址解析器？

视频详情里拿到的播放地址，不一定是可以直接播放的。常见的有几种情况：

| 地址类型 | 说明 | 是否能直接播 |
|----------|------|-------------|
| **直链** | `https://xxx.com/video.m3u8` | ✅ 可以直接播 |
| **分享页** | `https://xxx.com/share/abc123` | ❌ 需要解析 |
| **解析接口** | `https://jx.xxx.com/?url=xxx` | ❌ 需要二次解析 |
| **加密地址** | 加密的字符串 | ❌ 需要解密 |

所以我们需要**解析器**来把各种格式的地址，转换成播放器能直接播放的真实视频地址。

### 解析器插件化架构

参考 TvBox 的设计思想，我们实现了**解析器插件化架构**：

```
BaseParser（解析器基类）
    ├── DirectParser        ← 直链解析器（地址本身就是视频）
    ├── JsVariableParser    ← JS变量解析器（从HTML提取播放地址）
    ├── HtmlVideoParser     ← （待实现）从<video>标签提取
    └── ApiParser           ← （待实现）调用远程解析接口
```

**核心设计思想（开闭原则）：**
- 对扩展开放：添加新的解析器不需要修改已有代码
- 对修改关闭：已有的解析器和管理器代码保持稳定

**和 Spider 的关系：**
解析器和 Spider 用的是同样的设计模式 —— 基类定义接口，子类实现具体逻辑，管理器统一调度。理解了一个，另一个就很容易掌握。

### ParserManager（解析器管理器）

`ParserManager` 负责管理所有解析器，自动选择合适的来解析地址，还支持**链式解析**：

```
输入：分享页URL
    ↓
JsVariableParser 解析 → 得到 m3u8 地址，parse=1（需要继续解析？不，m3u8是直链）
    ↓
DirectParser 判断 → 是直链，parse=0，结束
    ↓
输出：真实播放地址
```

链式解析的好处：一个 URL 可能需要经过多层解析才能拿到真实地址（比如：网页 → 解析接口 → 真实地址），管理器会自动处理。

### JsVariableParser（JS变量解析器）

这是我们实现的第一个"真正的"解析器，用于从视频分享页的 HTML 中提取播放地址。

**适用场景：**
- 视频分享网站（如 phimgood.com）
- 播放地址嵌在页面的 JS 变量中
- 页面结构类似：`const url = "/xxx/index.m3u8?sign=xxx"`

**工作原理：**
```python
# 1. 请求页面 HTML
response = requests.get(url)

# 2. 用正则匹配 JS 变量
pattern = re.compile(r'const\s+url\s*=\s*["\']([^"\']+)["\']')
match = pattern.search(html)

# 3. 补全相对路径（urljoin）
play_url = urljoin(base_url, match.group(1))
```

### 播放器模块

播放模块负责调用系统安装的播放器（VLC、mpv 等）来播放视频。

**为什么不自己实现播放器？**
- 视频解码（H.264、H.265 等）非常复杂
- 音频同步、字幕渲染等功能工作量巨大
- 专业播放器（VLC）已经做得很好了，直接调用就行

TvBox 也是同样的思路 —— 它自己不做解码，而是封装了 IJKPlayer、ExoPlayer 等播放器内核。

**支持的播放器：**
| 播放器 | 说明 | 下载地址 |
|--------|------|----------|
| **VLC** | 功能最全，支持格式最多（推荐） | https://www.videolan.org/vlc/ |
| **mpv** | 轻量高效，启动快 | https://mpv.io/ |

### 完整播放流程

从用户操作到视频播放的完整流程：

```
用户选择某一集
    │
    ▼
拿到剧集地址（可能是直链，也可能是分享页）
    │
    ▼
ParserManager 自动选择解析器
    ├─ 直链 → DirectParser 直接通过
    └─ 分享页 → JsVariableParser 解析出 m3u8
    │
    ▼
得到真实播放地址（m3u8/mp4 等）
    │
    ▼
VideoPlayer 检测系统可用播放器
    │
    ▼
调用 VLC / mpv 开始播放 🎬
```

### 如何运行和测试

#### 1. 测试解析器架构

```bash
python Tests/test_parsers.py
```

验证：
- BaseParser 基类和标准接口
- DirectParser 直链解析
- ParserManager 管理器和优先级
- 链式解析功能

#### 2. 测试 JS 变量解析器（真实地址）

```bash
python Tests/test_js_parser.py
```

用真实的 phimgood.com 分享页测试，验证能否提取出 m3u8 地址。

#### 3. 测试播放器模块

```bash
python Tests/test_player.py
```

检测系统安装的播放器，并用真实视频地址测试播放。

#### 4. 完整播放流程演示

```bash
python demo_play.py
```

一键演示完整流程：爬虫 → 详情 → 线路 → 解析 → 播放。

#### 5. 在命令行界面中体验

```bash
python main.py
```

操作流程：
1. 选择第 1 个视频源（"🆕本地测试API站"）
2. 选择分类（如"电视剧"）
3. 选择一个视频进入详情页
4. 选择播放线路（线路 2"闪电"是分享页，需要解析）
5. 输入集数开始播放！

### Mock 服务器的分享页功能

为了方便学习，Mock API 服务器新增了分享页模拟功能：

| 路由 | 作用 |
|------|------|
| `/share/{vid}` | 模拟视频分享页（返回含 JS 变量的 HTML） |
| `/vod/{vid}.m3u8` | m3u8 播放列表 |
| `/vod/{vid}_{n}.ts` | 视频分片文件 |

分享页的 HTML 结构和 phimgood 一致，包含 `const url = "xxx"` 的 JS 变量。

---

## 第四阶段：Parses 解析器系统

经过前三个阶段的学习，我们已经掌握了视频源配置、JSON 接口爬虫、播放地址解析和视频播放。第四阶段我们来学习 **TvBox 的 parses 解析器系统**，这是 TvBox 中处理播放地址解析的核心机制。

### 什么是 TvBox 的 parses 配置

在 TvBox 的配置文件中，除了 `sites`（视频源数组）之外，还有一个重要的 `parses` 数组——**解析源数组**。它定义了所有可用的播放地址解析器，用于将各种加密、分享页、接口地址转换为可以直接播放的真实视频地址。

**parses 配置示例：**

```json
{
  "parses": [
    {
      "name": "Web嗅探",
      "type": 0,
      "url": "https://web-sniff.example.com/?url=",
      "ext": { "flag": ["qq", "iqiyi", "youku"] }
    },
    {
      "name": "JSON解析",
      "type": 1,
      "url": "https://json-parse.example.com/api?url=",
      "ext": { "flag": ["mgtv", "bilibili"] }
    },
    {
      "name": "Spider解析",
      "type": 3,
      "url": "csp_SomeSpider",
      "ext": { "flag": ["pptv", "le"] }
    }
  ]
}
```

每个解析源包含：
- `name`：解析器名称
- `type`：解析器类型（0/1/3）
- `url`：解析地址或爬虫标识
- `ext.flag`：该解析器支持的平台关键词列表

### parses 的类型

TvBox 的 parses 支持三种解析器类型，分别对应不同的解析方式：

| 类型值 | 名称 | 说明 |
|--------|------|------|
| **0** | Web 嗅探 | 通过请求网页并嗅探 HTML 内容提取真实播放地址 |
| **1** | JSON 接口 | 调用远程 JSON 解析接口，返回结构化播放地址 |
| **3** | Spider 解析 | 执行爬虫代码（JavaScript/Python）获取播放地址 |

**三种解析器的关系：**

```
BaseParseParser（解析器基类）
    ├── WebSniffParser      ← type=0，网页嗅探提取地址
    ├── JsonApiParser       ← type=1，调用 JSON 接口解析
    └── SpiderParseParser   ← type=3，执行爬虫代码解析
```

**和第三阶段解析器的区别：**
- 第三阶段的 `ParserManager` 是**地址格式驱动的**（根据 URL 特征选择解析器）
- 第四阶段的 `ParsesLoader` 是**配置驱动的**（根据 TvBox 配置文件中的 parses 数组创建解析器实例）

### flag 匹配机制

`flag` 是 parses 系统中非常重要的概念，它决定了**哪个解析器用于解析哪个平台的视频**。

**工作原理：**

每个视频源的播放线路都有一个 `flag` 标识（如 `qq`、`iqiyi`、`youku`、`mgtv` 等），表示该视频来自哪个平台。ParsesLoader 会根据这个 `flag` 去匹配解析源的 `ext.flag` 列表，找到最合适的解析器。

**匹配规则：**

```
视频播放地址的 flag = "qq"
    ↓
查找 parses 中 ext.flag 包含 "qq" 的解析源
    ↓
找到匹配 → 使用该解析器解析地址
未找到   → 使用默认解析器或直链播放
```

**示例：**

| 视频 flag | 匹配的解析器 |
|-----------|-------------|
| `qq` | Web嗅探（flag含qq） |
| `iqiyi` | Web嗅探（flag含iqiyi） |
| `mgtv` | JSON解析（flag含mgtv） |
| `bilibili` | JSON解析（flag含bilibili） |
| `pptv` | Spider解析（flag含pptv） |

这种设计的好处是：**精准选择解析器**，不同平台的视频可以使用最适合的解析方式。

### ParsesLoader 的作用

`ParsesLoader` 是连接**配置文件**和**解析器实例**的桥梁，它的核心职责：

1. **加载配置**：从 TvBox 配置文件中读取 `parses` 数组
2. **实例化解析器**：根据每个 parse 的 `type` 创建对应的解析器实例
3. **flag 映射**：建立 `flag → 解析器` 的映射关系，方便快速查找
4. **自动匹配**：提供 `get_parser(flag)` 方法，根据 flag 自动返回合适的解析器

**使用流程：**

```python
# 1. 加载配置
config = ConfigLoader.load("fty.json")

# 2. 创建 ParsesLoader
parses_loader = ParsesLoader(config.get("parses", []))

# 3. 根据 flag 获取解析器
parser = parses_loader.get_parser("qq")

# 4. 解析播放地址
result = parser.parse(video_url)
```

### 如何在 CLI 中自动加载 parses

在命令行界面中，ParsesLoader 会在启动时自动加载：

```python
# cli_app.py 中初始化
from utils.parses_loader import ParsesLoader

class CliApp:
    def __init__(self, config):
        # ... 其他初始化 ...
        self.parses_loader = ParsesLoader(config.get("parses", []))
```

当用户选择视频并播放时，CLI 会根据当前视频的 `flag` 自动从 ParsesLoader 中获取对应的解析器，完成地址解析后再交给播放器播放。

### 如何运行和测试

#### 1. 测试 Parses 系统

```bash
python Tests/test_parses_system.py
```

验证：
- `BaseParseParser` 基类和标准接口
- `WebSniffParser` 网页嗅探解析
- `JsonApiParser` JSON 接口解析
- `SpiderParseParser` Spider 解析
- `flag` 匹配机制

#### 2. 测试 Parses 端到端集成

```bash
python Tests/test_parses_integration.py
```

验证：
- `ParsesLoader` 从配置加载解析器
- 根据 `flag` 自动匹配解析器
- 完整解析流程（配置 → 加载 → 匹配 → 解析）

#### 3. 运行演示

```bash
python demo_parses.py
```

一键演示 Parses 解析器系统的完整功能，展示三种类型解析器的使用方式。

---

## 核心概念

### TvBox 架构概览

TvBox 是一个播放器框架，本身不提供视频内容，而是通过加载配置文件来聚合各种视频源。

```
┌─────────────────────────────────────────────────────────┐
│                      TvBox 客户端                        │
├─────────────┬─────────────────┬─────────────────────────┤
│  配置加载器  │   Spider 引擎   │        播放器            │
└──────┬──────┴────────┬────────┴──────────┬──────────────┘
       │               │                   │
       ▼               ▼                   ▼
┌─────────────┐  ┌──────────┐      ┌─────────────┐
│  配置文件    │  │  爬虫源   │      │  视频播放地址  │
│  (JSON)     │  │  (JS/Py) │      │  (m3u8/mp4) │
└─────────────┘  └──────────┘      └─────────────┘
```

### 1. 配置文件

配置文件是 TvBox 的入口，采用 JSON 格式，定义了所有可用的视频源、直播源等。

**核心结构：**

```json
{
  "sites": [           // 视频源列表
    {
      "key": "唯一标识",
      "name": "视频源名称",
      "type": 3,       // 类型: 0=xml, 1=json, 3=spider
      "api": "接口地址",
      "searchable": 1, // 是否支持搜索
      "ext": ""        // 扩展参数
    }
  ],
  "lives": [],         // 直播源列表
  "spider": "",        // 爬虫 jar/js 地址
  "wallpaper": ""      // 壁纸地址
}
```

**视频源类型速览：**

| 类型值 | 名称 | 说明 |
|--------|------|------|
| 0 | xml | 传统的 XML 视频源，使用 XML 格式返回数据 |
| 1 | json | JSON 视频源，使用 JSON 格式返回数据 |
| 3 | spider | 爬虫源，通过执行爬虫代码获取数据，最灵活 |

### 数据源类型详解

TvBox 支持三种主要的数据源类型，它们代表了视频源技术的演进过程。理解它们的区别和适用场景，有助于我们选择合适的方案。

#### type=0: XML 接口（暂未实现）

**工作方式：**
- 最早的视频源格式
- 通过 HTTP 请求获取 XML 格式的数据
- 解析 XML 提取视频信息

**特点：**
- 格式简单，解析容易
- 表达能力有限（不容易表示复杂结构）
- 现在已经比较少见，逐渐被 JSON 取代

**适用场景：**
- 一些比较老的视频站点
- 对数据格式要求简单的场景

> 💡 本项目暂未实现 XML 接口爬虫，感兴趣的同学可以作为扩展练习自己实现。

#### type=1: JSON 接口（已实现，JsonSpider）

**工作方式：**
- 通过 HTTP 请求获取 JSON 格式的数据
- 解析 JSON 提取视频信息
- 接口格式由苹果CMS、海洋CMS等建站系统标准化

**特点：**
- ✅ 格式清晰，解析高效
- ✅ 有统一的接口标准（苹果CMS格式）
- ✅ 开发简单，只需请求+解析
- ✅ 性能较好，服务器直接返回结构化数据
- ❌ 只能获取站点提供的数据，无法自定义
- ❌ 受限于站点的接口功能

**适用场景：**
- 使用苹果CMS、海洋CMS等建站系统的站点
- 站点有公开的 API 接口
- 对自定义要求不高的场景

**本项目实现：** `spiders/json_spider.py` 中的 `JsonSpider` 类

#### type=3: Spider 爬虫（JS/Jar/Python，当前用 MockSpider 演示）

**工作方式：**
- TvBox 加载并执行爬虫代码（JavaScript 或 Java）
- 爬虫代码自己发送 HTTP 请求、解析网页、提取数据
- 最终返回 TvBox 标准格式的数据

**特点：**
- ✅ 最灵活，可以适配任何网站
- ✅ 可以处理复杂的反爬虫机制
- ✅ 可以自定义数据处理逻辑
- ✅ 可以实现搜索、筛选等高级功能
- ❌ 开发难度最高
- ❌ 维护成本高（网站改版需要同步更新）
- ❌ 性能相对较差（需要解析HTML）

**适用场景：**
- 没有公开 API 的网站
- 需要定制化数据处理的场景
- 对数据源灵活性要求高的场景

**本项目实现：** `spiders/mock_spider.py` 中的 `MockSpider` 类（模拟演示）

#### 三种类型对比

| 对比项 | type=0 (XML) | type=1 (JSON) | type=3 (Spider) |
|--------|--------------|---------------|-----------------|
| 开发难度 | ⭐ 简单 | ⭐⭐ 中等 | ⭐⭐⭐⭐⭐ 困难 |
| 灵活度 | 低 | 中 | 最高 |
| 性能 | 高 | 高 | 较低 |
| 维护成本 | 低 | 低 | 高 |
| 适用站点 | 老站 | CMS建站 | 任意站点 |
| 本项目实现 | ❌ 未实现 | ✅ JsonSpider | ✅ MockSpider(模拟) |

**学习建议：**
- 初学者从 **type=1 (JSON)** 入手，理解数据获取和解析的基本流程
- 有一定基础后研究 **type=3 (Spider)**，学习网页解析和反爬虫
- type=0 (XML) 了解即可，实际使用越来越少

### 2. Spider 接口

Spider（爬虫）是 TvBox 最强大的功能，允许用户自定义数据源。所有爬虫都需要实现一组标准接口。

**接口方法一览：**

| 方法 | 作用 |
|------|------|
| `init(context, extend)` | 初始化爬虫，传入扩展参数 |
| `home_content(filter)` | 获取首页内容（分类 + 推荐） |
| `home_video_content()` | 仅获取首页推荐视频 |
| `category_content(tid, pg, filter, extend)` | 获取分类视频列表 |
| `detail_content(ids)` | 获取视频详情 |
| `search_content(key, quick, pg)` | 搜索视频 |
| `player_content(flag, id, vip_flags)` | 获取播放地址 |

**为什么这样设计？**

- **统一接口**：所有视频源都遵循相同的接口规范，上层代码无需关心底层实现
- **渐进式实现**：所有方法都有默认空实现，可以根据需要逐步实现功能
- **灵活扩展**：通过 ext 参数传递配置，同一爬虫可以适配多个站点

### 3. 数据流转

从用户操作到视频播放的完整数据流：

```
用户点击视频源
    │
    ▼
加载配置 → 创建 Spider 实例 → 调用 init() 初始化
    │
    ▼
用户浏览分类 → 调用 category_content() → 显示视频列表
    │
    ▼
用户点击视频 → 调用 detail_content() → 显示详情和播放线路
    │
    ▼
用户选择剧集 → 调用 player_content() → 获取真实播放地址
    │
    ▼
传给播放器 → 开始播放
```

### 4. 数据模型

#### SourceBean（视频源）

对应配置文件中的一个视频源配置，包含：
- `key`：唯一标识，用于区分不同视频源
- `name`：显示名称
- `type`：源类型（xml/json/spider）
- `api`：接口地址或爬虫类名
- `searchable`/`quickSearch`/`filterable`：功能开关
- `ext`：扩展参数，爬虫初始化时传入

#### VodInfo（视频信息）

存储视频的详细信息，其中最复杂的是播放线路的解析：

```
vod_play_from: "无尽$闪电$量子"     （线路名称，用 $ 分隔）
vod_play_url:  "第1集@url1#第2集@url2$第1集@url3"  （线路间用 $，剧集间用 #）
                                    （单集格式: 集名@URL）
```

解析后结构：
```python
[
  {
    "from": "无尽",
    "episodes": [
      {"name": "第1集", "url": "url1"},
      {"name": "第2集", "url": "url2"}
    ]
  },
  ...
]
```

---

## 命令说明

### 全局命令

| 命令 | 作用 | 可用页面 |
|------|------|----------|
| `q` | 退出程序 | 所有页面 |
| `0` | 返回上一页 | 除源列表外的所有页面 |

### 视频源列表页

| 输入 | 作用 |
|------|------|
| `数字` | 选择对应编号的视频源 |
| `q` | 退出程序 |

### 视频源首页

| 输入 | 作用 |
|------|------|
| `1~N` | 选择对应分类（N为分类数） |
| `N+1~M` | 选择对应推荐视频 |
| `0` | 返回视频源列表 |
| `q` | 退出程序 |

### 分类视频列表页

| 输入 | 作用 |
|------|------|
| `数字` | 查看对应编号的视频详情 |
| `n` | 下一页 |
| `p` | 上一页 |
| `0` | 返回视频源首页 |
| `q` | 退出程序 |

### 视频详情页

| 输入 | 作用 |
|------|------|
| `数字` | 查看对应线路的剧集列表 |
| `0` | 返回上一页（列表页） |
| `q` | 退出程序 |

---

## 后续学习路线

### 第一阶段：架构理解 ✅

- [x] 理解 TvBox 整体架构
- [x] 掌握配置文件格式
- [x] 理解 Spider 接口规范
- [x] 熟悉数据模型
- [x] 体验完整使用流程

### 第二阶段：JSON接口爬虫 ✅

**学习目标：** 掌握 type=1 JSON 接口爬虫的开发

- [x] 理解苹果CMS / 海洋CMS 标准接口格式
- [x] 学习 HTTP 请求库（requests）的使用
- [x] 掌握 JSON / JSONP 数据解析
- [x] 实现 JsonSpider 完整功能
- [x] 学会编写单元测试和集成测试
- [x] 理解本地模拟服务器的作用和实现

### 第三阶段：播放地址解析与视频播放 ✅

**学习目标：** 掌握播放地址解析和播放器集成

- [x] 理解为什么需要播放地址解析器
- [x] 学习解析器插件化架构（和 Spider 一样的设计模式）
- [x] 实现 BaseParser 基类和 ParserManager 管理器
- [x] 实现 DirectParser 直链解析器
- [x] 实现 JsVariableParser JS变量解析器
- [x] 理解链式解析的原理
- [x] 学习调用系统播放器（VLC/mpv）
- [x] 实现播放器检测和自动选择
- [x] 打通完整播放流程：选视频 → 选集 → 解析 → 播放

### 第四阶段：Parses 解析器系统 ✅

**学习目标：** 掌握 TvBox parses 配置和解析器插件化设计

- [x] 理解 TvBox 配置中的 parses 数组（解析源配置）
- [x] 掌握三种 parses 类型：type=0 Web嗅探、type=1 JSON接口、type=3 Spider解析
- [x] 理解 flag 匹配机制（平台关键词匹配解析器）
- [x] 实现 ParseBean 解析源数据模型
- [x] 实现 BaseParseParser 解析器基类和各类型解析器
- [x] 实现 ParsesLoader 解析器加载器（配置 → 实例）
- [x] 在 CLI 中集成 ParsesLoader，自动根据 flag 选择解析器
- [x] 打通完整流程：配置加载 → 解析器实例化 → flag 匹配 → 地址解析

### 第五阶段：HTML 爬虫开发

**学习目标：** 能够编写真实可用的 type=3 Spider 爬虫

- 学习 HTML 解析（BeautifulSoup4 / lxml）
- 学习 CSS 选择器和 XPath 的使用
- 学习正则表达式提取数据
- 练习编写简单的静态站点爬虫
- 学习搜索功能的实现思路和优化
- 学习处理分页、翻页逻辑
- 学习处理动态加载页面（JavaScript 渲染）
- 了解加密解密、反爬虫绕过技巧
- 实战：编写一个完整的视频站点爬虫

### 第六阶段：进阶开发

**学习目标：** 深入理解 TvBox 原理，能够扩展功能

- 研究 TvBox 的 Java 源码
- 理解 Spider 引擎的工作原理（Rhino / JavaScript 执行）
- 学习 Jar 包格式和打包方式
- 理解播放器内核（IJKPlayer / ExoPlayer）
- 学习直播源格式（m3u、txt）
- 研究解析接口（jx、parse）的工作原理
- 开发自定义功能插件

### 第七阶段：项目实战

**学习目标：** 开发完整的项目

- 搭建自己的视频源聚合服务
- 开发 Web 版视频播放器
- 开发移动端视频 App
- 构建视频推荐系统
- 实现视频搜索聚合引擎

---

## 扩展练习

想要深入学习？可以尝试以下练习：

### 入门级

1. 修改 `MockSpider` 中的视频名称，加入你喜欢的影视作品
2. 增加一个新的分类（例如"短剧"）
3. 修改每页显示的视频数量

### 进阶级

1. 实现一个真实的 Spider，从某个公开 API 获取数据
2. 增加搜索功能到命令行界面
3. 实现视频源的筛选（按类型、按名称搜索）

### 高级

1. 实现一个简单的 Web 界面替代命令行
2. 添加缓存机制，避免重复请求
3. 实现多线程并发请求
4. 添加配置文件的导出/导入功能

---

## 常见问题

### Q: 为什么用 Python 而不是 Java？

A: TvBox 本身是用 Java 写的，但 Python 语法更简洁，学习门槛更低。核心概念是相通的，掌握了 Python 版本，再去看 Java 源码会容易很多。

### Q: 这个项目能看真实的视频吗？

A: 目前使用的是 Mock 模拟数据，不能直接观看真实视频。但本项目已经实现了完整的 parses 解析器系统，支持通过配置加载真实解析接口。如果你提供真实的视频源配置和解析接口，就可以基于这个框架观看真实视频。

### Q: Spider 类型的源是怎么工作的？

A: 在真实的 TvBox 中，spider 类型的源会执行 JavaScript 代码或调用 Java 类来获取数据。本项目用 Python 类模拟了这个机制，原理是一样的。

### Q: 为什么要有三种源类型（xml/json/spider）？

A: 这是历史演进的结果：
- **xml**：最早的格式，简单但表达能力有限
- **json**：比 xml 更灵活，解析更高效
- **spider**：最灵活，可以处理任何网站，但开发成本最高

---

## 许可证

本项目仅供学习研究使用，请遵守相关法律法规，不要用于非法用途。

---

## 参考资源

- TvBox 官方仓库（自行搜索）
- 各种 Spider 开发教程
- Python 爬虫入门教程
