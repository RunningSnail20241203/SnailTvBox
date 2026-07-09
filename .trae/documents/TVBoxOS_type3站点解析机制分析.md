# TVBoxOS type=3 站点解析机制原理解析

> 本文档基于对 TVBoxOS 官方 Java 源码（`C:\MyTools\TvBox\TVBoxOS`）的深入阅读，系统梳理 type=3 Spider 站点的加载、调度、执行全流程，作为学习研究资料。

---

## 一、什么是 type=3 站点

在 TvBox 配置文件的 `sites` 数组中，每个站点都有一个 `type` 字段：

| type 值 | 名称 | 说明 |
|---------|------|------|
| 0 | XML | XML 接口源（B2B CMS 旧格式） |
| 1 | JSON | JSON 接口源（苹果CMS/海洋CMS 格式） |
| 2 | 混合 | JSON + XML 混合 |
| **3** | **Spider** | **爬虫源（核心，最灵活）** |
| 4 | Remote | 远程源 |

**type=3 是 Spider 爬虫源**，它的核心特点是：**站点采集逻辑不在 APP 内固定，而是通过外部插件（Jar 包或 JS 脚本）动态加载**。这意味着新增一个视频源无需重新编译 APP，只需在配置中添加一条 sites 条目即可。

"虾米影视"这类站点就是典型的 type=3 配置——它的采集逻辑由一段独立的 Spider 代码实现，APP 运行时按配置动态加载并调用。

---

## 二、核心调度入口：ApiConfig.getCSP()

**文件**: [ApiConfig.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/api/ApiConfig.java)

type=3 站点的总调度入口是 `ApiConfig.getCSP(SourceBean)` 方法。它的设计精髓在于：**不是根据 type 值分流，而是根据 `api` 字段的文件扩展名分流**。

```java
public Spider getCSP(SourceBean sourceBean) {
    if (sourceBean.getApi().endsWith(".js") || sourceBean.getApi().contains(".js?")){
        currentPyKey = "";
        return jsLoader.getSpider(key, api, ext, jar);   // JS 引擎路线
    }
    else if (sourceBean.getApi().contains(".py")) {
        currentPyKey = sourceBean.getKey();
        return pyLoader.getSpider(key, api, ext);          // Python 引擎路线
    }
    else {
        currentPyKey = "";
        return jarLoader.getSpider(key, api, ext, jar);    // Jar/Dex 路线
    }
}
```

**三种加载路线对照：**

| api 字段格式 | 加载器 | 引擎 | 虾米影视常用方式 |
|--------------|--------|------|------------------|
| `https://xxx/xiami.js` | JsLoader | QuickJS 解释器 | ✅ 现代 JS 爬虫主流 |
| `https://xxx/xiami.py` | IPyLoader | Python 解释器 | 较少 |
| `csp_XiaMi`（类名） | JarLoader | DexClassLoader | ✅ 传统 Jar 爬虫 |

ApiConfig 持有三个 Loader 实例：

```java
private final JarLoader jarLoader = new JarLoader();
private final JsLoader jsLoader = new JsLoader();
private final IPyLoader pyLoader = new pyLoader();
```

---

## 三、Spider 基类：统一接口规范

**文件**: [Spider.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/catvod/crawler/Spider.java)

无论哪种加载路线，所有 Spider 都实现同一个抽象基类 `Spider`，这是整个插件化架构的基石——**上层调用方完全不需要知道底层是 JS 还是 Jar**。

```java
public class Spider {
    public String siteKey;

    public void init(Context context, String extend) { }     // 初始化，extend=配置的ext字段
    public void initApi(SpiderApi api) { }                    // 注入工具API

    public String homeContent(boolean filter) { return ""; }  // 首页(分类+推荐)
    public String homeVideoContent() { return ""; }           // 仅首页推荐
    public String categoryContent(String tid, String pg,
                                  boolean filter,
                                  HashMap<String,String> extend) { return ""; }  // 分类列表
    public String detailContent(List<String> ids) { return ""; }    // 视频详情
    public String searchContent(String key, boolean quick) { return ""; }
    public String searchContent(String key, boolean quick, String pg) { }
    public String playerContent(String flag, String id,
                                List<String> vipFlags) { return ""; }  // 播放地址（关键）

    public boolean isVideoFormat(String url) { return false; }  // webview嗅探判断
    public boolean manualVideoCheck() { return false; }
    public String liveContent(String url) { return ""; }
    public Object[] proxyLocal(Map<String,String> params) { return null; }
    public void destroy() {}
}
```

**关键设计点：**
- 所有方法返回的都是 **JSON 字符串**（不是对象），由上层解析
- `init(context, extend)` 的 `extend` 参数就是配置文件中的 `ext` 字段，实现配置透传
- `SpiderNull.java` 是空实现占位符，加载失败时返回它，避免 NPE

