# -*- coding: utf-8 -*-
"""
数据模型模块
定义 TvBox 中使用的核心数据结构
"""

from .source_bean import SourceBean
from .vod_info import VodInfo
from .parse_bean import ParseBean

__all__ = ["SourceBean", "VodInfo", "ParseBean"]
