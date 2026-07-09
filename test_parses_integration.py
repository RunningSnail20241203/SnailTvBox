# -*- coding: utf-8 -*-
"""
Parses 解析器系统端到端集成测试

验证 Parses 解析器系统从配置加载到 URL 匹配的完整流程：
1. ConfigLoader 加载 jsm.json 配置
2. ParsesLoader 根据 ParseBean 创建对应解析器实例
3. 批量注册到 ParserManager
4. URL 匹配（直链 / 普通页面）
5. flag 匹配（有 flag 的解析器对特定平台 URL 的识别）
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config_loader import ConfigLoader
from utils.parses_loader import ParsesLoader
from parsers import ParserManager, DirectParser, WebSniffParser, JsonApiParser, SpiderParseParser
from models.parse_bean import ParseBean


class TestRunner:
    """简易测试运行器，统计通过/失败数量"""

    def __init__(self):
        self.passed = 0
        self.failed = 0

    def assert_true(self, condition, message):
        """断言条件为真"""
        if condition:
            self.passed += 1
            print(f"  ✅ {message}")
        else:
            self.failed += 1
            print(f"  ❌ {message}")

    def assert_equal(self, actual, expected, message):
        """断言实际值等于期望值"""
        if actual == expected:
            self.passed += 1
            print(f"  ✅ {message} (={actual})")
        else:
            self.failed += 1
            print(f"  ❌ {message}: 期望 {expected}, 实际 {actual}")


def test_config_loading(runner):
    """配置加载测试：使用 ConfigLoader 加载 jsm.json，验证 parses 数量大于 0"""
    print("=" * 60)
    print("1. 配置加载测试")
    print("=" * 60)

    loader = ConfigLoader()
    result = loader.load_from_file("jsm.json")
    runner.assert_true(result, "ConfigLoader 成功加载 jsm.json")
    runner.assert_true(len(loader.parses) > 0, f"parses 数量 > 0 (实际 {len(loader.parses)})")
    return loader


def test_create_parsers(runner, loader):
    """ParsesLoader 创建解析器测试：遍历 loader.parses，验证各 type 返回正确实例"""
    print("\n" + "=" * 60)
    print("2. ParsesLoader 创建解析器测试")
    print("=" * 60)

    for pb in loader.parses:
        parser = ParsesLoader.create_parser(pb)

        if pb.type == 0:
            runner.assert_true(
                isinstance(parser, WebSniffParser),
                f"{pb.name} (type=0) → WebSniffParser"
            )
        elif pb.type == 1:
            runner.assert_true(
                isinstance(parser, JsonApiParser),
                f"{pb.name} (type=1) → JsonApiParser"
            )
        elif pb.type == 3:
            runner.assert_true(
                isinstance(parser, SpiderParseParser),
                f"{pb.name} (type=3) → SpiderParseParser"
            )
        else:
            runner.assert_true(
                parser is None,
                f"{pb.name} (type={pb.type}) → None (不支持的类型)"
            )

    # 额外验证：不支持的 type 返回 None
    pb_unsupported = ParseBean()
    pb_unsupported.name = "不支持测试"
    pb_unsupported.type = 4
    pb_unsupported.url = "http://example.com"
    parser_unsupported = ParsesLoader.create_parser(pb_unsupported)
    runner.assert_true(parser_unsupported is None, "手动构造 type=4 → None")


def test_batch_register(runner, loader):
    """批量注册测试：创建 ParserManager，调用 load_into_manager，验证注册数量正确"""
    print("\n" + "=" * 60)
    print("3. 批量注册测试")
    print("=" * 60)

    manager = ParserManager()
    manager.register(DirectParser())

    count = ParsesLoader.load_into_manager(loader.parses, manager)

    # 计算期望注册数量（排除不支持的 type 和空 url）
    expected_count = 0
    for pb in loader.parses:
        p = ParsesLoader.create_parser(pb)
        if p is not None:
            expected_count += 1

    runner.assert_equal(count, expected_count, "ParsesLoader.load_into_manager 成功注册数量")

    total_parsers = len(manager.get_parsers())
    runner.assert_equal(
        total_parsers,
        expected_count + 1,
        "ParserManager 中解析器总数（含 DirectParser）"
    )


def test_url_matching(runner, loader):
    """URL 匹配测试：验证 m3u8 直链和普通 http 页面的 can_parse 行为"""
    print("\n" + "=" * 60)
    print("4. URL 匹配测试")
    print("=" * 60)

    manager = ParserManager()
    manager.register(DirectParser())
    ParsesLoader.load_into_manager(loader.parses, manager)

    # m3u8 直链应该返回 True（DirectParser 能处理）
    m3u8_url = "https://cdn.example.com/playlist.m3u8?token=abc123"
    runner.assert_true(
        manager.can_parse(m3u8_url),
        f"m3u8 直链 can_parse 返回 True: {m3u8_url}"
    )

    # 普通 http 页面应该返回 True（至少有一个万能解析器能处理）
    http_url = "https://www.example.com/video/page.html"
    runner.assert_true(
        manager.can_parse(http_url),
        f"普通 http 页面 can_parse 返回 True: {http_url}"
    )

    # 空的或非法 URL 应该返回 False
    runner.assert_true(
        not manager.can_parse(""),
        "空字符串 URL can_parse 返回 False"
    )


def test_flag_matching(runner, loader):
    """flag 匹配测试：验证有 flag 的解析器对匹配/不匹配 URL 的行为"""
    print("\n" + "=" * 60)
    print("5. flag 匹配测试")
    print("=" * 60)

    # 从配置中找带 flag 的 type=0 (WebSniffParser)
    web_flagged = None
    for pb in loader.parses:
        if pb.type == 0 and pb.flag:
            web_flagged = pb
            break

    if web_flagged:
        parser = ParsesLoader.create_parser(web_flagged)
        flag_keyword = web_flagged.flag[0]
        matched_url = f"https://{flag_keyword}.com/video/123"
        unmatched_url = "https://unknown-platform-example.com/video/123"

        runner.assert_true(
            parser.can_parse(matched_url),
            f"WebSniffParser({web_flagged.name}) 匹配 flag '{flag_keyword}' 的 URL"
        )
        runner.assert_true(
            not parser.can_parse(unmatched_url),
            f"WebSniffParser({web_flagged.name}) 不匹配无 flag 的 URL"
        )
    else:
        print("  ⚠️ 配置中未找到带 flag 的 type=0 解析源，跳过 WebSniffParser flag 测试")

    # 从配置中找带 flag 的 type=1 (JsonApiParser)
    json_flagged = None
    for pb in loader.parses:
        if pb.type == 1 and pb.flag:
            json_flagged = pb
            break

    if json_flagged:
        parser = ParsesLoader.create_parser(json_flagged)
        flag_keyword = json_flagged.flag[0]
        matched_url = f"https://{flag_keyword}.com/video/456"
        unmatched_url = "https://unknown-platform-example.com/video/456"

        runner.assert_true(
            parser.can_parse(matched_url),
            f"JsonApiParser({json_flagged.name}) 匹配 flag '{flag_keyword}' 的 URL"
        )
        runner.assert_true(
            not parser.can_parse(unmatched_url),
            f"JsonApiParser({json_flagged.name}) 不匹配无 flag 的 URL"
        )
    else:
        print("  ⚠️ 配置中未找到带 flag 的 type=1 解析源，跳过 JsonApiParser flag 测试")

    # 配置中没有带 flag 的 type=3，手动构造验证 SpiderParseParser 的 flag 行为
    pb_spider = ParseBean()
    pb_spider.name = "SpiderFlag测试"
    pb_spider.type = 3
    pb_spider.url = "Demo"
    pb_spider.flag = ["iqiyi", "爱奇艺"]

    spider_parser = ParsesLoader.create_parser(pb_spider)
    runner.assert_true(
        isinstance(spider_parser, SpiderParseParser),
        "手动构造带 flag 的 type=3 → SpiderParseParser"
    )
    runner.assert_true(
        spider_parser.can_parse("https://iqiyi.com/v/123"),
        "SpiderParseParser 匹配 flag 'iqiyi' 的 URL"
    )
    runner.assert_true(
        not spider_parser.can_parse("https://example.com/v/123"),
        "SpiderParseParser 不匹配无 flag 的 URL"
    )

    # 验证配置中 type=3 的 "Json聚合"（无 flag，应为万能解析）
    spider_universal = None
    for pb in loader.parses:
        if pb.type == 3:
            spider_universal = pb
            break

    if spider_universal:
        parser3 = ParsesLoader.create_parser(spider_universal)
        runner.assert_true(
            parser3.can_parse("https://any-platform.com/video"),
            f"SpiderParseParser({spider_universal.name}) 无 flag 时对普通 URL 返回 True"
        )


def main():
    """主入口：运行所有集成测试并打印统计结果"""
    runner = TestRunner()

    try:
        loader = test_config_loading(runner)
        test_create_parsers(runner, loader)
        test_batch_register(runner, loader)
        test_url_matching(runner, loader)
        test_flag_matching(runner, loader)
    except Exception as e:
        print(f"\n❌ 测试执行过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        runner.failed += 1

    print("\n" + "=" * 60)
    print("测试结果统计")
    print("=" * 60)
    print(f"  通过: {runner.passed}")
    print(f"  失败: {runner.failed}")
    print(f"  总计: {runner.passed + runner.failed}")

    if runner.failed == 0:
        print("\n🎉 所有端到端集成测试通过！")
        return 0
    else:
        print(f"\n⚠️ 共有 {runner.failed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