---

## 四、Jar Spider 加载机制（传统 csp_ 方式）

**文件**: [JarLoader.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/catvod/crawler/JarLoader.java)

这是 TVBox 最早的爬虫加载方式，`api` 字段是**类名标识**（如 `csp_XiaMi`）。

### 4.1 加载流程

```java
public Spider getSpider(String key, String cls, String ext, String jar) {
    if (spiders.containsKey(key)) return spiders.get(key);   // 1. 缓存命中直接返回

    String clsKey = cls.replace("csp_", "");          // 2. csp_XiaMi → XiaMi
    DexClassLoader classLoader;
    if (jar.isEmpty()) {
        classLoader = classLoaders.get("main");        // 3a. 用全局 spider jar
    } else {
        String[] urls = jar.split(";md5;");            // 3b. 用站点私有 jar
        classLoader = loadJarInternal(urls[0], urls[1], jarKey);
    }

    // 4. 反射加载类: com.github.catvod.spider.XiaMi
    Spider sp = (Spider) classLoader.loadClass(
        "com.github.catvod.spider." + clsKey
    ).newInstance();
    sp.siteKey = key;
    sp.initApi(new SpiderApi());       // 注入工具API
    sp.init(App.getInstance(), ext);   // ext 透传
    spiders.put(key, sp);
    return sp;
}
```

### 4.2 关键细节

- **类名约定**：`api` 字段去掉 `csp_` 前缀后，拼接到固定包名 `com.github.catvod.spider.` 下
- **Jar 来源**：配置顶层有全局 `spider` 字段（jar URL），站点可单独用 `jar` 字段覆盖
- **Jar 格式**：`url;md5;md5值`，支持 md5 校验避免重复下载
- **自举机制**：加载 jar 时会先加载其中的 `com.github.catvod.spider.Init` 类并调用 `init(Context)` 完成爬虫内部初始化
- **保护机制**：支持 `img+` 前缀的图片隐藏 jar、加密 dex 等反扒手段

### 4.3 虾米影视的 Jar 配置示例

```json
{
  "spider": "https://xxx/spider.jar;md5;abc123",
  "sites": [
    {
      "key": "csp_XiaMi",
      "name": "虾米影视",
      "type": 3,
      "api": "csp_XiaMi",
      "searchable": 1,
      "quickSearch": 1,
      "filterable": 1,
      "ext": "站点扩展配置"
    }
  ]
}
```

---

## 五、JS Spider 加载机制（现代主流方式）

**文件**: [JsLoader.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/catvod/crawler/JsLoader.java) + [JsSpider.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/util/js/JsSpider.java)

这是当前最主流的 Spider 加载方式，`api` 字段是 **JS 文件的 URL**。其核心是 **QuickJS 引擎**（一个轻量级 JS 解释器）。

### 5.1 JsLoader 加载流程

```java
public Spider getSpider(String key, String api, String ext, String jar) {
    if (spiders.containsKey(key)) return spiders.get(key);   // 缓存
    Class<?> classLoader = null;
    if (!jar.isEmpty()) {
        // 注意：JS 爬虫的 jar 不是爬虫本身，而是 JS API 扩展 dex
        // 加载含 com.github.catvod.js.Method 的 dex，绑定到 JS 全局对象 jsapi
        classLoader = loadJarInternal(jarUrl, jarMd5, jarKey);
    }
    Spider sp = new JsSpider(key, api, classLoader);   // 创建 QuickJS Spider
    sp.init(App.getInstance(), ext);                    // ext 透传
    spiders.put(key, sp);
    return sp;
}
```

### 5.2 JsSpider 的 JS 方法名映射

JsSpider 把 Java Spider 接口映射为 JS 全局函数名（**注意名称不同**）：

| Java Spider 方法 | JS 函数名 | 作用 |
|------------------|-----------|------|
| init(extend) | `init` | 初始化 |
| homeContent(filter) | `home` | 首页 |
| homeVideoContent() | `homeVod` | 首页推荐 |
| categoryContent(tid,pg,filter,extend) | `category` | 分类列表 |
| detailContent(ids) | `detail` | 视频详情 |
| searchContent(key,quick) | `search` | 搜索 |
| **playerContent(flag,id,vipFlags)** | **`play`** | **播放地址** |
| liveContent(url) | `live` | 直播 |
| isVideoFormat(url) | `isVideo` | 嗅探判断 |
| manualVideoCheck() | `sniffer` | 手动检测 |
| proxyLocal(params) | `proxy` | 代理 |

例如 `playerContent` 的实现：

