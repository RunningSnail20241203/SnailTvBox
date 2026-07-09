# -*- coding: utf-8 -*-
"""
JsonApiParser - type=1 JSON 解析接口解析器

对应 TvBox 配置中 type=1 的解析源。
通过调用远程 JSON 解析 API，获取真实的视频播放地址。

配置示例：
{
    "name": "jx",
    "type": 1,
    "url": "https://jx.m3u8.tv/jx/jx.php?url=",
    "ext": {
        "flag": ["qq", "腾讯"]
    }
}

调用方式：
GET https://jx.m3u8.tv/jx/jx.php?url={视频地址}
返回 JSON: {"url": "真实地址", "code": 200}
"""

import requests
import json
import logging
from typing import Dict, List
from .base_parser import BaseParser

logger = logging.getLogger(__name__)


class JsonApiParser(BaseParser):
    """JSON 解析接口解析器 (type=1)

    对应 TvBox 的 type=1 解析源。
    调用远程 JSON API 接口获取真实播放地址。

    适用场景：
    - 有专门的解析 API 服务
    - 返回 JSON 格式的解析结果
    - 支持通过 URL 参数传入待解析的视频地址

    工作原理：
    1. 构造完整的 API URL（解析接口 + 视频地址参数）
    2. 发送 HTTP GET 请求
    3. 从 JSON 响应中提取真实播放地址
    """

    def __init__(self, api_url: str, flag: List[str] = None, ext: Dict = None, timeout: int = 15):
        """初始化 JsonApiParser

        参数:
            api_url: 解析接口地址（如 https://jx.example.com/?url=）
            flag: 适用平台标识列表
            ext: 扩展参数（如 header 配置）
            timeout: HTTP 请求超时时间（秒）
        """
        super().__init__(name="JsonApiParser", priority=50)
        self.api_url = api_url
        self.flag = flag or []
        self.ext = ext or {}
        self.timeout = timeout
        self._session = requests.Session()

        # 设置请求头
        headers = self.ext.get("header", {})
        if not headers:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json, text/javascript, */*",
            }
        self._session.headers.update(headers)

    def can_parse(self, url: str) -> bool:
        """判断是否能处理该 URL

        判断逻辑：
        1. 如果有 flag，检查 URL 是否匹配 flag
        2. 如果没有 flag，万能解析（对所有 URL 都尝试）

        参数:
            url: 待解析的地址
        """
        if not url:
            return False

        # 如果已经是直链，不需要 API 解析
        url_lower = url.lower()
        if url_lower.endswith(('.m3u8', '.mp4', '.flv')):
            return False

        # 如果有 flag，检查是否匹配
        if self.flag:
            for f in self.flag:
                if f.lower() in url_lower:
                    return True
            return False

        # 没有 flag，万能解析
        return True

    def parse(self, url: str) -> Dict:
        """调用 JSON 解析接口获取真实地址

        步骤：
        1. 构造完整 API URL
        2. 发送 GET 请求
        3. 从 JSON 中提取播放地址

        参数:
            url: 待解析的视频地址
        """
        if not url:
            logger.error("JsonApiParser.parse: URL 为空")
            return {"url": "", "success": False, "error": "URL 为空"}

        try:
            # 构造完整的 API URL
            full_url = self._build_api_url(url)
            logger.info("调用 JSON 解析接口: %s", full_url[:80])

            response = self._session.get(full_url, timeout=self.timeout)
            response.raise_for_status()
            logger.debug("响应: status=%s, length=%s", response.status_code, len(response.text))

            # 尝试解析 JSON
            try:
                data = response.json()
            except json.JSONDecodeError:
                # 可能返回的是 JSONP 格式（callback({...})）
                text = response.text.strip()
                logger.debug("响应非标准 JSON，尝试 JSONP 解析: %s", text[:100])
                if text.startswith('(') and text.endswith(')'):
                    text = text[1:-1]
                data = json.loads(text)

            # 从 JSON 中提取播放地址（支持多种格式）
            video_url = self._extract_url_from_json(data)

            if not video_url:
                logger.warning("JSON 响应中未找到播放地址: %s", str(data)[:200])
                return {
                    "url": "",
                    "success": False,
                    "error": f"JSON 响应中未找到播放地址，响应: {str(data)[:200]}"
                }

            logger.debug("提取到播放地址: %s", video_url)

            # 判断格式
            format_type = "unknown"
            if ".m3u8" in video_url.lower():
                format_type = "m3u8"
            elif ".mp4" in video_url.lower():
                format_type = "mp4"
            elif ".flv" in video_url.lower():
                format_type = "flv"

            return {
                "url": video_url,
                "title": data.get("title", ""),
                "pic": data.get("pic", data.get("img", "")),
                "format": format_type,
                "parse": 0,
                "header": {},
                "success": True,
                "error": ""
            }

        except requests.exceptions.Timeout:
            logger.error("请求超时（%s秒）: %s", self.timeout, full_url[:80], exc_info=True)
            return {"url": "", "success": False, "error": f"请求超时（{self.timeout}秒）"}
        except requests.exceptions.ConnectionError as e:
            logger.error("连接失败: %s, url=%s", e, full_url[:80], exc_info=True)
            return {"url": "", "success": False, "error": f"连接失败: {str(e)[:100]}"}
        except json.JSONDecodeError as e:
            logger.error("JSON 解析失败: %s, url=%s", e, full_url[:80], exc_info=True)
            return {"url": "", "success": False, "error": f"JSON 解析失败: {str(e)[:100]}"}
        except Exception as e:
            logger.error("解析失败: %s, url=%s", e, full_url[:80], exc_info=True)
            return {"url": "", "success": False, "error": f"解析失败: {str(e)[:100]}"}

    def _build_api_url(self, video_url: str) -> str:
        """构造完整的 API URL

        根据 api_url 的格式拼接视频地址参数。
        支持两种格式：
        - https://jx.example.com/?url=  → 直接拼接
        - https://jx.example.com/api    → 添加 ?url= 参数

        参数:
            video_url: 待解析的视频地址
        """
        api = self.api_url

        # 如果 api_url 已经包含参数占位符或末尾有 =，直接拼接
        if api.endswith('=') or '?' in api:
            return api + video_url

        # 否则添加 ?url= 参数
        connector = '&' if '?' in api else '?'
        return f"{api}{connector}url={requests.utils.quote(video_url)}"

    def _extract_url_from_json(self, data: Dict) -> str:
        """从 JSON 响应中提取播放地址

        支持多种 JSON 格式：
        - {"url": "xxx"}
        - {"data": {"url": "xxx"}}
        - {"result": {"video": "xxx"}}
        - {"play": "xxx"}
        - {"src": "xxx"}

        参数:
            data: JSON 响应数据

        返回:
            播放地址，未找到返回空字符串
        """
        if not isinstance(data, dict):
            return ""

        # 尝试各种可能的字段名
        url_keys = ["url", "play", "src", "video", "m3u8", "mp4", "link", "address"]

        # 顶层查找
        for key in url_keys:
            if key in data and isinstance(data[key], str) and data[key]:
                return data[key]

        # 嵌套查找（data/result/video 等）
        nested_keys = ["data", "result", "body", "info", "video"]
        for nested in nested_keys:
            if nested in data and isinstance(data[nested], dict):
                nested_data = data[nested]
                for key in url_keys:
                    if key in nested_data and isinstance(nested_data[key], str) and nested_data[key]:
                        return nested_data[key]

        return ""