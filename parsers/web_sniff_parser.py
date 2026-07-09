# -*- coding: utf-8 -*-
"""
WebSniffParser - type=0 WebView 嗅探/HTTP 解析器

对应 TvBox 配置中 type=0 的解析源。
通过请求目标页面 HTML，用正则提取视频播放地址。

这是 WebView 嗅探的简化版：
- 真实 TvBox 用 WebView 加载页面并监听网络请求来捕获视频地址
- 我们用 requests 请求页面 + 正则提取来模拟这个过程
"""

import re
import requests
from typing import Dict, List, Optional
from urllib.parse import urljoin
from .base_parser import BaseParser


class WebSniffParser(BaseParser):
    """WebView 嗅探简化版解析器 (type=0)

    对应 TvBox 的 type=0 解析源。
    通过请求页面 HTML，提取其中嵌入的视频地址。

    适用场景：
    - 视频平台页面（腾讯视频、爱奇艺等）
    - 播放地址嵌在页面 JS 变量或 HTML 标签中
    - 页面需要加载后才能拿到真实地址

    工作原理（模拟 WebView 嗅探）：
    1. 请求目标页面 HTML
    2. 从 HTML 中提取视频地址（正则匹配）
    3. 支持多种提取模式：JS变量、video标签、iframe等
    """

    # 匹配视频地址的正则模式
    URL_PATTERNS = [
        # JS 变量中的地址
        re.compile(r'(?:const|var|let)\s+(?:url|playUrl|videoUrl|src)\s*=\s*["\']([^"\']+\.(?:m3u8|mp4|flv))["\']', re.I),
        # HTML video 标签
        re.compile(r'<video[^>]+src=["\']([^"\']+\.(?:m3u8|mp4|flv))["\']', re.I),
        # HTML source 标签
        re.compile(r'<source[^>]+src=["\']([^"\']+\.(?:m3u8|mp4|flv))["\']', re.I),
        # iframe 中的视频地址
        re.compile(r'<iframe[^>]+src=["\']([^"\']+)["\']', re.I),
        # 通用的 m3u8/mp4 链接
        re.compile(r'["\']([^"\']+\.(?:m3u8|mp4|flv)(?:\?[^"\']*)?)["\']', re.I),
    ]

    def __init__(self, flag: List[str] = None, ext: Dict = None, timeout: int = 15):
        """初始化 WebSniffParser

        参数:
            flag: 适用平台标识列表（如 ["qq", "腾讯", "iqiyi"]）
            ext: 扩展参数（如 header 配置）
            timeout: HTTP 请求超时时间（秒）
        """
        super().__init__(name="WebSniffParser", priority=40)
        self.flag = flag or []
        self.ext = ext or {}
        self.timeout = timeout
        self._session = requests.Session()

        # 设置请求头
        headers = self.ext.get("header", {})
        if not headers:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        self._session.headers.update(headers)

    def can_parse(self, url: str) -> bool:
        """判断是否能处理该 URL

        判断逻辑：
        1. 如果有 flag，检查 URL 是否匹配 flag 中的平台标识
        2. 如果没有 flag，则对所有 URL 都尝试解析（万能解析）
        3. URL 本身不是直链（不是 .m3u8/.mp4）

        参数:
            url: 待解析的地址
        """
        if not url:
            return False

        url_lower = url.lower()

        # 如果已经是直链，不需要 WebSniff
        if url_lower.endswith(('.m3u8', '.mp4', '.flv')):
            return False

        # 如果有 flag，检查是否匹配
        if self.flag:
            for f in self.flag:
                if f.lower() in url_lower:
                    return True
            return False

        # 没有 flag，对所有非直链 URL 都尝试
        return True

    def parse(self, url: str) -> Dict:
        """解析播放地址

        步骤：
        1. 请求目标页面
        2. 用正则提取视频地址
        3. 补全相对路径
        4. 返回结果

        参数:
            url: 视频页面地址
        """
        if not url:
            return {"url": "", "success": False, "error": "URL 为空"}

        try:
            print(f"[WebSniffParser] 请求页面: {url[:80]}...")
            response = self._session.get(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'
            html = response.text

            # 尝试多种模式提取视频地址
            video_url = self._extract_video_url(html, url)

            if not video_url:
                return {
                    "url": "",
                    "success": False,
                    "error": "未能在页面中找到视频地址"
                }

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
                "title": "",
                "pic": "",
                "format": format_type,
                "parse": 0,
                "header": {},
                "success": True,
                "error": ""
            }

        except requests.exceptions.Timeout:
            return {"url": "", "success": False, "error": f"请求超时（{self.timeout}秒）"}
        except requests.exceptions.ConnectionError as e:
            return {"url": "", "success": False, "error": f"连接失败: {str(e)[:100]}"}
        except requests.exceptions.HTTPError as e:
            return {"url": "", "success": False, "error": f"HTTP错误: {e.response.status_code}"}
        except Exception as e:
            return {"url": "", "success": False, "error": f"解析失败: {str(e)[:100]}"}

    def _extract_video_url(self, html: str, base_url: str) -> Optional[str]:
        """从 HTML 中提取视频地址

        按优先级尝试多种正则模式，直到找到一个有效地址。

        参数:
            html: 页面 HTML 内容
            base_url: 页面 URL，用于补全相对路径

        返回:
            视频地址，未找到返回 None
        """
        for i, pattern in enumerate(self.URL_PATTERNS):
            matches = pattern.findall(html)
            for match in matches:
                url = match if isinstance(match, str) else match[0]
                if not url:
                    continue

                # 补全相对路径
                if url.startswith('//'):
                    url = 'https:' + url
                elif url.startswith('/'):
                    parsed = __import__('urllib.parse').parse.urlparse(base_url)
                    url = f"{parsed.scheme}://{parsed.netloc}{url}"
                elif not url.startswith('http'):
                    url = urljoin(base_url, url)

                # 过滤掉明显不是视频地址的（如 .jpg、.png）
                lower = url.lower()
                if any(lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.css', '.js']):
                    continue

                return url

        return None