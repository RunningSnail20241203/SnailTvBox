"""
苹果CMS 格式的本地 JSON API 测试服务器
使用 Python 标准库 http.server 实现，无需第三方依赖

支持接口：
1. 首页接口: GET /api.php?ac=list
2. 分类列表接口: GET /api.php?ac=detail&t={tid}&pg={pg}
3. 详情接口: GET /api.php?ac=detail&ids={vod_id}
4. 搜索接口: GET /api.php?ac=detail&wd={keyword}
"""

import json
import random
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==================== 配置常量 ====================

SERVER_PORT = 8899
PAGE_SIZE = 5
ITEMS_PER_CATEGORY = 15

# ==================== 模拟数据生成 ====================

# 分类数据
CATEGORIES = [
    {"type_id": "1", "type_name": "电影"},
    {"type_id": "2", "type_name": "电视剧"},
    {"type_id": "3", "type_name": "综艺"},
    {"type_id": "4", "type_name": "动漫"},
]

# 电影数据（15部）
MOVIE_NAMES = [
    "流浪地球", "满江红", "消失的她", "孤注一掷", "封神第一部",
    "八佰", "长津湖", "我和我的祖国", "你好，李焕英", "唐人街探案3",
    "速度与激情10", "蜘蛛侠：纵横宇宙", "阿凡达：水之道", "盗梦空间", "星际穿越",
]

MOVIE_DIRECTORS = [
    "郭帆", "张艺谋", "崔睿", "申奥", "乌尔善",
    "管虎", "陈凯歌", "陈凯歌", "贾玲", "陈思诚",
    "路易斯·莱特里尔", "乔伊姆·多斯·桑托斯", "詹姆斯·卡梅隆", "克里斯托弗·诺兰", "克里斯托弗·诺兰",
]

MOVIE_ACTORS = [
    "吴京,刘德华", "沈腾,易烊千玺", "朱一龙,倪妮", "张艺兴,金晨", "费翔,李雪健",
    "王千源,张译", "吴京,易烊千玺", "黄渤,张译", "贾玲,张小斐", "王宝强,刘昊然",
    "范·迪塞尔,米歇尔·罗德里格兹", "沙梅克·摩尔,海莉·斯坦菲尔德", "萨姆·沃辛顿,佐伊·索尔达娜", "莱昂纳多·迪卡普里奥,约瑟夫·高登-莱维特", "马修·麦康纳,安妮·海瑟薇",
]

# 电视剧数据（15部）
TV_NAMES = [
    "狂飙", "人世间", "三体", "去有风的地方", "繁花",
    "漫长的季节", "隐秘的角落", "庆余年", "琅琊榜", "甄嬛传",
    "长相思", "莲花楼", "一念关山", "玉骨遥", "梦中的那片海",
]

TV_DIRECTORS = [
    "徐纪周", "李路", "杨磊", "丁梓光", "王家卫",
    "辛爽", "辛爽", "孙皓", "孔笙", "郑晓龙",
    "秦榛", "郭虎", "周靖韬", "蒋家骏", "付宁",
]

TV_ACTORS = [
    "张译,张颂文", "殷桃,雷佳音", "张鲁一,于和伟", "刘亦菲,李现", "胡歌,马伊琍",
    "范伟,秦昊", "秦昊,王景春", "张若昀,李沁", "胡歌,刘涛", "孙俪,陈建斌",
    "杨紫,张晚意", "成毅,曾舜晞", "刘诗诗,刘宇宁", "肖战,任敏", "肖战,李沁",
]

# 综艺数据（15部）
VARIETY_NAMES = [
    "奔跑吧", "极限挑战", "向往的生活", "快乐大本营", "王牌对王牌",
    "中国好声音", "歌手", "爸爸去哪儿", "乘风破浪的姐姐", "披荆斩棘的哥哥",
    "吐槽大会", "脱口秀大会", "奇葩说", "朗读者", "中国诗词大会",
]

VARIETY_DIRECTORS = [
    "陆皓", "严敏", "王征宇", "何炅", "吴彤",
    "金磊", "洪涛", "谢涤葵", "吴梦知", "吴梦知",
    "张绍刚", "张绍刚", "马东", "董卿", "董卿",
]

