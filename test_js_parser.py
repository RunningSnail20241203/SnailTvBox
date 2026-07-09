# -*- coding: utf-8 -*-
"""
JsVariableParser 真实地址测试

测试从 phimgood.com 分享页提取播放地址
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsers import JsVariableParser, DirectParser, ParserManager


def test_real_url():
    """测试真实分享页地址"""
    print("=" * 70)
    print("JsVariableParser 真实地址测试")
    print("=" * 70)
    
    # 用户提供的真实地址
    test_url = "https://play.phimgood.com/share/fe53ff5f33342773a12c81d85fb0a090"
    
    # 创建解析器
    parser = JsVariableParser()
    
    print(f"\n测试地址: {test_url}")
    print(f"can_parse: {parser.can_parse(test_url)}")
    
    # 执行解析
    print("\n正在解析...")
    result = parser.parse(test_url)
    
    print("\n解析结果:")
    print(f"  成功: {result['success']}")
    print(f"  地址: {result['url']}")
    print(f"  标题: {result['title']}")
    print(f"  封面: {result['pic']}")
    print(f"  格式: {result['format']}")
    
    if not result['success']:
        print(f"  错误: {result['error']}")
        return False
    
    # 验证地址是 m3u8
    if ".m3u8" in result['url']:
        print("\n✅ 成功提取 m3u8 播放地址！")
    else:
        print(f"\n⚠️ 提取的地址格式异常: {result['url']}")
    
    return True


def test_parser_manager():
    """测试 ParserManager 链式解析"""
    print("\n" + "=" * 70)
    print("ParserManager 链式解析测试")
    print("=" * 70)
    
    manager = ParserManager()
    manager.register(DirectParser())        # priority=10
    manager.register(JsVariableParser())    # priority=30
    
    # 测试直链
    print("\n测试1: 直链地址")
    result1 = manager.parse("https://example.com/video.m3u8")
    print(f"  结果: success={result1['success']}, url={result1['url']}")
    assert result1['success']
    
    # 测试分享页
    print("\n测试2: 分享页地址")
    test_url = "https://play.phimgood.com/share/fe53ff5f33342773a12c81d85fb0a090"
    result2 = manager.parse(test_url)
    print(f"  结果: success={result2['success']}")
    if result2['success']:
        print(f"  地址: {result2['url']}")
        print(f"  标题: {result2['title']}")
    else:
        print(f"  错误: {result2['error']}")
    
    return True


def main():
    print("\n" + "=" * 70)
    print("真实地址解析测试")
    print("=" * 70)
    
    try:
        test_real_url()
        test_parser_manager()
        print("\n" + "=" * 70)
        print("✅ 测试完成")
        print("=" * 70)
        return 0
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())