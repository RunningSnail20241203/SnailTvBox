# -*- coding: utf-8 -*-
"""
Parses 解析器系统演示

演示从 TvBox 配置加载 parses，并展示解析器的工作原理。
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config_loader import ConfigLoader
from utils.parses_loader import ParsesLoader
from parsers import ParserManager, DirectParser


def demo():
    print("=" * 70)
    print("TvBox Parses 解析器系统演示")
    print("=" * 70)

    # 步骤1：加载配置
    print("\n📋 步骤1：加载 TvBox 配置文件")
    loader = ConfigLoader()
    loader.load_from_file("jsm.json")

    print(f"   视频源数量: {len(loader.sites)}")
    print(f"   直播源数量: {len(loader.lives)}")
    print(f"   解析源数量: {len(loader.parses)}")

    # 步骤2：查看解析源详情
    print("\n🔍 步骤2：查看 parses 配置")
    print("-" * 70)

    # 按类型分组统计
    type_counts = {}
    for pb in loader.parses:
        t = pb.get_type_name()
        type_counts[t] = type_counts.get(t, 0) + 1

    print("  解析源类型分布:")
    for t, count in type_counts.items():
        print(f"    - {t}: {count} 个")

    # 显示前5个解析源
    print("\n  前 5 个解析源详情:")
    for i, pb in enumerate(loader.parses[:5]):
        print(f"    [{i+1}] {pb.name}")
        print(f"        type: {pb.type} ({pb.get_type_name()})")
        print(f"        url: {pb.url[:50]}...")
        if pb.flag:
            print(f"        flag: {pb.flag[:5]}")

    # 步骤3：加载到 ParserManager
    print("\n⚙️  步骤3：将解析源加载到 ParserManager")
    print("-" * 70)

    manager = ParserManager()
    manager.register(DirectParser())  # 先注册直链解析器

    count = ParsesLoader.load_from_config(loader, manager)
    print(f"\n  ParserManager 中共有 {len(manager.get_parsers())} 个解析器")

    # 步骤4：测试解析器匹配
    print("\n🧪 步骤4：测试解析器匹配")
    print("-" * 70)

    test_urls = [
        ("https://v.qq.com/x/cover/xxx.html", "腾讯视频页面"),
        ("https://www.iqiyi.com/v_xxx.html", "爱奇艺页面"),
        ("https://v.youku.com/v_show/xxx.html", "优酷页面"),
        ("https://example.com/video.m3u8", "直链 m3u8"),
        ("https://example.com/share/abc123", "分享页"),
    ]

    for url, desc in test_urls:
        can = manager.can_parse(url)
        status = "✅ 可解析" if can else "❌ 无匹配解析器"
        print(f"  {desc}")
        print(f"    URL: {url[:50]}...")
        print(f"    结果: {status}")
        print()

    # 步骤5：flag 匹配详细演示
    print("🔍 步骤5：flag 匹配机制演示")
    print("-" * 70)

    # 找有 flag 的解析源
    flagged = [p for p in loader.parses if p.flag]
    if flagged:
        print(f"  有 {len(flagged)} 个解析源设置了 flag（平台限制）")
        print("\n  示例：")
        for pb in flagged[:3]:
            print(f"    {pb.name}: flag={pb.flag[:5]}")
            print(f"      → 只解析包含这些关键词的 URL")
    else:
        print("  所有解析源都没有 flag 限制（万能解析）")

    # 找无 flag 的解析源
    universal = [p for p in loader.parses if not p.flag]
    print(f"\n  有 {len(universal)} 个解析源无 flag 限制（万能解析）")
    for pb in universal[:3]:
        print(f"    {pb.name}: 适用于所有 URL")

    print("\n" + "=" * 70)
    print("🎉 演示完成！")
    print("=" * 70)
    print("\n总结：")
    print(f"  - 配置文件中有 {len(loader.parses)} 个解析源")
    print(f"  - 成功注册到 ParserManager: {count} 个")
    print(f"  - 支持类型: Web嗅探(type=0), JSON接口(type=1), Spider(type=3)")
    print(f"  - 通过 flag 实现平台匹配，精准选择解析器")


if __name__ == "__main__":
    demo()