VARIETY_ACTORS = [
    "李晨,杨颖,郑恺", "黄渤,孙红雷,黄磊", "黄磊,何炅,彭昱畅", "何炅,谢娜,李维嘉", "沈腾,贾玲,华晨宇",
    "那英,庾澄庆,汪峰", "刘欢,齐豫,杨坤", "林志颖,郭涛,王岳伦", "宁静,张雨绮,万茜", "陈小春,谢天华,林晓峰",
    "李诞,王建国,呼兰", "李诞,罗永浩,杨笠", "马东,蔡康永,薛兆丰", "董卿,濮存昕,李敬泽", "董卿,康震,蒙曼",
]

# 动漫数据（15部）
ANIME_NAMES = [
    "斗罗大陆", "斗破苍穹", "完美世界", "遮天", "凡人修仙传",
    "海贼王", "火影忍者", "进击的巨人", "鬼灭之刃", "咒术回战",
    "间谍过家家", "电锯人", "进击的巨人 最终季", "葬送的芙莉莲", "药屋少女的呢喃",
]

ANIME_DIRECTORS = [
    "沈乐平", "赵丙乐", "汪成果", "罗乐", "伍彬",
    "宇田钢之助", "伊达勇登", "荒木哲郎", "外崎春雄", "御所园翔太",
    "古桥一浩", "中山龙", "林祐一郎", "斋藤哲人", "长沼范裕",
]

ANIME_ACTORS = [
    "肖战,吴宣仪", "张沛,黑石稔", "边江,陈张太康", "陈张太康,赵爽", "钱文青,李诗萌",
    "田中真弓,冈村明美", "竹内顺子,杉山纪彰", "梶裕贵,石川由依", "花江夏树,鬼头明里", "榎木淳弥,濑户麻沙美",
    "江口拓也,种崎敦美", "户谷菊之介,楠木灯", "梶裕贵,石川由依", "种崎敦美,冈本信彦", "悠木碧,大冢刚央",
]


def generate_vod_list():
    """
    生成所有视频数据
    返回：按分类组织的视频字典 {category_id: [vod_list]}
    """
    all_vods = {}
    vod_id_counter = 1

    # 电影
    movie_vods = []
    for i in range(ITEMS_PER_CATEGORY):
        vod = _create_vod_item(
            vod_id=str(vod_id_counter),
            name=MOVIE_NAMES[i],
            director=MOVIE_DIRECTORS[i],
            actor=MOVIE_ACTORS[i],
            year=str(2020 + (i % 5)),
            area="大陆" if i < 10 else "美国",
            category_id="1",
            category_name="电影",
            episode_count=1,
            remarks="HD"
        )
        movie_vods.append(vod)
        vod_id_counter += 1
    all_vods["1"] = movie_vods

    # 电视剧
    tv_vods = []
    for i in range(ITEMS_PER_CATEGORY):
        episode_count = random.randint(20, 40)
        vod = _create_vod_item(
            vod_id=str(vod_id_counter),
            name=TV_NAMES[i],
            director=TV_DIRECTORS[i],
            actor=TV_ACTORS[i],
            year=str(2020 + (i % 5)),
            area="大陆",
            category_id="2",
            category_name="电视剧",
            episode_count=episode_count,
            remarks=f"更新至{episode_count}集"
        )
        tv_vods.append(vod)
        vod_id_counter += 1
    all_vods["2"] = tv_vods

    # 综艺
    variety_vods = []
    for i in range(ITEMS_PER_CATEGORY):
        episode_count = random.randint(10, 20)
        vod = _create_vod_item(
            vod_id=str(vod_id_counter),
            name=VARIETY_NAMES[i],
            director=VARIETY_DIRECTORS[i],
            actor=VARIETY_ACTORS[i],
            year=str(2020 + (i % 5)),
            area="大陆",
            category_id="3",
            category_name="综艺",
            episode_count=episode_count,
            remarks=f"更新至第{episode_count}期"
        )
        variety_vods.append(vod)
        vod_id_counter += 1
    all_vods["3"] = variety_vods

    # 动漫
    anime_vods = []
    for i in range(ITEMS_PER_CATEGORY):
        episode_count = random.randint(20, 50)
        vod = _create_vod_item(
            vod_id=str(vod_id_counter),
            name=ANIME_NAMES[i],
            director=ANIME_DIRECTORS[i],
            actor=ANIME_ACTORS[i],
            year=str(2020 + (i % 5)),
            area="大陆" if i < 8 else "日本",
            category_id="4",
            category_name="动漫",
            episode_count=episode_count,
            remarks=f"更新至第{episode_count}集"
        )
        anime_vods.append(vod)
        vod_id_counter += 1
    all_vods["4"] = anime_vods

    return all_vods


