# -*- coding: utf-8 -*-
"""
端到端集成测试
验证 JsonSpider 与命令行界面的集成
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import start_server, stop_server
from utils.config_loader import ConfigLoader
from spiders.json_spider import JsonSpider
from spiders import MockSpider
from models.source_bean import SourceBean


def test_source_types():
    """测试配置加载后视频源类型是否正确"""
    print("=" * 60)
    print("测试 1: 配置加载与视频源类型")
    print("=" * 60)

    config = ConfigLoader()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fty.json")
    config.load_from_file(config_path)

    sources = config.sites
    print(f"视频源总数: {len(sources)}")

    # 统计各类型数量
    type_count = {}
    for s in sources:
        t = s.type
        type_name = SourceBean().get_type_name() if False else {0: "xml", 1: "json", 3: "spider"}.get(t, f"unknown({t})")
        type_count[type_name] = type_count.get(type_name, 0) + 1

    print(f"各类型数量: {type_count}")

    # 第一个源应该是 json 类型的本地测试站
    first = sources[0]
    print(f"\n第一个视频源: {first.name}")
    print(f"  类型: {first.type} (json类型=1)")
    print(f"  API: {first.api}")
    assert first.type == 1, "第一个源应该是json类型"
    assert "localhost:8899" in first.api, "第一个源应该指向本地API"
    print("✅ 测试 1 通过")


def test_json_spider_integration():
    """测试 JsonSpider 与本地服务器的完整交互"""
    print("\n" + "=" * 60)
    print("测试 2: JsonSpider 完整流程测试")
    print("=" * 60)

    print("正在启动本地API服务器...")
    start_server(port=8899)

    try:
        spider = JsonSpider(api_url="http://localhost:8899/api.php")
        spider.init(context=None, extend="")

        # 1. 首页
        print("\n【步骤1】获取首页内容")
        home = spider.home_content()
        assert "class" in home, "首页应该有 class 字段"
        assert "list" in home, "首页应该有 list 字段"
        class_count = len(home["class"])
        list_count = len(home["list"])
        print(f"  分类数: {class_count}")
        print(f"  推荐视频数: {list_count}")
        assert class_count == 4, "应该有4个分类"
        assert list_count >= 5, "推荐视频应该不少于5个"

        # 2. 分类列表
        print("\n【步骤2】获取分类视频列表")
        cat = spider.category_content("1", "1")
        assert "list" in cat, "分类列表应该有 list 字段"
        assert "page" in cat, "分类列表应该有 page 字段"
        assert cat["page"] == 1, "当前页应该是1"
        assert cat["pagecount"] == 3, "应该有3页"
        assert len(cat["list"]) == 5, "每页应该有5个视频"
        first_vod = cat["list"][0]
        print(f"  当前页: {cat['page']}/{cat['pagecount']}")
        print(f"  本页视频数: {len(cat['list'])}")
        print(f"  第一个视频: {first_vod.get('vod_name', '未知')}")

        # 3. 翻页
        print("\n【步骤3】翻页测试")
        cat2 = spider.category_content("1", "2")
        assert cat2["page"] == 2, "当前页应该是2"
        print(f"  第2页视频数: {len(cat2['list'])}")

        # 4. 视频详情
        print("\n【步骤4】获取视频详情")
        vod_id = first_vod.get("vod_id", "1")
        detail = spider.detail_content([vod_id])
        assert "list" in detail, "详情应该有 list 字段"
        assert len(detail["list"]) >= 1, "应该返回至少1个视频详情"
        vod = detail["list"][0]
        print(f"  视频名称: {vod.get('vod_name', '未知')}")
        print(f"  导演: {vod.get('vod_director', '未知')}")
        print(f"  演员: {vod.get('vod_actor', '未知')}")
        print(f"  年份: {vod.get('vod_year', '未知')}")
        play_from = vod.get("vod_play_from", "")
        line_count = len(play_from.split("$")) if play_from else 0
        print(f"  播放线路数: {line_count}")
        assert "vod_content" in vod, "应该有简介"
        assert "vod_play_from" in vod, "应该有播放线路"
        assert "vod_play_url" in vod, "应该有播放地址"

        # 5. 搜索
        print("\n【步骤5】搜索功能")
        search = spider.search_content("流浪")
        assert "list" in search, "搜索结果应该有 list 字段"
        print(f"  关键词: '流浪'")
        print(f"  结果数: {len(search['list'])}")
        for vod in search["list"]:
            print(f"    - {vod.get('vod_name', '未知')}")
        assert len(search["list"]) >= 1, "搜索应该有结果"

        # 6. 空搜索
        print("\n【步骤6】无结果搜索")
        search2 = spider.search_content("不存在的视频xxx123")
        print(f"  结果数: {len(search2['list'])}")
        assert len(search2["list"]) == 0, "应该没有搜索结果"

        # 7. 播放地址
        print("\n【步骤7】播放地址接口")
        player = spider.player_content("无尽", vod_id)
        print(f"  返回: url={player.get('url', '')[:50]}..., parse={player.get('parse', 0)}")
        assert "url" in player, "应该返回 url 字段"
        assert "parse" in player, "应该返回 parse 字段"

        print("\n✅ 测试 2 通过")

    finally:
        print("\n正在停止服务器...")
        stop_server()


def test_spider_creation():
    """测试根据视频源类型创建对应爬虫"""
    print("\n" + "=" * 60)
    print("测试 3: 爬虫工厂模式（按类型创建）")
    print("=" * 60)

    def create_spider(source):
        """根据视频源类型创建对应爬虫"""
        if source.type == 1:
            from spiders.json_spider import JsonSpider
            return JsonSpider(api_url=source.api)
        else:
            from spiders import MockSpider
            return MockSpider()

    config = ConfigLoader()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fty.json")
    config.load_from_file(config_path)

    # 测试第1个源（json类型）
    s1 = config.sites[0]
    spider1 = create_spider(s1)
    print(f"源: {s1.name}, type={s1.type}")
    print(f"爬虫类型: {type(spider1).__name__}")
    assert isinstance(spider1, JsonSpider), "type=1 应该创建 JsonSpider"

    # 测试第2个源（spider类型）
    s2 = config.sites[1]
    spider2 = create_spider(s2)
    print(f"\n源: {s2.name}, type={s2.type}")
    print(f"爬虫类型: {type(spider2).__name__}")
    assert isinstance(spider2, MockSpider), "type=3 应该创建 MockSpider"

    print("\n✅ 测试 3 通过")


def test_error_handling():
    """测试错误处理能力"""
    print("\n" + "=" * 60)
    print("测试 4: 错误处理能力")
    print("=" * 60)

    # 测试无效的 API 地址
    spider = JsonSpider(api_url="http://invalid.local:9999/api.php")
    spider.timeout = 2  # 缩短超时时间

    print("测试无效API地址...")
    home = spider.home_content()
    print(f"  home_content 返回: class数量={len(home.get('class', []))}, list数量={len(home.get('list', []))}")
    assert "class" in home, "即使失败也应该返回正确的结构"
    assert "list" in home, "即使失败也应该返回正确的结构"

    cat = spider.category_content("1", "1")
    print(f"  category_content 返回: list数量={len(cat.get('list', []))}")
    assert "list" in cat, "即使失败也应该返回正确的结构"

    detail = spider.detail_content(["1"])
    print(f"  detail_content 返回: list数量={len(detail.get('list', []))}")
    assert "list" in detail, "即使失败也应该返回正确的结构"

    search = spider.search_content("test")
    print(f"  search_content 返回: list数量={len(search.get('list', []))}")
    assert "list" in search, "即使失败也应该返回正确的结构"

    print("\n✅ 测试 4 通过")


if __name__ == "__main__":
    tests = [
        test_source_types,
        test_json_spider_integration,
        test_spider_creation,
        test_error_handling,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n❌ {test.__name__} 失败: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"测试结果: 通过 {passed}, 失败 {failed}, 总计 {len(tests)}")
    print("=" * 60)

    if failed == 0:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n💔 有测试失败")
        sys.exit(1)
