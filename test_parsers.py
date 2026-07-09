# -*- coding: utf-8 -*-
"""
解析器架构测试

测试 BaseParser、DirectParser 和 ParserManager 的基本功能。
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsers import BaseParser, DirectParser, ParserManager


def test_direct_parser():
    """测试直链解析器"""
    print("=" * 60)
    print("测试 DirectParser")
    print("=" * 60)
    
    parser = DirectParser()
    
    # 测试 can_parse
    test_urls = [
        ("https://example.com/video.m3u8", True, "m3u8直链"),
        ("https://example.com/video.mp4", True, "mp4直链"),
        ("https://example.com/video.m3u8?token=xxx", True, "带参数的m3u8"),
        ("https://example.com/share/abc123", False, "非视频地址"),
        ("https://phimgood.com/share/xxx", False, "分享页"),
    ]
    
    for url, expected, desc in test_urls:
        result = parser.can_parse(url)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {desc}: {url[:50]}... -> can_parse={result}")
        assert result == expected, f"期望 {expected}，实际 {result}"
    
    # 测试 parse
    print("\n测试 parse 方法:")
    result = parser.parse("https://example.com/video.m3u8")
    print(f"  解析结果: success={result['success']}, format={result['format']}, parse={result['parse']}")
    assert result["success"] == True
    assert result["format"] == "m3u8"
    assert result["parse"] == 0
    print("  ✅ DirectParser 测试通过")
    
    return True


def test_parser_manager():
    """测试解析器管理器"""
    print("\n" + "=" * 60)
    print("测试 ParserManager")
    print("=" * 60)
    
    manager = ParserManager()
    
    # 注册解析器
    parser1 = DirectParser()
    manager.register(parser1)
    print(f"  注册解析器: {parser1.name}")
    
    # 检查解析器列表
    parsers = manager.get_parsers()
    print(f"  已注册解析器数量: {len(parsers)}")
    assert len(parsers) == 1
    
    # 测试 can_parse
    print("\n测试 can_parse:")
    test_urls = [
        ("https://example.com/video.m3u8", True),
        ("https://example.com/share/abc", False),
    ]
    for url, expected in test_urls:
        result = manager.can_parse(url)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {url[:50]}... -> {result}")
        assert result == expected
    
    # 测试 parse - 直链
    print("\n测试 parse（直链）:")
    result = manager.parse("https://example.com/video.m3u8")
    print(f"  结果: success={result['success']}, url={result['url'][:50]}...")
    assert result["success"] == True
    assert result["url"] == "https://example.com/video.m3u8"
    assert result["parse"] == 0
    print("  ✅ 直链解析通过")
    
    # 测试 parse - 无法解析的地址
    print("\n测试 parse（无法解析）:")
    result = manager.parse("https://example.com/share/abc123")
    print(f"  结果: success={result['success']}, error={result['error'][:50]}...")
    assert result["success"] == False
    assert "没有找到" in result["error"]
    print("  ✅ 无法解析的情况正确处理")
    
    return True


def test_parser_priority():
    """测试解析器优先级"""
    print("\n" + "=" * 60)
    print("测试解析器优先级")
    print("=" * 60)
    
    # 创建自定义解析器（不同优先级）
    class HighPriorityParser(BaseParser):
        def __init__(self):
            super().__init__(name="HighPriorityParser", priority=5)
        def can_parse(self, url):
            return "high" in url
        def parse(self, url):
            return {"url": url, "success": True, "parse": 0}
    
    class LowPriorityParser(BaseParser):
        def __init__(self):
            super().__init__(name="LowPriorityParser", priority=50)
        def can_parse(self, url):
            return "low" in url or "high" in url  # 都能处理
        def parse(self, url):
            return {"url": url + "_low", "success": True, "parse": 0}
    
    manager = ParserManager()
    manager.register(LowPriorityParser())   # 后注册但优先级低
    manager.register(HighPriorityParser())  # 后注册但优先级高
    
    parsers = manager.get_parsers()
    print(f"  解析器顺序: {[p.name for p in parsers]}")
    assert parsers[0].name == "HighPriorityParser"  # 高优先级在前
    
    # 测试：两个解析器都能处理时，优先级高的先尝试
    result = manager.parse("https://example.com/high/test")
    print(f"  解析 'high' 地址时使用: {parsers[0].name}")
    assert result["success"] == True
    print("  ✅ 优先级排序正确")
    
    return True


def test_chain_parsing():
    """测试链式解析"""
    print("\n" + "=" * 60)
    print("测试链式解析")
    print("=" * 60)
    
    # 创建一个返回 "需要继续解析" 的解析器
    class IntermediateParser(BaseParser):
        def __init__(self):
            super().__init__(name="IntermediateParser", priority=20)
        def can_parse(self, url):
            return "share" in url
        def parse(self, url):
            # 模拟从分享页提取 m3u8 地址
            return {
                "url": "https://example.com/video.m3u8",
                "title": "测试视频",
                "parse": 1,  # 需要继续解析
                "success": True,
                "error": ""
            }
    
    manager = ParserManager()
    manager.register(DirectParser())         # priority=10
    manager.register(IntermediateParser())   # priority=20
    
    # 链式解析：分享页 -> m3u8
    print("  输入: https://example.com/share/abc123")
    result = manager.parse("https://example.com/share/abc123")
    print(f"  输出: success={result['success']}, url={result['url']}")
    
    # 应该经过两次解析：
    # 1. IntermediateParser (share -> m3u8, parse=1)
    # 2. DirectParser (m3u8 直链, parse=0)
    assert result["success"] == True
    assert result["url"] == "https://example.com/video.m3u8"
    assert result["parse"] == 0
    print("  ✅ 链式解析正确工作")
    
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("解析器架构测试")
    print("=" * 60)
    
    tests = [
        ("DirectParser", test_direct_parser),
        ("ParserManager", test_parser_manager),
        ("解析器优先级", test_parser_priority),
        ("链式解析", test_chain_parsing),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ {name} 测试失败: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: 通过 {passed}/{len(tests)}")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n❌ 有 {failed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())