def _create_vod_item(vod_id, name, director, actor, year, area,
                     category_id, category_name, episode_count, remarks):
    """
    创建单个视频条目

    参数:
        vod_id: 视频ID
        name: 视频名称
        director: 导演
        actor: 演员
        year: 年份
        area: 地区
        category_id: 分类ID
        category_name: 分类名称
        episode_count: 集数
        remarks: 备注

    返回:
        视频信息字典
    """
    # 生成播放线路（无尽、闪电）
    play_from = "无尽$闪电"

    # 生成无尽线路播放地址（直链 m3u8）
    wujin_urls = []
    for ep in range(1, episode_count + 1):
        wujin_urls.append(f"第{ep}集@http://localhost:{SERVER_PORT}/vod/{vod_id}_wujin_{ep}.m3u8")

    # 生成闪电线路播放地址（分享页地址，需要解析）
    shandian_urls = []
    for ep in range(1, episode_count + 1):
        shandian_urls.append(f"第{ep}集@http://localhost:{SERVER_PORT}/share/{vod_id}_shandian_{ep}")

    play_url = "$".join([
        "#".join(wujin_urls),
        "#".join(shandian_urls)
    ])

    return {
        "vod_id": vod_id,
        "vod_name": name,
        "vod_pic": f"https://picsum.photos/seed/vod{vod_id}/300/400",
        "vod_content": f"{name}是一部由{director}执导，{actor}主演的{year}年{area}{category_name}。影片讲述了一个引人入胜的故事，深受观众喜爱。",
        "vod_director": director,
        "vod_actor": actor,
        "vod_year": year,
        "vod_area": area,
        "vod_remarks": remarks,
        "vod_play_from": play_from,
        "vod_play_url": play_url,
        "type_id": category_id,
        "type_name": category_name,
    }


# 全局视频数据缓存
_ALL_VODS = None
_ALL_VODS_BY_ID = None


def get_all_vods():
    """获取所有视频数据（按分类组织）"""
    global _ALL_VODS
    if _ALL_VODS is None:
        _ALL_VODS = generate_vod_list()
    return _ALL_VODS


def get_vod_by_id():
    """获取所有视频数据（按ID索引）"""
    global _ALL_VODS_BY_ID
    if _ALL_VODS_BY_ID is None:
        all_vods = get_all_vods()
        _ALL_VODS_BY_ID = {}
        for cat_vods in all_vods.values():
            for vod in cat_vods:
                _ALL_VODS_BY_ID[vod["vod_id"]] = vod
    return _ALL_VODS_BY_ID


# ==================== HTTP 请求处理器 ====================

