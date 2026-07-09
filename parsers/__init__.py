# -*- coding: utf-8 -*-
"""
播放地址解析器模块

参考 TvBox 的设计思想：不同来源的播放地址需要不同的解析方式，
通过插件化的解析器来处理各种情况。

解析流程：URL → 判断能否解析 → 解析 → 返回真实播放地址
"""

from .base_parser import BaseParser
from .direct_parser import DirectParser
from .js_variable_parser import JsVariableParser
from .web_sniff_parser import WebSniffParser
from .json_api_parser import JsonApiParser
from .spider_parse_parser import SpiderParseParser
from .parser_manager import ParserManager

__all__ = [
    "BaseParser",
    "DirectParser",
    "JsVariableParser",
    "WebSniffParser",
    "JsonApiParser",
    "SpiderParseParser",
    "ParserManager",
]