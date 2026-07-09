# -*- coding: utf-8 -*-
"""
播放器模块测试

测试播放器检测和播放功能。
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from player import VideoPlayer


def test_detect_players():
    """测试播放器检测"""
    print("=" * 60)
    print("测试播放器检测")
    print("=" * 60)
    
    player = VideoPlayer()
    players = player.detect_players()
    
    print(f"\n检测到 {len(players)} 个播放器:")
    for p in players:
        print(f"  - {p['name']}: {p['path']}")
    
    if not players:
        print("\n未检测到播放器")
        print(player.get_install_hint())
    else:
        print(f"\n默认播放器: {player.get_default_player()['name']}")
    
    return True


def test_play_real_url():
    """测试播放真实地址"""
    print("\n" + "=" * 60)
    print("测试播放真实视频地址")
    print("=" * 60)
    
    # 从分享页解析出的真实地址
    url = "https://play.phimgood.com/20260709/28754_fe53ff5f/index.m3u8?sign=00900674ce592c0d41de2b1a9339aaf4"
    
    player = VideoPlayer()
    
    if not player.has_player():
        print("\n没有可用的播放器")
        print(player.get_install_hint())
        return False
    
    print(f"\n正在播放:")
    print(f"  地址: {url}")
    print(f"  格式: m3u8")
    
    result = player.play(url)
    
    if result["success"]:
        print(f"\n✅ {result['player']} 播放器已启动！")
        print("  播放器在独立窗口运行，可以关闭本程序。")
    else:
        print(f"\n❌ 播放失败: {result['error']}")
    
    return result["success"]


def main():
    """运行测试"""
    print("\n" + "=" * 60)
    print("播放器模块测试")
    print("=" * 60)
    
    test_detect_players()
    
    print("\n" + "-" * 60)
    input("按回车继续测试真实播放...")
    test_play_real_url()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()