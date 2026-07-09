# -*- coding: utf-8 -*-
"""
SpiderParseParser - type=3 Spider 解析器

对应 TvBox 配置中 type=3 的解析源。
通过调用 Spider 爬虫的 playerContent 方法来解析视频地址。

在 TvBox 中，type=3 的解析源通常是自定义的 Spider 类，
通过 Jar 包加载，用 Java 代码实现复杂的解析逻辑。

在我们的学习项目中，简化实现为：
- 可以传入 Spider 实例
- 或者传入类名，通过工厂创建 Spider 实例
"""

from typing import Dict, List, Optional
from .base_parser import BaseParser


class SpiderParseParser(BaseParser):
    """Spider 解析器 (type=3)

    对应 TvBox 的 type=3 解析源。
    通过 Spider 爬虫来解析视频地址。

    适用场景：
    - 需要复杂逻辑才能解析的地址
    - 需要执行 JavaScript 或自定义算法的解析
    - 加密的视频地址需要解密

    工作原理：
    1. 获取或创建 Spider 实例
    2. 调用 Spider.playerContent(flag, id) 方法
    3. 从返回的 JSON 中提取播放地址
    """

    def __init__(self, spider_instance=None, flag: List[str] = None, ext: Dict = None):
        """初始化 SpiderParseParser

        参数:
            spider_instance: Spider 实例（可选）
            flag: 适用平台标识列表
            ext: 扩展参数
        """
        super().__init__(name="SpiderParseParser", priority=60)
        self.spider = spider_instance
        self.flag = flag or []
        self.ext = ext or {}

    def can_parse(self, url: str) -> bool:
        """判断是否能处理该 URL

        判断逻辑：
        1. 如果有 flag，检查 URL 是否匹配
        2. 如果没有 flag，万能解析
        3. 需要 Spider 实例可用

        参数:
            url: 待解析的地址
        """
        if not url:
            return False

        # 如果已经有 Spider 实例，可以直接解析
        if self.spider is not None:
            return True

        url_lower = url.lower()

        # 如果已经是直链
        if url_lower.endswith(('.m3u8', '.mp4', '.flv')):
            return False

        # 如果有 flag，检查是否匹配
        if self.flag:
            for f in self.flag:
                if f.lower() in url_lower:
                    return True
            return False

        return True

    def parse(self, url: str) -> Dict:
        """调用 Spider 解析视频地址

        步骤：
        1. 检查 Spider 实例是否可用
        2. 调用 Spider.playerContent() 方法
        3. 从返回的 JSON 中提取播放地址

        参数:
            url: 待解析的视频地址
        """
        if not url:
            return {"url": "", "success": False, "error": "URL 为空"}

        if self.spider is None:
            return {
                "url": "",
                "success": False,
                "error": "Spider 实例未设置，无法解析"
            }

        try:
            print(f"[SpiderParseParser] 调用 Spider 解析: {url[:80]}...")

            # 调用 Spider 的 playerContent 方法
            # 参数: playerContent(String flag, String id, List<String> vipFlags)
            # 在我们的简化实现中，flag 为空，id 为 URL
            result_json = self.spider.playerContent("", url, [])

            # 解析返回的 JSON
            import json
            result = json.loads(result_json)

            # 提取播放地址
            play_url = result.get("url", "")
            if not play_url:
                return {
                    "url": "",
                    "success": False,
                    "error": f"Spider 返回结果中未找到播放地址: {result_json[:200]}"
                }

            # 判断是否需要继续解析
            parse_flag = result.get("parse", 0)

            # 判断格式
            format_type = "unknown"
            if ".m3u8" in play_url.lower():
                format_type = "m3u8"
            elif ".mp4" in play_url.lower():
                format_type = "mp4"
            elif ".flv" in play_url.lower():
                format_type = "flv"

            return {
                "url": play_url,
                "title": result.get("title", ""),
                "pic": result.get("pic", ""),
                "format": format_type,
                "parse": parse_flag,
                "header": result.get("header", {}),
                "success": True,
                "error": ""
            }

        except json.JSONDecodeError as e:
            return {"url": "", "success": False, "error": f"Spider 返回 JSON 解析失败: {str(e)[:100]}"}
        except Exception as e:
            return {"url": "", "success": False, "error": f"Spider 解析失败: {str(e)[:100]}"}

    def set_spider(self, spider_instance):
        """设置 Spider 实例

        参数:
            spider_instance: Spider 实例
        """
        self.spider = spider_instance