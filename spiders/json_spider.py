# -*- coding: utf-8 -*-
"""
JSON 接口爬虫模块（type=1）
对接苹果CMS、海洋CMS等返回标准JSON格式的视频站点
"""

import requests
import json
import re
from .base_spider import BaseSpider


class JsonSpider(BaseSpider):
    """JSON接口爬虫（type=1）

    对接苹果CMS、海洋CMS等返回标准JSON格式的视频站点。
    通过 HTTP 请求获取 JSON 数据，并转换为 TvBox 标准格式。

    支持的接口:
        - home_content: 首页分类+推荐
        - category_content: 分类视频列表
        - detail_content: 视频详情
        - search_content: 搜索视频
        - player_content: 播放地址（详情中已包含，直接返回空结构）
    """

    def __init__(self, api_url=""):
        """
        初始化 JsonSpider

        参数:
            api_url (str): API 基础地址，例如 "http://example.com/api.php"
        """
        super().__init__()

        self.api_url = api_url
        self.timeout = 10

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

    def init(self, context, extend=""):
        """
        初始化爬虫

        可以从 extend 参数中提取额外配置，例如自定义超时、User-Agent 等。

        参数:
            context: 上下文对象，TvBox 传入的上下文环境
            extend (str): 扩展参数，对应视频源配置中的 ext 字段
        """
        pass

    def _get(self, url, params=None):
        """
        发送 GET 请求，返回解析后的 JSON dict

        参数:
            url (str): 请求 URL
            params (dict): 查询参数

        返回:
            dict: 解析后的 JSON 数据，失败返回 None
        """
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)

            resp.encoding = resp.apparent_encoding

            text = resp.text.strip()

            return self._parse_json(text)
        except requests.exceptions.Timeout:
            print(f"[JsonSpider] 请求超时: {url}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"[JsonSpider] 连接失败: {url}")
            return None
        except Exception as e:
            print(f"[JsonSpider] 请求失败: {e}, URL: {url}")
            return None

    def _parse_json(self, text):
        """
        解析 JSON，兼容 JSONP 格式

        尝试多种方式解析：
        1. 直接解析为 JSON
        2. 匹配 JSONP 格式 callback({...}) 并提取 JSON 部分

        参数:
            text (str): 响应文本

        返回:
            dict: 解析后的 JSON 数据，失败返回 None
        """
        if not text:
            print("[JsonSpider] JSON 解析失败: 响应为空")
            return None

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        match = re.search(r'\w*\((\{.*\})\)\w*$', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        print(f"[JsonSpider] JSON 解析失败，响应前200字: {text[:200]}")
        return None

    def _extract_vod_brief(self, item):
        """
        从 API 返回的视频数据中提取简要信息（用于列表展示）

        参数:
            item (dict): API 返回的单条视频数据

        返回:
            dict: TvBox 标准格式的视频简要信息
        """
        return {
            "vod_id": str(item.get("vod_id", "")),
            "vod_name": str(item.get("vod_name", "")),
            "vod_pic": str(item.get("vod_pic", "")),
            "vod_remarks": str(item.get("vod_remarks", "")),
        }

    def _extract_vod_detail(self, item):
        """
        从 API 返回的视频数据中提取详细信息

        参数:
            item (dict): API 返回的单条视频数据

        返回:
            dict: TvBox 标准格式的视频详情
        """
        return {
            "vod_id": str(item.get("vod_id", "")),
            "vod_name": str(item.get("vod_name", "")),
            "vod_pic": str(item.get("vod_pic", "")),
            "vod_content": str(item.get("vod_content", "")),
            "vod_director": str(item.get("vod_director", "")),
            "vod_actor": str(item.get("vod_actor", "")),
            "vod_year": str(item.get("vod_year", "")),
            "vod_area": str(item.get("vod_area", "")),
            "vod_remarks": str(item.get("vod_remarks", "")),
            "vod_play_from": str(item.get("vod_play_from", "")),
            "vod_play_url": str(item.get("vod_play_url", "")),
        }

    def home_content(self, filter=False):
        """
        获取首页内容

        请求 {api}?ac=list，返回分类列表和推荐视频。

        参数:
            filter (bool): 是否启用筛选功能，默认 False

        返回:
            dict: 首页内容数据，包含 class 和 list
        """
        result = {
            "class": [],
            "list": []
        }

        if not self.api_url:
            return result

        data = self._get(self.api_url, params={"ac": "list"})
        if not data:
            return result

        if "class" in data and isinstance(data["class"], list):
            result["class"] = []
            for cat in data["class"]:
                if isinstance(cat, dict):
                    result["class"].append({
                        "type_id": str(cat.get("type_id", "")),
                        "type_name": str(cat.get("type_name", ""))
                    })

        if "list" in data and isinstance(data["list"], list):
            result["list"] = []
            for item in data["list"]:
                if isinstance(item, dict):
                    result["list"].append(self._extract_vod_brief(item))

        return result

    def category_content(self, tid, pg, filter=False, extend=None):
        """
        获取分类视频列表

        请求 {api}?ac=detail&t={tid}&pg={pg}，返回该分类下的视频列表。

        参数:
            tid (str): 分类ID，对应 type_id
            pg (str): 页码，从1开始
            filter (bool): 是否启用筛选，默认 False
            extend (dict): 扩展筛选参数，默认为 None

        返回:
            dict: 分类视频列表数据
        """
        page = int(pg) if pg else 1

        result = {
            "page": page,
            "pagecount": 0,
            "limit": 20,
            "total": 0,
            "list": []
        }

        if not self.api_url:
            return result

        params = {
            "ac": "detail",
            "t": tid,
            "pg": page
        }

        data = self._get(self.api_url, params=params)
        if not data:
            return result

        if "page" in data:
            try:
                result["page"] = int(data["page"])
            except (ValueError, TypeError):
                pass

        if "pagecount" in data:
            try:
                result["pagecount"] = int(data["pagecount"])
            except (ValueError, TypeError):
                pass

        if "limit" in data:
            try:
                result["limit"] = int(data["limit"])
            except (ValueError, TypeError):
                pass

        if "total" in data:
            try:
                result["total"] = int(data["total"])
            except (ValueError, TypeError):
                pass

        if "list" in data and isinstance(data["list"], list):
            for item in data["list"]:
                if isinstance(item, dict):
                    result["list"].append(self._extract_vod_brief(item))

        return result

    def detail_content(self, ids):
        """
        获取视频详情

        请求 {api}?ac=detail&ids={逗号分隔的ids}，返回视频详细信息。

        参数:
            ids (list): 视频ID列表，例如 ["movie_1", "movie_2"]

        返回:
            dict: 视频详情数据
        """
        result = {
            "list": []
        }

        if not self.api_url or not ids:
            return result

        ids_str = ",".join([str(x) for x in ids])

        params = {
            "ac": "detail",
            "ids": ids_str
        }

        data = self._get(self.api_url, params=params)
        if not data:
            return result

        if "list" in data and isinstance(data["list"], list):
            for item in data["list"]:
                if isinstance(item, dict):
                    result["list"].append(self._extract_vod_detail(item))

        return result

    def search_content(self, key, quick=False, pg="1"):
        """
        搜索视频

        请求 {api}?ac=detail&wd={key}&pg={pg}，返回搜索结果。

        参数:
            key (str): 搜索关键词
            quick (bool): 是否快速搜索，默认 False
            pg (str): 页码，默认 "1"

        返回:
            dict: 搜索结果数据
        """
        page = int(pg) if pg else 1

        result = {
            "page": page,
            "pagecount": 0,
            "limit": 20,
            "total": 0,
            "list": []
        }

        if not self.api_url or not key:
            return result

        params = {
            "ac": "detail",
            "wd": key,
            "pg": page
        }

        data = self._get(self.api_url, params=params)
        if not data:
            return result

        if "page" in data:
            try:
                result["page"] = int(data["page"])
            except (ValueError, TypeError):
                pass

        if "pagecount" in data:
            try:
                result["pagecount"] = int(data["pagecount"])
            except (ValueError, TypeError):
                pass

        if "limit" in data:
            try:
                result["limit"] = int(data["limit"])
            except (ValueError, TypeError):
                pass

        if "total" in data:
            try:
                result["total"] = int(data["total"])
            except (ValueError, TypeError):
                pass

        if "list" in data and isinstance(data["list"], list):
            for item in data["list"]:
                if isinstance(item, dict):
                    result["list"].append(self._extract_vod_brief(item))

        return result

    def player_content(self, flag, id, vip_flags=None):
        """
        获取播放地址

        type=1 的数据源通常在 detail_content 中就已经返回了播放地址列表，
        所以 player_content 不需要额外请求，直接返回空结构即可。

        为了接口一致性，仍保留此方法。

        参数:
            flag (str): 播放线路标识，对应 vod_play_from 中的线路名称
            id (str): 视频ID
            vip_flags (list): VIP 线路标识列表，默认为 None

        返回:
            dict: 播放地址数据
        """
        return {
            "url": "",
            "parse": 0,
            "jx": 0
        }