```java
@Override
public String playerContent(String flag, String id, List<String> vipFlags) {
    try {
        JSArray array = submit(() -> new JSUtils<String>().toArray(ctx, vipFlags)).get();
        return (String) call("play", flag, id, array);   // 调用 JS 的 play 函数
    } catch (Exception e) { return null; }
}
```

### 5.3 JS 模块加载机制

JsSpider 支持三种 JS 格式（`initializeJS` 方法）：

1. **`//bb` 前缀** → Base64 编码的 QuickJS 字节码（防源码泄露）
2. **`__jsEvalReturn`** → cat 框架老格式，调用 `__jsEvalReturn()` 工厂函数返回 spider 对象
3. **`export default`** → ES Module 标准格式（现代主流）

加载逻辑：

```java
String content = FileUtils.loadModule(api);   // 从 api(URL) 下载 JS 内容
if (content.contains("__JS_SPIDER__")) {
    content = content.replaceAll("__JS_SPIDER__\\s*=", "export default ");
}
ctx.evaluateModule(content, api);              // QuickJS 编译执行模块
jsObject = (JSObject) ctx.get(ctx.getGlobalObject(), key);  // 取出导出的 spider 对象
```

### 5.4 JS 运行时环境

JsSpider 在创建 QuickJS 上下文时，会预加载支撑库：

| 预加载文件 | 作用 |
|------------|------|
| `net.js` | HTTP 请求工具，绑定到全局 `http`/`req` |
| `模板.js` | 爬虫模板系统，提供 `muban` 字典（mxpro、mxone5、首图等预设模板） |

这些支撑库位于 [assets/js/lib/](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/assets/js/lib/)，使所有 JS 爬虫都能直接使用 `http`、`muban` 等全局对象。

**线程安全**：所有 JS 调用通过单线程 `executor` 串行执行，保证 QuickJS 的线程安全。

### 5.5 虾米影视的 JS 配置示例

```json
{
  "sites": [
    {
      "key": "csp_XiaMi",
      "name": "虾米影视",
      "type": 3,
      "api": "https://raw.githubusercontent.com/xxx/xiami.js",
      "searchable": 1,
      "ext": "站点扩展配置JSON"
    }
  ]
}
```

---

## 六、完整调用流程

**文件**: [SourceViewModel.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/viewmodel/SourceViewModel.java)

SourceViewModel 是 UI 层与 Spider 之间的桥梁，每个业务方法都按 `type` 分支，type==3 时通过 `getCSP()` 获取 Spider 实例后调用对应方法。

### 6.1 首页（homeContent）

```java
if (type == 3) {
    Spider sp = ApiConfig.get().getCSP(sourceBean);
    String json = sp.homeContent(true);        // 30秒超时
    // 解析 json 中的 class(分类) + list(推荐)
}
```

### 6.2 分类列表（categoryContent）

```java
if (type == 3) {
    Spider sp = ApiConfig.get().getCSP(homeSourceBean);
    return sp.categoryContent(tid, page+"", true, filterSelect);
}
```

### 6.3 视频详情（detailContent）

```java
if (type == 3) {
    Spider sp = ApiConfig.get().getCSP(sourceBean);
    List<String> ids = new ArrayList<>(); ids.add(id);
    return sp.detailContent(ids);              // 15秒超时
}
```

### 6.4 搜索（searchContent）

```java
if (type == 3) {
    Spider sp = ApiConfig.get().getCSP(sourceBean);
    String search = sp.searchContent(wd, false);
}
```

### 6.5 播放地址（playerContent）—— 衔接解析的关键

```java
if (type == 3) {
    Spider sp = ApiConfig.get().getCSP(sourceBean);
    String json = sp.playerContent(playFlag, url, ApiConfig.get().getVipParseFlags());
    JSONObject result = normalizePlayerResult(new JSONObject(json));
    result.put("flag", playFlag);
    postPlayResult(requestSeq, result);
}
```

---

## 七、player_content 如何触发解析

**文件**: [PlayActivity.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/ui/activity/PlayActivity.java)

Spider 的 `playerContent` 返回的 JSON 中，`parse` 字段决定**直接播放**还是**进入解析流程**：

```java
boolean parse = info.optString("parse", "1").equals("1");   // 默认需解析
boolean jx = info.optString("jx", "0").equals("1");
String flag = info.optString("flag");
String url = info.getString("url");
String playUrl = info.optString("playUrl", "");

if (parse || jx) {
    // 需要解析 → 调度 parses 列表中的解析器
    boolean userJxList = (playUrl.isEmpty() &&
                          ApiConfig.get().getVipParseFlags().contains(flag)) || jx;
    initParse(flag, userJxList, playUrl, url);
} else {
    // 直接播放
    playUrl(playUrl + url, headers);
}
```

