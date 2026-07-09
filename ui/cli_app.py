# -*- coding: utf-8 -*-
"""
命令行交互界面模块
CliApp 提供完整的命令行导航界面，支持视频源选择、分类浏览、视频详情等功能
"""

import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_loader import ConfigLoader
from spiders.mock_spider import MockSpider
from spiders.json_spider import JsonSpider
from models.vod_info import VodInfo
from parsers import ParserManager, DirectParser, JsVariableParser
from utils.parses_loader import ParsesLoader
from player import VideoPlayer

logger = logging.getLogger(__name__)


class CliApp:
    """
    命令行应用主类
    使用栈来管理页面导航，每个页面是一个方法，返回后弹出栈
    """

    def __init__(self, config_path=None):
        """
        初始化 CliApp

        参数:
            config_path: 配置文件路径或 URL，默认使用 fty.json
        """
        self.config_loader = ConfigLoader()
        self.page_stack = []
        self.current_source = None
        self.current_spider = None
        self.home_data = None
        self.category_list = []
        self.recommend_list = []
        self.current_tid = None
        self.current_type_name = ""
        self.current_page = 1
        self.category_data = None
        self.current_vod = None
        self.play_list = []
        self.current_line = None

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        default_config = os.path.join(base_dir, "fty.json")
        self.config_path = config_path if config_path else default_config

        # 初始化解析器管理器
        self.parser_manager = ParserManager()
        self.parser_manager.register(DirectParser())
        self.parser_manager.register(JsVariableParser())

        # 初始化播放器
        self.video_player = VideoPlayer()

    def run(self):
        """启动应用，加载配置并进入首页"""
        print("=" * 60)
        print("TvBox Learn - 命令行演示")
        print("=" * 60)

        if not self._load_config():
            print("\n配置加载失败，程序退出。")
            return

        # 加载配置文件中的 parses 解析源
        try:
            ParsesLoader.load_from_config(self.config_loader, self.parser_manager)
        except Exception as e:
            logger.error("ParsesLoader 加载解析源失败: %s", e, exc_info=True)
            print(f"\n[ParsesLoader] 加载解析源失败: {e}")

        self.page_stack.append(self._page_source_list)
        self._run_page_loop()

    def _load_config(self):
        """
        加载配置文件

        返回:
            bool: 是否加载成功
        """
        path = self.config_path
        if path.startswith("http://") or path.startswith("https://"):
            return self.config_loader.load_from_url(path)
        else:
            return self.config_loader.load_from_file(path)

    def _run_page_loop(self):
        """页面循环，不断执行栈顶的页面方法"""
        while self.page_stack:
            current_page = self.page_stack[-1]
            result = current_page()
            if result == "pop":
                self.page_stack.pop()
            elif result == "quit":
                break
            elif callable(result):
                self.page_stack.append(result)
            # None 表示继续当前页面

    def _print_separator(self, title=""):
        """
        打印分隔线

        参数:
            title: 可选标题文字
        """
        if title:
            line_len = max(60 - len(title) - 2, 0)
            left = line_len // 2
            right = line_len - left
            print("\n" + "=" * left + f" {title} " + "=" * right)
        else:
            print("\n" + "=" * 60)

    def _input(self, prompt="请输入: "):
        """
        统一的输入处理

        参数:
            prompt: 提示文字

        返回:
            str: 用户输入（去除首尾空白）
        """
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return "q"

    # ============================================================
    # 页面1：视频源列表页（首页）
    # ============================================================
    def _page_source_list(self):
        """
        视频源列表页（首页）
        显示所有视频源的编号、名称、类型
        选择后进入该视频源的首页
        """
        self._print_separator("视频源列表")

        sites = self.config_loader.sites
        if not sites:
            print("没有可用的视频源。")
            return "quit"

        print(f"共 {len(sites)} 个视频源：")
        print("-" * 60)
        for i, site in enumerate(sites):
            print(f"  [{i + 1:2d}] {site.name}  ({site.get_type_name()})")

        print("-" * 60)
        print("提示：输入编号选择视频源，输入 q 退出")

        user_input = self._input()

        if user_input.lower() == "q":
            print("\n再见！")
            return "quit"

        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(sites):
                self.current_source = sites[idx]
                self.current_spider = self._create_spider(self.current_source)
                return self._page_source_home
            else:
                print("\n无效输入，请重试。")
                return None
        else:
            print("\n无效输入，请重试。")
            return None

    def _create_spider(self, source):
        """
        根据视频源类型创建对应的爬虫实例

        参数:
            source: SourceBean 视频源对象

        返回:
            BaseSpider: 爬虫实例
        """
        logger.info("创建爬虫: key=%s, name=%s, type=%s, api=%s",
                    source.key, source.name, source.type, source.api)
        if source.type == 1:
            spider = JsonSpider(source.api)
            spider.init(None, source.ext)
            return spider
        else:
            spider = MockSpider()
            spider.init(None, source.ext)
            return spider

    # ============================================================
    # 页面2：视频源首页
    # ============================================================
    def _page_source_home(self):
        """
        视频源首页
        显示分类列表和首页推荐视频
        """
        if not self.home_data:
            self.home_data = self.current_spider.home_content()
            self.category_list = self.home_data.get("class", [])
            self.recommend_list = self.home_data.get("list", [])

        self._print_separator(f"{self.current_source.name}")
        if isinstance(self.current_spider, JsonSpider):
            print("[JSON接口源]")
        else:
            print("[演示模式：使用Mock数据]")
        print("-" * 60)

        print("【分类列表】")
        for i, cat in enumerate(self.category_list):
            print(f"  [{i + 1}] {cat['type_name']}")

        print()
        print("【首页推荐】")
        rec_start = len(self.category_list) + 1
        for i, vod in enumerate(self.recommend_list):
            num = rec_start + i
            print(f"  [{num:2d}] {vod['vod_name']}  [{vod['vod_remarks']}]")

        print("-" * 60)
        print("提示：输入编号选择，0 返回，q 退出")

        user_input = self._input()

        if user_input.lower() == "q":
            print("\n再见！")
            return "quit"

        if user_input == "0":
            self.home_data = None
            self.category_list = []
            self.recommend_list = []
            return "pop"

        if user_input.isdigit():
            num = int(user_input)
            cat_count = len(self.category_list)
            rec_count = len(self.recommend_list)

            if 1 <= num <= cat_count:
                cat = self.category_list[num - 1]
                self.current_tid = cat["type_id"]
                self.current_type_name = cat["type_name"]
                self.current_page = 1
                self.category_data = None
                return self._page_category_list
            elif cat_count < num <= cat_count + rec_count:
                vod_idx = num - cat_count - 1
                vod = self.recommend_list[vod_idx]
                self._load_vod_detail(vod["vod_id"])
                return self._page_vod_detail
            else:
                print("\n无效输入，请重试。")
                return None
        else:
            print("\n无效输入，请重试。")
            return None

    # ============================================================
    # 页面3：分类视频列表页
    # ============================================================
    def _page_category_list(self):
        """
        分类视频列表页
        显示本页视频列表，支持翻页
        """
        if not self.category_data or self.category_data.get("page") != self.current_page:
            self.category_data = self.current_spider.category_content(
                self.current_tid, str(self.current_page)
            )

        page = self.category_data.get("page", 1)
        pagecount = self.category_data.get("pagecount", 0)
        total = self.category_data.get("total", 0)
        vod_list = self.category_data.get("list", [])

        self._print_separator(f"{self.current_type_name}")
        print(f"第 {page} 页 / 共 {pagecount} 页  (共 {total} 个视频)")
        print("-" * 60)

        for i, vod in enumerate(vod_list):
            print(f"  [{i + 1:2d}] {vod['vod_name']}  [{vod['vod_remarks']}]")

        print("-" * 60)
        print("提示：输入编号看详情，n 下一页，p 上一页，0 返回，q 退出")

        user_input = self._input()

        if user_input.lower() == "q":
            print("\n再见！")
            return "quit"

        if user_input == "0":
            self.category_data = None
            return "pop"

        if user_input.lower() == "n":
            if self.current_page < pagecount:
                self.current_page += 1
                self.category_data = None
            else:
                print("\n已经是最后一页了。")
            return None

        if user_input.lower() == "p":
            if self.current_page > 1:
                self.current_page -= 1
                self.category_data = None
            else:
                print("\n已经是第一页了。")
            return None

        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(vod_list):
                vod = vod_list[idx]
                self._load_vod_detail(vod["vod_id"])
                return self._page_vod_detail
            else:
                print("\n无效输入，请重试。")
                return None
        else:
            print("\n无效输入，请重试。")
            return None

    # ============================================================
    # 页面4：视频详情页
    # ============================================================
    def _page_vod_detail(self):
        """
        视频详情页
        显示视频详细信息和播放线路
        """
        if not self.current_vod:
            return "pop"

        vod = self.current_vod

        self._print_separator(f"{vod.vod_name}")
        print(f"年份：{vod.vod_year}")
        print(f"地区：{vod.vod_area}")
        print(f"导演：{vod.vod_director}")
        print(f"主演：{vod.vod_actor}")
        print(f"状态：{vod.vod_remarks}")
        print("-" * 60)
        print("【简介】")
        content = vod.vod_content
        if len(content) > 200:
            content = content[:200] + "..."
        print(content)
        print("-" * 60)

        self.play_list = vod.parse_play_list()
        print("【播放线路】")
        for i, line in enumerate(self.play_list):
            ep_count = len(line["episodes"])
            print(f"  [{i + 1}] {line['from']}  ({ep_count}集)")

        print("-" * 60)
        print("提示：输入线路编号查看剧集，0 返回，q 退出")

        user_input = self._input()

        if user_input.lower() == "q":
            print("\n再见！")
            return "quit"

        if user_input == "0":
            self.current_vod = None
            self.play_list = []
            self.current_line = None
            return "pop"

        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(self.play_list):
                self.current_line = self.play_list[idx]
                return self._page_episode_list
            else:
                print("\n无效输入，请重试。")
                return None
        else:
            print("\n无效输入，请重试。")
            return None

    def _page_episode_list(self):
        """
        剧集列表页
        显示当前线路的剧集列表，选择后播放
        """
        if not self.current_line:
            return "pop"

        line = self.current_line
        episodes = line["episodes"]
        ep_count = len(episodes)

        self._print_separator(f"{line['from']} - 剧集列表")
        print(f"共 {ep_count} 集")
        print("-" * 60)

        # 显示剧集（最多显示50个，太多了分页显示）
        display_count = min(ep_count, 50)
        for i in range(display_count):
            ep = episodes[i]
            print(f"  [{i + 1:2d}] {ep['name']}")

        if ep_count > 50:
            print(f"  ... 共 {ep_count} 集 (显示前50集)")

        print("-" * 60)
        print("提示：输入集数播放，0 返回，q 退出")

        user_input = self._input()

        if user_input.lower() == "q":
            print("\n再见！")
            return "quit"

        if user_input == "0":
            return "pop"

        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < ep_count:
                ep = episodes[idx]
                self._play_episode(ep)
                return None  # 播放后留在当前页面
            else:
                print("\n无效输入，请重试。")
                return None
        else:
            print("\n无效输入，请重试。")
            return None

    def _play_episode(self, episode):
        """
        播放指定剧集

        流程：
        1. 获取剧集地址
        2. 调用解析器解析真实播放地址
        3. 调用播放器播放

        参数:
            episode: 集数字典 {"name": "第1集", "url": "xxx"}
        """
        url = episode["url"]
        name = episode["name"]

        logger.info("播放剧集: name=%r, url=%r", name, url)

        print(f"\n{'=' * 60}")
        print(f"正在播放: {name}")
        print(f"原始地址: {url}")
        print("-" * 60)

        # 步骤1：解析播放地址
        if not url:
            logger.warning("剧集 URL 为空! name=%r, 即将调用解析器解析空 URL", name)

        print("正在解析播放地址...")
        logger.debug("调用 parser_manager.parse: url=%r", url)
        result = self.parser_manager.parse(url)
        logger.debug("解析结果: success=%s, url=%s",
                     result.get("success"), str(result.get("url", ""))[:80])

        if not result.get("success", False):
            print(f"❌ 解析失败: {result.get('error', '未知错误')}")
            print("-" * 60)
            self._input("按回车继续...")
            return

        real_url = result["url"]
        print(f"✅ 解析成功!")
        print(f"真实地址: {real_url[:80]}...")
        print(f"格式: {result.get('format', 'unknown')}")
        if result.get("title"):
            print(f"标题: {result['title']}")

        # 步骤2：检测播放器
        print("\n正在检测播放器...")
        players = self.video_player.detect_players()
        if not players:
            print("❌ 未检测到可用播放器")
            print(self.video_player.get_install_hint())
            print("-" * 60)
            self._input("按回车继续...")
            return

        print(f"✅ 检测到 {len(players)} 个播放器:")
        for p in players:
            print(f"   - {p['name']}")

        # 步骤3：播放
        print("\n正在启动播放器...")
        logger.info("调用播放器播放: real_url=%s", real_url[:80])
        play_result = self.video_player.play(real_url)

        if play_result["success"]:
            print(f"\n🎉 {play_result['player']} 播放器已启动！")
            print("   视频正在播放中...")
            print("   （关闭播放器窗口后，可以回到这里继续操作）")
        else:
            print(f"\n❌ 播放失败: {play_result['error']}")

        print("=" * 60)
        self._input("按回车继续...")

    def _load_vod_detail(self, vod_id):
        """
        加载视频详情

        参数:
            vod_id: 视频ID
        """
        logger.info("加载视频详情: vod_id=%s", vod_id)
        detail_data = self.current_spider.detail_content([vod_id])
        if detail_data.get("list"):
            vod_dict = detail_data["list"][0]
            vod = VodInfo()
            vod.vod_id = vod_dict.get("vod_id", "")
            vod.vod_name = vod_dict.get("vod_name", "")
            vod.vod_pic = vod_dict.get("vod_pic", "")
            vod.vod_remarks = vod_dict.get("vod_remarks", "")
            vod.vod_year = vod_dict.get("vod_year", "")
            vod.vod_area = vod_dict.get("vod_area", "")
            vod.vod_director = vod_dict.get("vod_director", "")
            vod.vod_actor = vod_dict.get("vod_actor", "")
            vod.vod_content = vod_dict.get("vod_content", "")
            vod.vod_play_from = vod_dict.get("vod_play_from", "")
            vod.vod_play_url = vod_dict.get("vod_play_url", "")
            self.current_vod = vod
            logger.debug("视频详情加载完成: name=%s, 线路数=%d",
                         vod.vod_name, vod.get_line_count())
        else:
            logger.warning("视频详情为空: vod_id=%s", vod_id)
            self.current_vod = None


def main():
    """命令行入口函数"""
    config_path = None
    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    app = CliApp(config_path)
    app.run()


if __name__ == "__main__":
    main()