class MockApiHandler(BaseHTTPRequestHandler):
    """
    模拟苹果CMS API 的 HTTP 请求处理器
    """

    def log_message(self, format, *args):
        """
        重写日志方法，自定义访问日志格式
        打印请求路径和返回状态码
        """
        print(f"[访问日志] {self.address_string()} - {self.command} {self.path} - 状态码: {args[1]}")

    def do_GET(self):
        """
        处理 GET 请求
        解析 URL，路由到对应接口
        """
        parsed = urllib.parse.urlparse(self.path)

        # 处理分享页路由（模拟视频分享网站）
        if parsed.path.startswith("/share/"):
            self._handle_share_page(parsed)
            return

        # 处理 m3u8 文件（模拟真实的 HLS 视频流）
        if parsed.path.startswith("/vod/") and parsed.path.endswith(".m3u8"):
            self._handle_m3u8(parsed)
            return

        # 处理 .ts 文件（模拟视频分片）
        if parsed.path.startswith("/vod/") and parsed.path.endswith(".ts"):
            self._handle_ts(parsed)
            return

        # 只处理 /api.php 路径
        if parsed.path != "/api.php":
            self._send_json_response(404, {"code": 404, "msg": "Not Found"})
            return

        # 解析查询参数
        params = urllib.parse.parse_qs(parsed.query)
        ac = params.get("ac", [""])[0]

        if ac == "list":
            # 首页接口
            self._handle_list()
        elif ac == "detail":
            # 判断是分类列表、详情还是搜索
            if "ids" in params:
                # 详情接口
                self._handle_detail(params)
            elif "wd" in params:
                # 搜索接口
                self._handle_search(params)
            elif "t" in params:
                # 分类列表接口
                self._handle_category_list(params)
            else:
                self._send_json_response(400, {"code": 400, "msg": "参数错误"})
        else:
            self._send_json_response(400, {"code": 400, "msg": "参数错误"})

    def _handle_share_page(self, parsed):
        """
        处理分享页: GET /share/{vid}
        返回包含 JS 变量的 HTML 页面（模拟 phimgood 格式）
        
        页面中包含:
        - const vid = "xxx"
        - const url = "/vod/xxx.m3u8"
        - const pic = "/vod/xxx.jpg"
        """
        # 提取视频ID
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) < 2:
            self._send_html_response(404, "<h1>404 Not Found</h1>")
            return
        
        vid = path_parts[1]
        
        # 生成 m3u8 地址（相对路径）
        m3u8_url = f"/vod/{vid}.m3u8"
        pic_url = f"https://picsum.photos/seed/{vid}/300/400"
        
        # 生成 HTML（模拟 phimgood 的 share 页面格式）
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>分享视频 - {vid}</title>
    <style>
        body {{ margin: 0; padding: 0; background: #000; }}
        .player {{ width: 100vw; height: 100vh; }}
    </style>
    <script>
        const vid = "{vid}";
        const url = "{m3u8_url}";
        const pic = "{pic_url}";
        const resumeKey = "{vid}:progress";
    </script>
</head>
<body>
    <div class="player" id="player"></div>
</body>
</html>"""
        
        self._send_html_response(200, html)

    def _handle_m3u8(self, parsed):
        """
        处理 m3u8 文件请求
        返回一个简单的 m3u8 播放列表
        """
        path_parts = parsed.path.strip("/").split("/")
        filename = path_parts[-1] if path_parts else "video.m3u8"
        vid = filename.replace(".m3u8", "")
        
        # 生成简单的 m3u8 内容（5个分片）
        m3u8_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10.0
#EXT-X-MEDIA-SEQUENCE:0
"""
        for i in range(5):
            m3u8_content += f"#EXTINF:10.000,\n"
            m3u8_content += f"/vod/{vid}_{i:04d}.ts\n"
        m3u8_content += "#EXT-X-ENDLIST\n"
        
        self.send_response(200)
        self.send_header("Content-Type", "application/vnd.apple.mpegurl")
        self.send_header("Content-Length", str(len(m3u8_content.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(m3u8_content.encode("utf-8"))

    def _handle_ts(self, parsed):
        """
        处理 .ts 分片文件请求
        返回一个空的 TS 文件（用于测试，实际播放需要真实视频）
        """
        # 返回一个最小的 TS 文件（空的）
        # 注意：这不是一个有效的视频文件，仅用于测试 URL 是否可达
        ts_data = b'\x47' * 188  # 一个 TS 包（188字节，开头是0x47）
        
        self.send_response(200)
        self.send_header("Content-Type", "video/MP2T")
        self.send_header("Content-Length", str(len(ts_data)))
        self.end_headers()
        self.wfile.write(ts_data)

    def _send_html_response(self, status_code, html):
        """发送 HTML 响应"""
        response = html.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def _handle_list(self):
        """
        首页接口: GET /api.php?ac=list
        返回分类列表和推荐视频（每个分类取前5个）
        """
        all_vods = get_all_vods()

        # 每个分类取前5个作为首页推荐
        recommend_list = []
        for cat_vods in all_vods.values():
            recommend_list.extend(cat_vods[:5])

        # 随机打乱
        random.shuffle(recommend_list)

        result = {
            "class": CATEGORIES,
            "list": recommend_list[:10]
        }
        self._send_json_response(200, result)

    def _handle_category_list(self, params):
        """
        分类列表接口: GET /api.php?ac=detail&t={tid}&pg={pg}

        参数:
            t: 分类ID
            pg: 页码（可选，默认1）
        """
        tid = params.get("t", ["1"])[0]
        pg = int(params.get("pg", ["1"])[0])

        all_vods = get_all_vods()

        if tid not in all_vods:
            self._send_json_response(400, {"code": 400, "msg": "分类不存在"})
            return

        cat_vods = all_vods[tid]
        total = len(cat_vods)
        pagecount = (total + PAGE_SIZE - 1) // PAGE_SIZE

        # 计算分页
        start = (pg - 1) * PAGE_SIZE
        end = start + PAGE_SIZE
        page_list = cat_vods[start:end]

        result = {
            "page": pg,
            "pagecount": pagecount,
            "limit": PAGE_SIZE,
            "total": total,
            "list": page_list
        }
        self._send_json_response(200, result)

    def _handle_detail(self, params):
        """
        详情接口: GET /api.php?ac=detail&ids={vod_id}

        参数:
            ids: 视频ID，多个用逗号分隔
        """
        ids_str = params.get("ids", [""])[0]
        ids = ids_str.split(",")

        vod_by_id = get_vod_by_id()
        result_list = []

        for vid in ids:
            vid = vid.strip()
            if vid in vod_by_id:
                result_list.append(vod_by_id[vid])

        result = {
            "list": result_list
        }
        self._send_json_response(200, result)

    def _handle_search(self, params):
        """
        搜索接口: GET /api.php?ac=detail&wd={keyword}

        参数:
            wd: 搜索关键词
            pg: 页码（可选，默认1）
        """
        keyword = params.get("wd", [""])[0]
        pg = int(params.get("pg", ["1"])[0])

        vod_by_id = get_vod_by_id()

        # 搜索匹配（名称包含关键词）
        matched_vods = []
        for vod in vod_by_id.values():
            if keyword.lower() in vod["vod_name"].lower():
                matched_vods.append(vod)

        total = len(matched_vods)
        pagecount = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

        # 计算分页
        start = (pg - 1) * PAGE_SIZE
        end = start + PAGE_SIZE
        page_list = matched_vods[start:end]

        result = {
            "page": pg,
            "pagecount": pagecount,
            "limit": PAGE_SIZE,
            "total": total,
            "list": page_list
        }
        self._send_json_response(200, result)

    def _send_json_response(self, status_code, data):
        """
        发送 JSON 响应

        参数:
            status_code: HTTP 状态码
            data: 要返回的数据字典
        """
        response = json.dumps(data, ensure_ascii=False)
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))


# ==================== 服务器控制 ====================

_server_instance = None
_server_thread = None


def start_server(port=SERVER_PORT):
    """
    启动模拟 API 服务器（在后台线程运行）

    参数:
        port: 监听端口，默认 8899

    返回:
        启动成功返回 True，失败返回 False
    """
    global _server_instance, _server_thread

    if _server_instance is not None:
        print("[服务器] 服务器已在运行中")
        return False

    try:
        _server_instance = HTTPServer(("0.0.0.0", port), MockApiHandler)
        _server_thread = threading.Thread(target=_server_instance.serve_forever, daemon=True)
        _server_thread.start()
        print(f"[服务器] 模拟 API 服务器已启动，监听端口: {port}")
        return True
    except Exception as e:
        print(f"[服务器] 启动失败: {e}")
        _server_instance = None
        _server_thread = None
        return False


def stop_server():
    """
    停止模拟 API 服务器

    返回:
        停止成功返回 True，失败返回 False
    """
    global _server_instance, _server_thread

    if _server_instance is None:
        print("[服务器] 服务器未运行")
        return False

    try:
        _server_instance.shutdown()
        _server_instance.server_close()
        _server_instance = None
        _server_thread = None
        print("[服务器] 模拟 API 服务器已停止")
        return True
    except Exception as e:
        print(f"[服务器] 停止失败: {e}")
        return False


# ==================== 主函数 ====================

def main():
    """
    主函数：直接运行服务器
    """
    print("=" * 60)
    print("  苹果CMS 模拟 API 服务器")
    print(f"  监听端口: {SERVER_PORT}")
    print("=" * 60)
    print("  支持接口:")
    print(f"  1. 首页接口:    http://localhost:{SERVER_PORT}/api.php?ac=list")
    print(f"  2. 分类列表:    http://localhost:{SERVER_PORT}/api.php?ac=detail&t=1&pg=1")
    print(f"  3. 详情接口:    http://localhost:{SERVER_PORT}/api.php?ac=detail&ids=1")
    print(f"  4. 搜索接口:    http://localhost:{SERVER_PORT}/api.php?ac=detail&wd=流浪")
    print("=" * 60)
    print("  按 Ctrl+C 停止服务器")
    print("=" * 60)

    server = HTTPServer(("0.0.0.0", SERVER_PORT), MockApiHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[服务器] 收到停止信号，正在关闭...")
        server.shutdown()
        server.server_close()
        print("[服务器] 服务器已关闭")


if __name__ == "__main__":
    main()