### 7.1 normalizePlayerResult 的 url 前缀处理

| url 前缀 | 处理 | parse 设置 |
|----------|------|------------|
| `video://` | 去前缀 | parse=1（需解析） |
| `proxy://` | 替换为代理地址 | parse=0（直接播） |
| 直链视频格式 + 无 playUrl | 直接返回 | parse=0（直接播） |

### 7.2 解析器调度（initParse）

`initParse` 根据 `playUrl` 前缀选择解析器类型：

| playUrl 前缀 | 解析器类型 | 说明 |
|--------------|-----------|------|
| `json:` | type=1 JSON 解析器 | 调用第三方解析接口 |
| `parse:` | 按名称匹配 parses 列表 | 指定解析源 |
| 其他 | type=0 Web 嗅探解析器 | WebView 嗅探视频地址 |

---

## 八、配置字段含义总结

type=3 站点的配置字段含义取决于子类型（Jar/JS/Python）：

### Jar Spider（api 非 .js/.py）

| 字段 | 含义 | 示例 |
|------|------|------|
| `api` | Spider 类名标识 | `csp_XiaMi` |
| `ext` | 透传给 `spider.init()` 的字符串 | 站点配置 JSON |
| `jar` | 站点私有 jar URL（覆盖全局 spider） | `url;md5;md5值` |

### JS Spider（api 含 .js）

| 字段 | 含义 | 示例 |
|------|------|------|
| `api` | JS 文件 URL | `https://xxx/xiami.js` |
| `ext` | 传给 JS `init(cfg)` 的配置 | 站点扩展配置 |
| `jar` | JS API 扩展 dex（含 `com.github.catvod.js.Method`） | dex URL |

---

## 九、架构精髓总结

TVBoxOS 的 type=3 Spider 体系体现了以下设计思想：

### 9.1 三层分流架构

```
配置 type==3
    ↓
ApiConfig.getCSP() 按 api 扩展名分流
    ↓
┌─────────────┬─────────────┬─────────────┐
│  JarLoader  │  JsLoader   │  PyLoader   │
│ DexClassLdr │   QuickJS   │  Python     │
└─────────────┴─────────────┴─────────────┘
    ↓               ↓             ↓
         统一 Spider 接口
    ↓
SourceViewModel 统一调用 homeContent/categoryContent/...
```

### 9.2 核心设计原则

1. **面向接口编程**：所有 Spider 实现同一基类，上层无需感知底层引擎
2. **配置驱动**：ext 字段从 JSON 配置一路透传到 `spider.init()`，新增源无需改代码
3. **开闭原则**：新增 Spider 类型（如未来加 WASM）只需新增 Loader，不改上层
4. **双引擎并存**：Jar 适合闭源商业爬虫（编译期保护），JS 适合开源社区爬虫（易分享）
5. **解析解耦**：`playerContent` 只返回 url + parse 标志，具体解析交给独立的 parses 系统

### 9.3 为什么找不到"虾米"源码

在 TVBoxOS 代码库中**找不到任何 "虾米/xiami" 的引用**，这是设计使然：

- TVBoxOS 本身只是**爬虫引擎**，不内置任何站点爬虫
- 具体站点爬虫（如虾米）的 JS/Jar 文件托管在远端 URL
- 用户通过配置文件的 `api` 字段指向该爬虫文件
- 应用运行时动态下载并加载执行

这种"引擎 + 外部插件"的架构，使得 TvBox 能够聚合无限多的视频源，而 APP 本身保持精简。

---

## 十、关键源码索引

| 文件 | 作用 |
|------|------|
| [Spider.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/catvod/crawler/Spider.java) | Spider 基类，定义标准接口 |
| [SpiderNull.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/catvod/crawler/SpiderNull.java) | 空实现占位符 |
| [ApiConfig.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/api/ApiConfig.java) | 总调度入口（getCSP 方法） |
| [JarLoader.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/catvod/crawler/JarLoader.java) | Jar 爬虫加载器 |
| [JsLoader.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/catvod/crawler/JsLoader.java) | JS 爬虫加载器 |
| [JsSpider.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/util/js/JsSpider.java) | QuickJS 引擎 Spider 实现 |
| [SourceBean.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/bean/SourceBean.java) | 视频源数据模型 |
| [SourceViewModel.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/viewmodel/SourceViewModel.java) | UI 与 Spider 桥梁 |
| [PlayActivity.java](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/java/com/github/tvbox/osc/ui/activity/PlayActivity.java) | 播放与解析调度 |
| [assets/js/lib/](file:///C:/MyTools/TvBox/TVBoxOS/app/src/main/assets/js/lib/) | JS 运行时支撑库 |
