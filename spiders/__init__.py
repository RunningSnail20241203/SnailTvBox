# -*- coding: utf-8 -*-
"""
爬虫模块
提供 TvBox 爬虫源的基类和模拟实现
"""

from .base_spider import BaseSpider
from .mock_spider import MockSpider
from .json_spider import JsonSpider

__all__ = ["BaseSpider", "MockSpider", "JsonSpider"]
