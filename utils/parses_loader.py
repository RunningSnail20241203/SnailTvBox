# -*- coding: utf-8 -*-
"""
ParsesLoader - Parses 解析器加载器

负责从 ParseBean 列表创建对应的解析器实例，并注册到 ParserManager 中。

这是连接 TvBox 配置（parses 字段）和我们解析器架构的桥梁。

使用方式：
    config_loader = ConfigLoader()
    config_loader.load_from_file("jsm.json")
    
    parser_manager = ParserManager()
    ParsesLoader.load_into_manager(config_loader.parses, parser_manager)
    
    # 现在 parser_manager 中已经注册了所有 parses 对应的解析器
    result = parser_manager.parse("https://xxx.com/video")
"""

import logging
from typing import List
from models.parse_bean import ParseBean
from parsers import (
    ParserManager,
    WebSniffParser,
    JsonApiParser,
    SpiderParseParser,
)

logger = logging.getLogger(__name__)


class ParsesLoader:
    """Parses 解析器加载器

    根据 ParseBean 的 type 字段，创建对应的解析器实例：
    - type=0 → WebSniffParser
    - type=1 → JsonApiParser
    - type=3 → SpiderParseParser
    - type=2, 4 → 暂不支持

    然后将解析器注册到 ParserManager 中，使其参与链式解析。
    """

    @staticmethod
    def create_parser(parse_bean: ParseBean):
        """根据 ParseBean 创建对应的解析器实例

        参数:
            parse_bean: 解析源配置

        返回:
            解析器实例，如果 type 不支持则返回 None
        """
        if not parse_bean or not parse_bean.url:
            logger.debug("跳过无效的 parse_bean: name=%s, url=%s",
                         getattr(parse_bean, "name", None), getattr(parse_bean, "url", None))
            return None

        name = parse_bean.name or "Unknown"
        logger.debug("创建解析器: name=%s, type=%s, url=%s", name, parse_bean.type, parse_bean.url)

        try:
            if parse_bean.type == 0:
                # type=0: WebView 嗅探 / HTTP 解析
                parser = WebSniffParser(
                    flag=parse_bean.flag,
                    ext=parse_bean.ext,
                )
                logger.debug("创建 WebSniffParser 成功: %s", name)
                return parser

            elif parse_bean.type == 1:
                # type=1: JSON 解析接口
                parser = JsonApiParser(
                    api_url=parse_bean.url,
                    flag=parse_bean.flag,
                    ext=parse_bean.ext,
                )
                logger.debug("创建 JsonApiParser 成功: %s", name)
                return parser

            elif parse_bean.type == 3:
                # type=3: Spider 解析
                parser = SpiderParseParser(
                    flag=parse_bean.flag,
                    ext=parse_bean.ext,
                )
                logger.debug("创建 SpiderParseParser 成功: %s", name)
                return parser

            else:
                logger.warning("不支持的解析类型: type=%s, name=%s", parse_bean.type, name)
                return None

        except Exception:
            logger.error("解析器创建失败: name=%s, type=%s", name, parse_bean.type, exc_info=True)
            return None

    @staticmethod
    def load_into_manager(parses: List[ParseBean], manager: ParserManager) -> int:
        """将 ParseBean 列表批量加载到 ParserManager

        参数:
            parses: ParseBean 列表
            manager: ParserManager 实例

        返回:
            成功注册的解析器数量
        """
        if not parses or not manager:
            logger.debug("load_into_manager 跳过: parses=%s, manager=%s", parses is not None, manager is not None)
            return 0

        logger.info("开始批量加载解析器，共 %d 个 ParseBean", len(parses))
        registered_count = 0

        for parse_bean in parses:
            parser = ParsesLoader.create_parser(parse_bean)
            if parser:
                manager.register(parser)
                registered_count += 1
                logger.debug("注册解析器: %s (%s)", parse_bean.name, parse_bean.get_type_name())

        logger.info("共注册 %d/%d 个解析器", registered_count, len(parses))
        return registered_count

    @staticmethod
    def load_from_config(config_loader, manager: ParserManager) -> int:
        """从 ConfigLoader 直接加载 parses 到 ParserManager

        参数:
            config_loader: ConfigLoader 实例（已加载配置）
            manager: ParserManager 实例

        返回:
            成功注册的解析器数量
        """
        if not config_loader or not manager:
            logger.warning("load_from_config 参数为空: config_loader=%s, manager=%s",
                           config_loader is not None, manager is not None)
            return 0

        parses = getattr(config_loader, "parses", [])
        logger.info("从 config_loader 加载 parses，共 %d 个", len(parses))
        return ParsesLoader.load_into_manager(parses, manager)
