# -*- coding: utf-8 -*-
"""
解析器管理器

管理多个解析器，按优先级自动选择合适的解析器。
支持链式解析：如果解析结果 parse=1，会继续解析。

参考 TvBox 的解析链思想：
- PlayFragment.doParse() 方法会根据 parse 类型选择解析方式
- 如果 parse=1，会继续调用解析源进行二次解析
- 支持多级解析，直到拿到真实播放地址
"""

from typing import List, Dict, Optional
import logging
from .base_parser import BaseParser

logger = logging.getLogger(__name__)


class ParserManager:
    """解析器管理器
    
    管理多个解析器，按优先级自动选择合适的解析器。
    参考 TvBox 的解析链思想：一个 URL 可能需要经过多层解析。
    
    使用方式：
    ```python
    manager = ParserManager()
    manager.register(DirectParser())
    manager.register(JsVariableParser())
    
    result = manager.parse("https://xxx.com/video.m3u8")
    if result["success"]:
        print(f"真实地址: {result['url']}")
    ```
    
    链式解析示例：
    1. URL: https://share.xxx.com/abc123（分享页）
    2. JsVariableParser 解析后返回: https://xxx.com/index.m3u8（m3u8地址）
    3. DirectParser 判断是直链，parse=0，结束解析
    """
    
    def __init__(self):
        """初始化解析器管理器"""
        self._parsers: List[BaseParser] = []
    
    def register(self, parser: BaseParser) -> None:
        """注册解析器
        
        注册后按优先级排序（priority 数字小的优先）
        
        参数：
            parser: 解析器实例
        """
        if parser not in self._parsers:
            self._parsers.append(parser)
            # 按优先级排序（数字小的优先）
            self._parsers.sort(key=lambda p: p.priority)
            logger.debug("注册解析器: %s (priority=%d)", parser.name, parser.priority)
    
    def unregister(self, parser: BaseParser) -> bool:
        """移除解析器
        
        参数：
            parser: 要移除的解析器
            
        返回：
            True 表示移除成功，False 表示不存在
        """
        if parser in self._parsers:
            self._parsers.remove(parser)
            return True
        return False
    
    def get_parsers(self) -> List[BaseParser]:
        """获取所有已注册的解析器（按优先级排序）
        
        返回：
            解析器列表的副本
        """
        return self._parsers.copy()
    
    def can_parse(self, url: str) -> bool:
        """判断是否有解析器能处理这个 URL
        
        参数：
            url: 待判断的地址
            
        返回：
            True 表示至少有一个解析器能处理
        """
        for parser in self._parsers:
            if parser.can_parse(url):
                return True
        return False
    
    def parse(self, url: str, max_depth: int = 5) -> Dict:
        """解析播放地址
        
        按优先级依次尝试解析器，直到解析成功或所有解析器都无法处理。
        支持链式解析（如果返回 parse=1，继续解析）。
        
        链式解析逻辑（参考 TvBox）：
        1. 找到能处理当前 URL 的解析器
        2. 执行解析，获得结果
        3. 如果 parse=0，结束解析，返回结果
        4. 如果 parse=1，用新的 URL 继续解析
        5. 重复直到 parse=0 或达到最大深度
        
        参数：
            url: 原始地址
            max_depth: 最大解析深度，防止无限循环（默认5层）
            
        返回：
            标准化的解析结果字典
        """
        if not url:
            logger.error("原始 URL 为空，无法解析")
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

        logger.info("开始解析: %s", url)
        current_url = url
        depth = 0
        last_result = None

        while depth < max_depth:
            # 找到能处理当前 URL 的解析器
            matched_parser = None
            for parser in self._parsers:
                try:
                    can = parser.can_parse(current_url)
                except Exception:
                    logger.error("解析器 %s.can_parse 异常", parser.name, exc_info=True)
                    can = False
                if can:
                    matched_parser = parser
                    break

            if matched_parser is None:
                # 没有解析器能处理了
                if last_result is None:
                    # 从未成功解析过
                    logger.warning("没有解析器能处理此 URL: %s", current_url)
                    return {
                        "url": current_url,
                        "title": "",
                        "pic": "",
                        "format": "",
                        "parse": 0,
                        "header": {},
                        "success": False,
                        "error": f"没有找到能处理此 URL 的解析器: {current_url[:100]}..."
                    }
                else:
                    # 之前解析过，返回最后成功的结果
                    logger.debug("无更多解析器可用，返回最后成功结果")
                    return last_result

            # 执行解析
            logger.debug("使用解析器: %s, URL: %s", matched_parser.name, current_url[:80])
            result = matched_parser.parse(current_url)

            # 检查是否解析成功
            if not result.get("success", False):
                logger.warning("解析器 %s 失败: %s", matched_parser.name, result.get("error", "未知错误"))
                return result

            # 更新最后成功的结果
            last_result = result
            logger.debug("解析结果: success=True, parse=%s, url=%s",
                         result.get("parse", 0), result.get("url", "")[:80])

            # 检查是否需要继续解析
            if result.get("parse", 0) == 0:
                # 不需要继续解析了
                logger.info("解析完成: success=True, url=%s", result.get("url", "")[:80])
                return result

            # 需要继续解析，获取新的 URL
            new_url = result.get("url", "")
            if not new_url:
                # 新 URL 为空，无法继续
                logger.error("解析返回的 URL 为空，无法继续链式解析")
                result["error"] = "解析返回的 URL 为空"
                return result

            if new_url == current_url:
                # URL 没变化，防止无限循环
                logger.warning("解析后 URL 未变化，强制结束: %s", current_url)
                result["parse"] = 0  # 强制结束
                result["error"] = "解析后 URL 未变化"
                return result

            # 更新 URL，继续下一轮解析
            current_url = new_url
            depth += 1
            logger.debug("继续链式解析 (深度 %d): %s", depth, current_url[:80])
        
        # 达到最大深度
        return {
            "url": current_url,
            "title": last_result.get("title", "") if last_result else "",
            "pic": last_result.get("pic", "") if last_result else "",
            "format": last_result.get("format", "") if last_result else "",
            "parse": 1,
            "header": last_result.get("header", {}) if last_result else {},
            "success": True,
            "error": f"达到最大解析深度 {max_depth}，可能存在循环解析"
        }
    
    def clear(self) -> None:
        """清空所有已注册的解析器"""
        self._parsers.clear()
    
    def __repr__(self):
        parser_names = [p.name for p in self._parsers]
        return f"<ParserManager parsers={parser_names}>"