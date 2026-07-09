# -*- coding: utf-8 -*-
"""
播放地址解析器基类

所有解析器都继承这个基类，定义统一的接口。
参考 TvBox 的设计：解析器负责将各种格式的播放地址转换成可直接播放的地址。
"""

from abc import ABC, abstractmethod
from typing import Dict


class BaseParser(ABC):
    """播放地址解析器基类
    
    参考 TvBox 的设计思想：不同来源的播放地址需要不同的解析方式，
    通过插件化的解析器来处理各种情况。
    
    解析流程：URL → 判断能否解析 → 解析 → 返回真实播放地址
    
    设计要点：
    1. can_parse() - 判断当前解析器能否处理某个 URL（基于 URL 特征）
    2. parse() - 执行实际的解析逻辑
    3. priority - 优先级，数字越小越优先尝试
    
    这样设计的好处（开闭原则）：
    - 添加新的解析器不需要修改已有代码
    - 只需要继承 BaseParser 实现新的子类即可
    - ParserManager 会自动按优先级调用
    """
    
    def __init__(self, name: str = "BaseParser", priority: int = 100):
        """初始化解析器
        
        参数：
            name: 解析器名称，用于日志和调试
            priority: 优先级，数字越小优先级越高（越先被尝试）
        """
        self.name = name
        self.priority = priority
    
    def can_parse(self, url: str) -> bool:
        """判断当前解析器能否处理这个 URL
        
        子类应该重写此方法，根据 URL 特征判断是否能解析。
        
        比如：
        - DirectParser: URL 本身就是视频格式（.m3u8/.mp4）
        - JsVariableParser: URL 是某个视频分享网站
        - ApiParser: URL 需要调用远程解析接口
        
        参数：
            url: 待解析的地址
            
        返回：
            True 表示能处理，False 表示不能处理
        """
        return False
    
    def parse(self, url: str) -> Dict:
        """解析播放地址
        
        子类必须重写此方法，执行实际的解析逻辑。
        
        返回值格式（标准化，方便后续处理）：
        {
            "url": "真实播放地址",      # 必填，解析后的地址
            "title": "视频标题",        # 可选
            "pic": "封面图地址",        # 可选
            "format": "m3u8",          # 可选，视频格式 m3u8/mp4/flv 等
            "parse": 0,                # 是否需要继续解析，0=不需要，1=需要
            "header": {},              # 可选，播放时需要的请求头
            "success": True,           # 是否解析成功
            "error": ""                # 失败时的错误信息
        }
        
        注意：parse 字段参考 TvBox 的设计
        - parse=0：已经拿到真实播放地址，可以直接播放
        - parse=1：还需要继续解析（比如拿到了另一个网页地址）
        这样 ParserManager 可以链式解析
        
        参数：
            url: 待解析的地址
            
        返回：
            标准化的解析结果字典
        """
        return {
            "url": "",
            "title": "",
            "pic": "",
            "format": "",
            "parse": 0,
            "header": {},
            "success": False,
            "error": "BaseParser 不能直接使用，请使用子类"
        }
    
    def __repr__(self):
        return f"<{self.name}(priority={self.priority})>"