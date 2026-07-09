# -*- coding: utf-8 -*-
"""
JsonSpider 测试脚本
测试 JsonSpider 的各个接口功能
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spiders.json_spider import JsonSpider
from server.mock_api_server import start_server, stop_server, SERVER_PORT


def test_home_content(spider):
    """测试首页内容接口"""
    print("\n" + "=" * 60)
    print("测试 1: home_content - 首页内容")
    print("=" * 60)

    result = spider.home_content(filter=False)

    assert isinstance(result, dict), "返回值应该是 dict"
    assert "class" in result, "返回值应该包含 class 字段"
    assert "list" in result, "返回值应该包含 list 字段"
    assert isinstance(result["class"], list), "class 应该是 list"
    assert isinstance(result["list"], list), "list 应该是 list"

    print(f"  分类数量: {len(result['class'])}")
    for cat in result["class"]:
        print(f"    - {cat['type_id']}: {cat['type_name']}")

    print(f"  推荐视频数量: {len(result['list'])}")
    for i, vod in enumerate(result["list"][:3]):
        print(f"    {i+1}. {vod['vod_name']} ({vod['vod_remarks']})")

    if len(result["list"]) > 3:
        print(f"    ... 还有 {len(result['list']) - 3} 个视频")

    print("  ✅ home_content 测试通过")
    return True


def test_category_content(spider):
    """测试分类列表接口"""
    print("\n" + "=" * 60)
    print("测试 2: category_content - 分类视频列表")
    print("=" * 60)

    result = spider.category_content(tid="1", pg="1", filter=False)

    assert isinstance(result, dict), "返回值应该是 dict"
    assert "page" in result, "返回值应该包含 page 字段"
    assert "pagecount" in result, "返回值应该包含 pagecount 字段"
    assert "limit" in result, "返回值应该包含 limit 字段"
    assert "total" in result, "返回值应该包含 total 字段"
    assert "list" in result, "返回值应该包含 list 字段"
    assert isinstance(result["list"], list), "list 应该是 list"

    print(f"  分类ID: 1 (电影)")
    print(f"  当前页码: {result['page']}")
    print(f"  总页数: {result['pagecount']}")
    print(f"  每页数量: {result['limit']}")
    print(f"  总条数: {result['total']}")
    print(f"  本页视频数: {len(result['list'])}")

    for i, vod in enumerate(result["list"]):
        print(f"    {i+1}. {vod['vod_name']} ({vod['vod_remarks']})")

    assert result["page"] == 1, "当前页码应该是 1"
    assert result["total"] > 0, "总条数应该大于 0"
    assert len(result["list"]) > 0, "视频列表不应该为空"

    print("  ✅ category_content 测试通过")
    return True


def test_detail_content(spider):
    """测试视频详情接口"""
    print("\n" + "=" * 60)
    print("测试 3: detail_content - 视频详情")
    print("=" * 60)

    result = spider.detail_content(ids=["1", "2"])

    assert isinstance(result, dict), "返回值应该是 dict"
    assert "list" in result, "返回值应该包含 list 字段"
    assert isinstance(result["list"], list), "list 应该是 list"

    print(f"  请求视频ID: 1, 2")
    print(f"  返回详情数量: {len(result['list'])}")

    for vod in result["list"]:
        print(f"\n  视频: {vod['vod_name']}")
        print(f"    ID: {vod['vod_id']}")
        print(f"    导演: {vod['vod_director']}")
        print(f"    演员: {vod['vod_actor']}")
        print(f"    年份: {vod['vod_year']}")
        print(f"    地区: {vod['vod_area']}")
        print(f"    播放线路: {vod['vod_play_from']}")
        print(f"    简介: {vod['vod_content'][:50]}...")

        assert vod["vod_id"], "vod_id 不应该为空"
        assert vod["vod_name"], "vod_name 不应该为空"
        assert vod["vod_play_from"], "vod_play_from 不应该为空"
        assert vod["vod_play_url"], "vod_play_url 不应该为空"

    assert len(result["list"]) == 2, "应该返回 2 个视频详情"

    print("\n  ✅ detail_content 测试通过")
    return True


def test_search_content(spider):
    """测试搜索接口"""
    print("\n" + "=" * 60)
    print("测试 4: search_content - 搜索视频")
    print("=" * 60)

    keyword = "流浪"
    result = spider.search_content(key=keyword, quick=False, pg="1")

    assert isinstance(result, dict), "返回值应该是 dict"
    assert "page" in result, "返回值应该包含 page 字段"
    assert "pagecount" in result, "返回值应该包含 pagecount 字段"
    assert "list" in result, "返回值应该包含 list 字段"
    assert isinstance(result["list"], list), "list 应该是 list"

    print(f"  搜索关键词: {keyword}")
    print(f"  当前页码: {result['page']}")
    print(f"  总页数: {result['pagecount']}")
    print(f"  总条数: {result['total']}")
    print(f"  本页结果数: {len(result['list'])}")

    for i, vod in enumerate(result["list"]):
        print(f"    {i+1}. {vod['vod_name']} ({vod['vod_remarks']})")
        assert keyword in vod["vod_name"], f"搜索结果应该包含关键词 '{keyword}'"

    assert result["total"] > 0, "搜索结果应该大于 0"

    print("  ✅ search_content 测试通过")
    return True


def test_player_content(spider):
    """测试播放地址接口"""
    print("\n" + "=" * 60)
    print("测试 5: player_content - 播放地址")
    print("=" * 60)

    result = spider.player_content(flag="无尽", id="1")

    assert isinstance(result, dict), "返回值应该是 dict"
    assert "url" in result, "返回值应该包含 url 字段"
    assert "parse" in result, "返回值应该包含 parse 字段"
    assert "jx" in result, "返回值应该包含 jx 字段"

    print(f"  线路: 无尽, 视频ID: 1")
    print(f"  返回: url='{result['url']}', parse={result['parse']}, jx={result['jx']}")
    print("  说明: type=1 数据源播放地址在详情中返回，player_content 返回空结构")

    print("  ✅ player_content 测试通过")
    return True


def test_empty_api_url():
    """测试空 API URL 的情况"""
    print("\n" + "=" * 60)
    print("测试 6: 空 API URL 容错")
    print("=" * 60)

    spider = JsonSpider(api_url="")

    home = spider.home_content()
    assert home["class"] == [], "空 API 时 class 应该为空列表"
    assert home["list"] == [], "空 API 时 list 应该为空列表"

    category = spider.category_content(tid="1", pg="1")
    assert category["list"] == [], "空 API 时分类列表应该为空"

    detail = spider.detail_content(ids=["1"])
    assert detail["list"] == [], "空 API 时详情应该为空"

    search = spider.search_content(key="test")
    assert search["list"] == [], "空 API 时搜索结果应该为空"

    print("  空 API URL 时所有接口都返回正确的空结构")
    print("  ✅ 空 API URL 容错测试通过")
    return True


def main():
    """主测试函数"""
    print("=" * 60)
    print("  JsonSpider 测试")
    print("=" * 60)

    print("\n[步骤 1] 启动模拟 API 服务器...")
    server_started = start_server(port=SERVER_PORT)
    if not server_started:
        print("  服务器启动失败，尝试继续测试...")

    import time
    time.sleep(0.5)

    api_url = f"http://localhost:{SERVER_PORT}/api.php"
    print(f"\n[步骤 2] 创建 JsonSpider，API 地址: {api_url}")
    spider = JsonSpider(api_url=api_url)

    passed = 0
    failed = 0
    tests = [
        ("home_content", test_home_content, True),
        ("category_content", test_category_content, True),
        ("detail_content", test_detail_content, True),
        ("search_content", test_search_content, True),
        ("player_content", test_player_content, True),
        ("empty_api_url", test_empty_api_url, False),
    ]

    for name, test_func, need_spider in tests:
        try:
            if need_spider:
                test_func(spider)
            else:
                test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n  ❌ {name} 测试失败: {e}")
            failed += 1
        except Exception as e:
            print(f"\n  ❌ {name} 测试发生异常: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print("  测试总结")
    print("=" * 60)
    print(f"  通过: {passed}")
    print(f"  失败: {failed}")
    print(f"  总计: {len(tests)}")

    print("\n[步骤 3] 停止模拟 API 服务器...")
    stop_server()

    if failed == 0:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  有 {failed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
