# -*- coding: utf-8 -*-
"""
直链解析器

如果地址本身就是视频格式（m3u8/mp4等），直接返回，不需要额外解析。
参考 TvBox 的 isVideoFormat 判断逻辑。
"""

from typing import Dict
from .base_parser import BaseParser


class DirectParser(BaseParser):
    """直链解析器
    
    如果地址本身就是视频格式（m3u8/mp4/flv 等），直接返回，
    不需要额外解析。
    
    这是优先级最高的解析器，会先被尝试。
    参考 TvBox SourceViewModel.java 里的判断逻辑：
    if (DefaultConfig.isVideoFormat(url)) {
        result.put("parse", 0);
        result.put("url", url);
    }
    """
    
    # 常见视频格式后缀（参考 TvBox 的 DefaultConfig.isVideoFormat）
    VIDEO_EXTENSIONS = (
        '.m3u8', '.mp4', '.flv', '.avi', '.mkv', '.rmvb', 
        '.wmv', '.mov', '.3gp', '.mpd',  # HLS/DASH
        '.mp3', '.m4a', '.wav', '.aac'   # 音频格式也支持
    )
    
    def __init__(self):
        """初始化直链解析器"""
        super().__init__(name="DirectParser", priority=10)  # 最高优先级
    
    def can_parse(self, url: str) -> bool:
        """判断 URL 是否是直接的视频地址
        
        判断逻辑：
        1. URL 不为空
        2. URL 中包含视频格式后缀（不区分大小写）
        
        参数：
            url: 待判断的地址
            
        返回：
            True 表示是直链，可以解析
        """
        if not url:
            return False
        
        url_lower = url.lower().split('?')[0]  # 忽略查询参数
        
        # 判断是否包含视频后缀
        for ext in self.VIDEO_EXTENSIONS:
            if url_lower.endswith(ext):
                return True
            # 有些地址可能是 xxx.m3u8?token=xxx 格式
            if ext in url_lower:
                return True
        
        return False
    
    def parse(self, url: str) -> Dict:
        """解析直链地址
        
        直接返回原地址，不需要任何网络请求。
        会尝试判断视频格式。
        
        参数：
            url: 视频直链地址
            
        返回：
            标准化的解析结果
        """
        # 判断格式
        format_type = "unknown"
        url_lower = url.lower()
        
        if ".m3u8" in url_lower:
            format_type = "m3u8"
        elif ".mp4" in url_lower:
            format_type = "mp4"
        elif ".flv" in url_lower:
            format_type = "flv"
        elif ".mpd" in url_lower:
            format_type = "dash"
        elif ".mkv" in url_lower:
            format_type = "mkv"
        elif ".avi" in url_lower:
            format_type = "avi"
        
        return {
            "url": url,
            "title": "",
            "pic": "",
            "format": format_type,
            "parse": 0,  # 不需要继续解析，直接播放
            "header": {},
            "success": True,
            "error": ""
        }