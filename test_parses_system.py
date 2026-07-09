# -*- coding: utf-8 -*-
"""
Parses 解析器系统完整测试

测试从配置加载 → 解析器创建 → ParserManager 注册的完整流程
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config_loader import ConfigLoader
from utils.parses_loader import ParsesLoader
from parsers import ParserManager, DirectParser, WebSniffParser, JsonApiParser, SpiderParseParser
from models.parse_bean import ParseBean


def test_parses_loader():
    """测试 ParsesLoader 从 ParseBean 创建解析器"""
    print("=" * 60)
    print("测试 ParsesLoader")
    print("=" * 60)

    # 测试 type=0
    pb0 = ParseBean()
    pb0.name = "嗅探测试"
    pb0.type = 0
    pb0.url = "https://jx.example.com/?url="
    pb0.flag = ["qq", "腾讯"]

    parser0 = ParsesLoader.create_parser(pb0)
    assert parser0 is not None, "type=0 解析器创建失败"
    assert isinstance(parser0, WebSniffParser), f"期望 WebSniffParser，实际是 {type(parser0)}"
    assert parser0.flag == ["qq", "腾讯"]
    print(f"  ✅ type=0: {parser0}")

    # 测试 type=1
    pb1 = ParseBean()
    pb1.name = "JSON测试"
    pb1.type = 1
    pb1.url = "https://jx.api.com/?url="
    pb1.ext = {"header": {"User-Agent": "Test"}}

    parser1 = ParsesLoader.create_parser(pb1)
    assert parser1 is not None, "type=1 解析器创建失败"
    assert isinstance(parser1, JsonApiParser), f"期望 JsonApiParser，实际是 {type(parser1)}"
    assert parser1.api_url == "https://jx.api.com/?url="
    print(f"  ✅ type=1: {parser1}")

    # 测试 type=3
    pb3 = ParseBean()
    pb3.name = "Spider测试"
    pb3.type = 3
    pb3.url = "Demo"
    pb3.flag = ["iqiyi"]

    parser3 = ParsesLoader.create_parser(pb3)
    assert parser3 is not None, "type=3 解析器创建失败"
    assert isinstance(parser3, SpiderParseParser), f"期望 SpiderParseParser，实际是 {type(parser3)}"
    assert parser3.flag == ["iqiyi"]
    print(f"  ✅ type=3: {parser3}")

    # 测试不支持的 type
    pb2 = ParseBean()
    pb2.name = "不支持"
    pb2.type = 2
    pb2.url = "xxx"

    parser2 = ParsesLoader.create_parser(pb2)
    assert parser2 is None, "type=2 应该返回 None"
    print(f"  ✅ type=2 (不支持): 返回 None")

    # 测试空 url
    pb_empty = ParseBean()
    pb_empty.name = "空URL"
    pb_empty.type = 0
    pb_empty.url = ""

    parser_empty = ParsesLoader.create_parser(pb_empty)
    assert parser_empty is None, "空 URL 应该返回 None"
    print(f"  ✅ 空 URL: 返回 None")


def test_load_into_manager():
    """测试批量加载到 ParserManager"""
    print("\n" + "=" * 60)
    print("测试批量加载到 ParserManager")
    print("=" * 60)

    manager = ParserManager()
    manager.register(DirectParser())

    parses = [
        ParseBean(),
        ParseBean(),
        ParseBean(),
    ]
    parses[0].name = "jx1"
    parses[0].type = 0
    parses[0].url = "https://jx1.com/?url="
    parses[0].flag = ["qq"]

    parses[1].name = "jx2"
    parses[1].type = 1
    parses[1].url = "https://jx2.com/?url="
    parses[1].flag = ["iqiyi"]

    parses[2].name = "jx3"
    parses[2].type = 3
    parses[2].url = "Demo"
    parses[2].flag = ["youku"]

    count = ParsesLoader.load_into_manager(parses, manager)
    assert count == 3, f"期望注册 3 个，实际 {count}"

    parsers = manager.get_parsers()
    print(f"  注册后解析器数量: {len(parsers)}")
    for p in parsers:
        print(f"    - {p.name} (priority={p.priority})")

    # 测试 flag 匹配
    assert manager.can_parse("https://v.qq.com/xxx") == True, "qq 地址应该能解析"
    assert manager.can_parse("https://iqiyi.com/xxx") == True, "iqiyi 地址应该能解析"
    assert manager.can_parse("https://youku.com/xxx") == True, "youku 地址应该能解析"
    # example.com 不在任何 flag 中，所以应该返回 False
    assert manager.can_parse("https://example.com/xxx") == False, "不在任何 flag 中的地址应该不能解析"
    print("  ✅ flag 匹配测试通过")


def test_from_config():
    """测试从配置文件加载 parses"""
    print("\n" + "=" * 60)
    print("测试从配置文件加载 parses")
    print("=" * 60)

    loader = ConfigLoader()
    result = loader.load_from_file("jsm.json")
    assert result == True, "配置加载失败"

    print(f"\n  配置中 parses 数量: {len(loader.parses)}")

    manager = ParserManager()
    manager.register(DirectParser())

    count = ParsesLoader.load_from_config(loader, manager)
    print(f"  成功注册解析器: {count} 个")

    parsers = manager.get_parsers()
    type0_count = sum(1 for p in parsers if isinstance(p, WebSniffParser))
    type1_count = sum(1 for p in parsers if isinstance(p, JsonApiParser))
    type3_count = sum(1 for p in parsers if isinstance(p, SpiderParseParser))

    print(f"    - WebSniffParser (type=0): {type0_count}")
    print(f"    - JsonApiParser (type=1): {type1_count}")
    print(f"    - SpiderParseParser (type=3): {type3_count}")

    assert type0_count > 0, "应该有 type=0 解析器"
    assert count == type0_count + type1_count + type3_count
    print("  ✅ 从配置加载测试通过")


def test_flag_matching():
    """测试 flag 匹配功能"""
    print("\n" + "=" * 60)
    print("测试 flag 匹配")
    print("=" * 60)

    # 创建带 flag 的解析器
    pb = ParseBean()
    pb.name = "腾讯专用"
    pb.type = 0
    pb.url = "https://jx.qq.com/?url="
    pb.flag = ["qq", "腾讯", "v.qq.com"]

    manager = ParserManager()
    parser = ParsesLoader.create_parser(pb)
    manager.register(parser)

    # 测试匹配
    assert parser.can_parse("https://v.qq.com/x/cover/xxx.html") == True
    assert parser.can_parse("https://film.qq.com/xxx") == True
    assert parser.can_parse("https://iqiyi.com/xxx") == False
    assert parser.can_parse("https://example.com/xxx") == False
    print("  ✅ flag 匹配测试通过")


def main():
    try:
        test_parses_loader()
        test_load_into_manager()
        test_from_config()
        test_flag_matching()

        print("\n" + "=" * 60)
        print("🎉 所有 Parses 系统测试通过！")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())