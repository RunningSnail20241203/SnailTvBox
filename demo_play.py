# -*- coding: utf-8 -*-
"""
快速演示脚本：模拟用户操作，演示完整播放流程
自动选择：第1个源 → 电视剧 → 第1个视频 → 线路2(分享页) → 第1集 → 播放
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import start_server, stop_server
from parsers import ParserManager, DirectParser, JsVariableParser
from player import VideoPlayer
from spiders.json_spider import JsonSpider
from models.vod_info import VodInfo


def demo():
    print("=" * 70)
    print("TvBox Learn - 完整播放流程演示")
    print("=" * 70)

    # 启动服务器
    start_server()
    time.sleep(0.3)

    try:
        # 1. 创建爬虫
        print("\n📺 第1步：创建 JSON 接口爬虫")
        spider = JsonSpider("http://localhost:8899/api.php")
        spider.init(None, "")
        print("   ✅ 爬虫创建成功")

        # 2. 获取首页
        print("\n📋 第2步：获取首页数据")
        home_data = spider.home_content()
        categories = home_data.get("class", [])
        print(f"   ✅ {len(categories)} 个分类")
        for cat in categories:
            print(f"      - {cat['type_name']}")

        # 3. 进入电视剧分类
        print("\n🎬 第3步：进入电视剧分类")
        cat_data = spider.category_content("2", "1")
        vod_list = cat_data.get("list", [])
        print(f"   ✅ 第1页 {len(vod_list)} 个视频")
        for i, vod in enumerate(vod_list[:5]):
            print(f"      [{i+1}] {vod['vod_name']}  [{vod['vod_remarks']}]")

        # 4. 选第一个视频，看详情
        first_vod = vod_list[0]
        vod_id = first_vod["vod_id"]
        print(f"\n📖 第4步：查看视频详情 - {first_vod['vod_name']}")
        detail_data = spider.detail_content([vod_id])
        vod_dict = detail_data["list"][0]
        vod = VodInfo()
        vod.vod_id = vod_dict.get("vod_id", "")
        vod.vod_name = vod_dict.get("vod_name", "")
        vod.vod_play_from = vod_dict.get("vod_play_from", "")
        vod.vod_play_url = vod_dict.get("vod_play_url", "")
        play_list = vod.parse_play_list()
        print(f"   ✅ {len(play_list)} 条播放线路")
        for i, line in enumerate(play_list):
            print(f"      [{i+1}] {line['from']} ({len(line['episodes'])}集")

        # 5. 选择第2条线路（分享页），播放第1集
        line2 = play_list[1]
        ep1 = line2["episodes"][0]
        print(f"\n🔗 第5步：选择线路[{line2['from']} - {ep1['name']}")
        print(f"   原始地址: {ep1['url']}")

        # 6. 解析播放地址
        print("\n🔍 第6步：解析播放地址")
        parser_mgr = ParserManager()
        parser_mgr.register(DirectParser())
        parser_mgr.register(JsVariableParser())
        result = parser_mgr.parse(ep1["url"])
        if result["success"]:
            print(f"   ✅ 解析成功!")
            print(f"      真实地址: {result['url']}")
            print(f"      格式: {result.get('format', 'unknown')}")
        else:
            print(f"   ❌ 解析失败: {result['error']}")
            return False

        # 7. 播放
        print("\n🎥 第7步：启动播放器")
        player = VideoPlayer()
        players = player.detect_players()
        if not players:
            print("   ❌ 未检测到播放器")
            print(player.get_install_hint())
            return False
        
        print(f"   ✅ 检测到 {len(players)} 个播放器")
        play_result = player.play(result["url"])
        if play_result["success"]:
            print(f"\n🎉 {play_result['player']} 播放器已启动！")
            print("   视频正在播放中...")
        else:
            print(f"   ❌ 播放失败: {play_result['error']}")
            return False

        print("\n" + "=" * 70)
        print("🎉 演示完成！完整流程全部通过！")
        print("=" * 70)
        print("\n完整流程：")
        print("  JSON接口 → 爬虫 → 首页 → 分类 → 详情 → 线路 → 剧集")
        print("  分享页 → JsVariableParser解析 → m3u8地址 → VLC播放")

        return True

    finally:
        stop_server()


if __name__ == "__main__":
    try:
        success = demo()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        stop_server()
        sys.exit(1)