# -*- coding: utf-8 -*-
"""
JS变量解析器

从 HTML 页面的嵌入式 JS 变量中提取播放地址。
参考 TvBox 对 phimgood 等视频分享网站的处理方式。

示例页面结构：
<script>
    const vid = "fe53ff5f33342773a12c81d85fb0a090";
    const url = "/20260709/28754_fe53ff5f/index.m3u8?sign=xxx";
    const pic = "/20260709/28754_fe53ff5f/1.jpg";
</script>
"""

import re
import requests
import logging
from typing import Dict, Optional
from urllib.parse import urljoin, urlparse
from .base_parser import BaseParser

logger = logging.getLogger(__name__)


class JsVariableParser(BaseParser):
    """JS变量解析器
    
    从 HTML 页面的嵌入式 JS 变量中提取播放地址。
    
    适用场景：
    - 视频分享页面（如 phimgood.com/share/xxx）
    - 播放地址嵌入在页面 JS 变量中的网站
    
    工作原理：
    1. 请求页面 HTML
    2. 用正则匹配 JS 变量（如 const url = "xxx"）
    3. 提取 url、vid、pic 等变量值
    4. 补全相对路径为完整 URL
    
    参考 TvBox 的设计：
    - 不执行任意 JS，只提取已知格式的变量
    - 安全性高，避免 XSS 风险
    """
    
    # 匹配 JS 变量的正则表达式
    # 支持: const url = "xxx", var url = 'xxx', let url = "xxx"
    # 变量名支持: url, playUrl, videoUrl, play_url, video_url 等
    URL_PATTERN = re.compile(
        r'(?:const|var|let)\s+'
        r'(?:url|playUrl|videoUrl|play_url|video_url|videoSrc|play_src)\s*'
        r'=\s*'
        r'["\']([^"\']+)["\']',
        re.IGNORECASE
    )
    
    # 匹配视频ID的正则
    VID_PATTERN = re.compile(
        r'(?:const|var|let)\s+vid\s*=\s*["\']([^"\']+)["\']',
        re.IGNORECASE
    )
    
    # 匹配封面图的正则
    PIC_PATTERN = re.compile(
        r'(?:const|var|let)\s+(?:pic|img|cover|thumbnail)\s*=\s*["\']([^"\']+)["\']',
        re.IGNORECASE
    )
    
    # 支持的域名（用于 can_parse 判断）
    SUPPORTED_DOMAINS = [
        'phimgood.com',
        'phimmoi',
        'phim',
        # 可以继续添加支持的网站
    ]
    
    def __init__(self, timeout: int = 10):
        """初始化JS变量解析器
        
        参数：
            timeout: HTTP请求超时时间（秒）
        """
        super().__init__(name="JsVariableParser", priority=30)
        self.timeout = timeout
        self._session = requests.Session()
        # 设置合理的请求头
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })
    
    def can_parse(self, url: str) -> bool:
        """判断是否是支持的分享页
        
        判断逻辑：
        1. URL 包含 "share" 路径（常见的分享页特征）
        2. 或者 URL 域名在支持列表中
        
        参数：
            url: 待判断的地址
            
        返回：
            True 表示可能可以解析
        """
        if not url:
            return False

        url_lower = url.lower()

        # 检查是否包含 share 路径
        if '/share/' in url_lower:
            logger.debug("JsVariableParser.can_parse(%s) = True (含 /share/)", url[:80])
            return True

        # 检查域名是否在支持列表中
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        for supported in self.SUPPORTED_DOMAINS:
            if supported in domain:
                logger.debug("JsVariableParser.can_parse(%s) = True (域名匹配 %s)", url[:80], supported)
                return True

        return False
    
    def parse(self, url: str) -> Dict:
        """解析分享页，提取播放地址
        
        步骤：
        1. 请求页面 HTML
        2. 用正则提取 JS 变量中的 url、vid、pic
        3. 补全相对路径
        4. 判断是否需要继续解析
        
        参数：
            url: 分享页地址
            
        返回：
            标准化的解析结果
        """
        if not url:
            logger.error("JsVariableParser.parse: URL 为空")
            return {
                "url": "",
                "title": "",
                "pic": "",
                "format": "",
                "parse": 0,
                "header": {},
                "success": False,
                "error": "URL 为空"
            }

        logger.info("解析分享页: %s", url)
        try:
            # 请求页面
            logger.debug("请求页面 HTML, timeout=%s", self.timeout)
            response = self._session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # 自动处理编码
            response.encoding = response.apparent_encoding or 'utf-8'
            html = response.text
            logger.debug("响应: status=%s, html 长度=%d", response.status_code, len(html))

            # 提取播放地址
            play_url = self._extract_url(html, url)
            if not play_url:
                logger.warning("未能在页面中找到播放地址: %s", url)
                return {
                    "url": "",
                    "title": "",
                    "pic": "",
                    "format": "",
                    "parse": 0,
                    "header": {},
                    "success": False,
                    "error": "未能在页面中找到播放地址"
                }

            logger.debug("提取到播放地址: %s", play_url)

            # 提取封面图
            pic_url = self._extract_pic(html, url)

            # 提取标题（从页面 title 标签）
            title = self._extract_title(html)

            # 判断格式
            format_type = "unknown"
            if ".m3u8" in play_url:
                format_type = "m3u8"
            elif ".mp4" in play_url:
                format_type = "mp4"

            # 判断是否需要继续解析
            # 如果已经是视频格式，parse=0；否则继续
            need_parse = 0 if DirectParser().can_parse(play_url) else 0

            logger.info("分享页解析成功: url=%s, format=%s", play_url[:80], format_type)
            return {
                "url": play_url,
                "title": title,
                "pic": pic_url,
                "format": format_type,
                "parse": 0,  # m3u8/mp4 地址不需要继续解析
                "header": {},
                "success": True,
                "error": ""
            }

        except requests.exceptions.Timeout:
            logger.error("请求超时（%s秒）: %s", self.timeout, url, exc_info=True)
            return {
                "url": "",
                "title": "",
                "pic": "",
                "format": "",
                "parse": 0,
                "header": {},
                "success": False,
                "error": f"请求超时（{self.timeout}秒）"
            }
        except requests.exceptions.ConnectionError as e:
            logger.error("连接失败: %s, url=%s", e, url, exc_info=True)
            return {
                "url": "",
                "title": "",
                "pic": "",
                "format": "",
                "parse": 0,
                "header": {},
                "success": False,
                "error": f"连接失败: {str(e)[:100]}"
            }
        except requests.exceptions.HTTPError as e:
            logger.error("HTTP错误: %s, url=%s", e.response.status_code, url, exc_info=True)
            return {
                "url": "",
                "title": "",
                "pic": "",
                "format": "",
                "parse": 0,
                "header": {},
                "success": False,
                "error": f"HTTP错误: {e.response.status_code}"
            }
        except Exception as e:
            logger.error("解析失败: %s, url=%s", e, url, exc_info=True)
            return {
                "url": "",
                "title": "",
                "pic": "",
                "format": "",
                "parse": 0,
                "header": {},
                "success": False,
                "error": f"解析失败: {str(e)[:100]}"
            }
    
    def _extract_url(self, html: str, base_url: str) -> Optional[str]:
        """从 HTML 中提取播放地址
        
        参数：
            html: 页面 HTML 内容
            base_url: 页面 URL，用于补全相对路径
            
        返回：
            完整的播放地址，如果未找到返回 None
        """
        match = self.URL_PATTERN.search(html)
        if not match:
            return None
        
        url = match.group(1)
        
        # 补全相对路径
        if url.startswith('/'):
            parsed = urlparse(base_url)
            url = f"{parsed.scheme}://{parsed.netloc}{url}"
        elif not url.startswith('http'):
            url = urljoin(base_url, url)
        
        return url
    
    def _extract_pic(self, html: str, base_url: str) -> str:
        """从 HTML 中提取封面图地址
        
        参数：
            html: 页面 HTML 内容
            base_url: 页面 URL
            
        返回：
            封面图地址，未找到返回空字符串
        """
        match = self.PIC_PATTERN.search(html)
        if not match:
            return ""
        
        pic = match.group(1)
        
        # 补全相对路径
        if pic.startswith('/'):
            parsed = urlparse(base_url)
            pic = f"{parsed.scheme}://{parsed.netloc}{pic}"
        elif not pic.startswith('http'):
            pic = urljoin(base_url, pic)
        
        return pic
    
    def _extract_title(self, html: str) -> str:
        """从 HTML 中提取标题
        
        参数：
            html: 页面 HTML 内容
            
        返回：
            标题文本
        """
        # 从 title 标签提取
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
        return ""


# 导入 DirectParser 用于判断是否需要继续解析
from .direct_parser import DirectParser