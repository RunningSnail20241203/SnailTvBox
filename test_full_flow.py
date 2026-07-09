# -*- coding: utf-8 -*-
"""
端到端测试：从选视频到播放的完整流程
"""

import sys
import os
import time
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import start_server, stop_server
from parsers import ParserManager, DirectParser, JsVariableParser
from player import VideoPlayer
from spiders.json_spider import JsonSpider
from models.vod_info import VodInfo


def test_full_flow():
    """测试完整流程"""
    print("=" * 70)
    print("端到端测试：完整播放流程")
    print("=" * 70)

    # 步骤1：启动 Mock API 服务器
    print("\n[1/6] 启动 Mock API 服务器...")
    start_server()
    time.sleep(0.5)  # 等服务器启动
    print("✅ 服务器已启动")

    # 步骤2：创建 JsonSpider
    print("\n[2/6] 创建 JSON 接口爬虫...")
    spider = JsonSpider("http://localhost:8899/api.php")
    spider.init(None, "")
    print("✅ 爬虫创建成功")

    # 步骤3：获取首页数据
    print("\n[3/6] 获取首页数据...")
    home_data = spider.home_content()
    categories = home_data.get("class", [])
    recommend = home_data.get("list", [])
    print(f"✅ 获取到 {len(categories)} 个分类，{len(recommend)} 个推荐")

    # 步骤4：选一个电视剧，获取详情
    print("\n[4/6] 获取视频详情...")
    # 找电视剧分类
    tv_cat = None
    for cat in categories:
        if cat["type_id"] == "2":
            tv_cat = cat
            break
    
    if not tv_cat:
        print("❌ 找不到电视剧分类")
        stop_server()
        return False

    # 获取分类列表
    cat_data = spider.category_content("2", "1")
    vod_list = cat_data.get("list", [])
    if not vod_list:
        print("❌ 分类列表为空")
        stop_server()
        return False
    
    # 获取第一个视频的详情
    first_vod = vod_list[0]
    vod_id = first_vod["vod_id"]
    print(f"   选择视频: {first_vod['vod_name']} (ID: {vod_id})")
    
    detail_data = spider.detail_content([vod_id])
    if not detail_data.get("list"):
        print("❌ 获取详情失败")
        stop_server()
        return False
    
    vod_dict = detail_data["list"][0]
    vod = VodInfo()
    vod.vod_id = vod_dict.get("vod_id", "")
    vod.vod_name = vod_dict.get("vod_name", "")
    vod.vod_play_from = vod_dict.get("vod_play_from", "")
    vod.vod_play_url = vod_dict.get("vod_play_url", "")
    
    play_list = vod.parse_play_list()
    print(f"✅ 获取到 {len(play_list)} 条播放线路")
    for i, line in enumerate(play_list):
        print(f"   [{i+1}] {line['from']} ({len(line['episodes'])}集)")

    # 步骤5：测试解析器 - 直链（无尽线路）
    print("\n[5/6] 测试解析器...")
    parser_mgr = ParserManager()
    parser_mgr.register(DirectParser())
    parser_mgr.register(JsVariableParser())
    
    # 测试直链（无尽线路）
    wujin_line = play_list[0]
    ep1_url = wujin_line["episodes"][0]["url"]
    print(f"\n   测试线路1（直链）: {wujin_line['from']}")
    print(f"   原始地址: {ep1_url}")
    result1 = parser_mgr.parse(ep1_url)
    print(f"   解析结果: success={result1['success']}, format={result1['format']}")
    print(f"   真实地址: {result1['url']}")
    assert result1["success"] == True, "直链解析失败"
    assert result1["format"] == "m3u8", "格式应该是 m3u8"
    print("   ✅ 直链解析通过")
    
    # 测试分享页（闪电线路）
    shandian_line = play_list[1]
    ep1_share_url = shandian_line["episodes"][0]["url"]
    print(f"\n   测试线路2（分享页）: {shandian_line['from']}")
    print(f"   原始地址: {ep1_share_url}")
    result2 = parser_mgr.parse(ep1_share_url)
    print(f"   解析结果: success={result2['success']}, format={result2.get('format', 'unknown')}")
    if result2["success"]:
        print(f"   真实地址: {result2['url']}")
        assert result2["format"] == "m3u8", "格式应该是 m3u8"
        print("   ✅ 分享页解析通过")
    else:
        print(f"   ❌ 解析失败: {result2.get('error', '未知错误')}")
        stop_server()
        return False

    # 步骤6：测试播放器（检测）
    print("\n[6/6] 测试播放器检测...")
    player = VideoPlayer()
    players = player.detect_players()
    print(f"   检测到 {len(players)} 个播放器")
    for p in players:
        print(f"   - {p['name']}: {p['path']}")
    
    if players:
        print("   ✅ 播放器检测通过")
    else:
        print("   ⚠️  未检测到播放器（需要安装 VLC 或 mpv 才能播放）")
        print(player.get_install_hint())

    # 总结
    print("\n" + "=" * 70)
    print("🎉 端到端测试通过！")
    print("=" * 70)
    print("\n完整流程:")
    print("  视频源 → 分类 → 视频详情 → 播放线路 → 剧集 → 解析地址 → 播放")
    print("\n两个线路都解析成功:")
    print(f"  ✅ 无尽线路（直链）: {result1['format']}")
    print(f"  ✅ 闪电线路（分享页）: {result2['format']}")
    
    stop_server()
    return True


def main():
    try:
        success = test_full_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        stop_server()
        sys.exit(1)


if __name__ == "__main__":
    main()