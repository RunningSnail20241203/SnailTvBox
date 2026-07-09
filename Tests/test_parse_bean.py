# -*- coding: utf-8 -*-
"""
ParseBean 和 ConfigLoader parses 解析测试
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.parse_bean import ParseBean
from utils.config_loader import ConfigLoader


def test_parse_bean():
    """测试 ParseBean 数据模型"""
    print("=" * 60)
    print("测试 ParseBean")
    print("=" * 60)

    pb = ParseBean()
    pb.name = "测试解析"
    pb.type = 1
    pb.url = "https://jx.example.com/?url="
    pb.flag = ["qq", "腾讯", "iqiyi"]

    print(f"  name: {pb.name}")
    print(f"  type: {pb.type} ({pb.get_type_name()})")
    print(f"  url: {pb.url}")
    print(f"  flag: {pb.flag}")
    print(f"  has_flag('qq'): {pb.has_flag('qq')}")
    print(f"  has_flag('youku'): {pb.has_flag('youku')}")
    print(f"  match_url('https://v.qq.com/xxx'): {pb.match_url('https://v.qq.com/xxx')}")
    print(f"  match_url('https://youku.com/xxx'): {pb.match_url('https://youku.com/xxx')}")

    assert pb.has_flag("qq") == True
    assert pb.has_flag("youku") == False
    assert pb.match_url("https://v.qq.com/xxx") == True
    assert pb.match_url("https://youku.com/xxx") == False
    print("  ✅ ParseBean 测试通过")


def test_config_loader_parses():
    """测试 ConfigLoader 解析 parses 字段"""
    print("\n" + "=" * 60)
    print("测试 ConfigLoader 解析 parses")
    print("=" * 60)

    loader = ConfigLoader()
    result = loader.load_from_file(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "jsm.json"))

    assert result == True, "配置加载失败"
    assert len(loader.parses) > 0, "parses 为空"

    print(f"\n  解析到 {len(loader.parses)} 个解析源:")
    for i, pb in enumerate(loader.parses[:5]):
        print(f"    [{i+1}] {pb.name} (type={pb.type}, {pb.get_type_name()})")
        print(f"        url: {pb.url[:60]}...")
        if pb.flag:
            print(f"        flag: {pb.flag[:5]}...")

    # 验证第一个解析源
    first = loader.parses[0]
    assert first.name == "Json聚合"
    assert first.type == 3

    # 验证 type=0 的解析源
    type0_list = [p for p in loader.parses if p.type == 0]
    print(f"\n  type=0 (Web嗅探) 解析源: {len(type0_list)} 个")
    for pb in type0_list[:3]:
        print(f"    - {pb.name}: {pb.url[:50]}...")

    # 验证有 flag 的解析源
    flagged = [p for p in loader.parses if p.flag]
    print(f"\n  有 flag 限制的解析源: {len(flagged)} 个")
    for pb in flagged[:3]:
        print(f"    - {pb.name}: flag={pb.flag[:5]}...")

    print(f"\n  ✅ ConfigLoader parses 测试通过")


def main():
    try:
        test_parse_bean()
        test_config_loader_parses()
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())