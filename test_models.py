# -*- coding: utf-8 -*-
"""
单元测试脚本
测试 SourceBean、VodInfo、MockSpider、ConfigLoader 的基本功能
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.source_bean import SourceBean
from models.vod_info import VodInfo
from spiders.mock_spider import MockSpider
from utils.config_loader import ConfigLoader


def test_source_bean():
    """测试 SourceBean：创建对象、设置字段、读取字段"""
    print("\n" + "=" * 60)
    print("测试 SourceBean")
    print("=" * 60)

    try:
        source = SourceBean()

        source.key = "test_key"
        source.name = "测试视频源"
        source.api = "https://api.test.com/vod/"
        source.type = 3
        source.searchable = 1
        source.quickSearch = 1
        source.filterable = 1
        source.playerUrl = "https://player.test.com"
        source.ext = {"ua": "test_ua"}
        source.jar = "test.jar"
        source.playerType = 1
        source.timeout = 10
        source.style = {"theme": "dark"}

        assert source.key == "test_key", f"key 不匹配: {source.key}"
        assert source.name == "测试视频源", f"name 不匹配: {source.name}"
        assert source.api == "https://api.test.com/vod/", f"api 不匹配: {source.api}"
        assert source.type == 3, f"type 不匹配: {source.type}"
        assert source.searchable == 1, f"searchable 不匹配: {source.searchable}"
        assert source.quickSearch == 1, f"quickSearch 不匹配: {source.quickSearch}"
        assert source.filterable == 1, f"filterable 不匹配: {source.filterable}"
        assert source.playerUrl == "https://player.test.com", f"playerUrl 不匹配: {source.playerUrl}"
        assert '"ua": "test_ua"' in source.ext, f"ext 不匹配: {source.ext}"
        assert source.jar == "test.jar", f"jar 不匹配: {source.jar}"
        assert source.playerType == 1, f"playerType 不匹配: {source.playerType}"
        assert source.timeout == 10, f"timeout 不匹配: {source.timeout}"
        assert '"theme": "dark"' in source.style, f"style 不匹配: {source.style}"

        assert source.get_type_name() == "spider", f"type_name 不匹配: {source.get_type_name()}"

        source.type = 0
        assert source.get_type_name() == "xml", f"type_name 不匹配: {source.get_type_name()}"

        source.type = 1
        assert source.get_type_name() == "json", f"type_name 不匹配: {source.get_type_name()}"

        source.type = 99
        assert "unknown(99)" in source.get_type_name(), f"type_name 不匹配: {source.get_type_name()}"

        source.type = "invalid"
        assert source.type == 0, f"非法 type 应默认为 0: {source.type}"

        source.key = None
        assert source.key == "", f"None 值应转为空字符串: {source.key}"

        str_repr = str(source)
        assert "SourceBean" in str_repr, f"__str__ 应包含 SourceBean: {str_repr}"

        print("✅ test_source_bean 通过")
        return True

    except Exception as e:
        print(f"❌ test_source_bean 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vod_info():
    """测试 VodInfo：创建对象、解析播放线路"""
    print("\n" + "=" * 60)
    print("测试 VodInfo")
    print("=" * 60)

    try:
        vod = VodInfo()

        vod.vod_id = "vod_001"
        vod.vod_name = "测试电影"
        vod.vod_pic = "https://picsum.photos/300/420.jpg"
        vod.vod_remarks = "HD"
        vod.vod_year = "2024"
        vod.vod_area = "大陆"
        vod.vod_director = "张艺谋"
        vod.vod_actor = "吴京,刘德华"
        vod.vod_content = "这是一部测试电影。"

        assert vod.vod_id == "vod_001", f"vod_id 不匹配: {vod.vod_id}"
        assert vod.vod_name == "测试电影", f"vod_name 不匹配: {vod.vod_name}"
        assert vod.vod_pic == "https://picsum.photos/300/420.jpg", f"vod_pic 不匹配: {vod.vod_pic}"
        assert vod.vod_remarks == "HD", f"vod_remarks 不匹配: {vod.vod_remarks}"
        assert vod.vod_year == "2024", f"vod_year 不匹配: {vod.vod_year}"
        assert vod.vod_area == "大陆", f"vod_area 不匹配: {vod.vod_area}"
        assert vod.vod_director == "张艺谋", f"vod_director 不匹配: {vod.vod_director}"
        assert vod.vod_actor == "吴京,刘德华", f"vod_actor 不匹配: {vod.vod_actor}"
        assert vod.vod_content == "这是一部测试电影。", f"vod_content 不匹配: {vod.vod_content}"

        vod.vod_play_from = "无尽$闪电$量子"
        vod.vod_play_url = "第1集@https://url1.m3u8#第2集@https://url2.m3u8$第1集@https://url3.m3u8#第2集@https://url4.m3u8$第1集@https://url5.m3u8"

        line_count = vod.get_line_count()
        assert line_count == 3, f"线路数量应为 3，实际: {line_count}"

        play_list = vod.parse_play_list()
        assert len(play_list) == 3, f"解析后线路数量应为 3，实际: {len(play_list)}"

        assert play_list[0]["from"] == "无尽", f"线路1名称不匹配: {play_list[0]['from']}"
        assert len(play_list[0]["episodes"]) == 2, f"线路1剧集数应为 2，实际: {len(play_list[0]['episodes'])}"
        assert play_list[0]["episodes"][0]["name"] == "第1集", f"剧集名不匹配: {play_list[0]['episodes'][0]['name']}"
        assert play_list[0]["episodes"][0]["url"] == "https://url1.m3u8", f"剧集URL不匹配: {play_list[0]['episodes'][0]['url']}"

        assert play_list[1]["from"] == "闪电", f"线路2名称不匹配: {play_list[1]['from']}"
        assert play_list[2]["from"] == "量子", f"线路3名称不匹配: {play_list[2]['from']}"

        vod_empty = VodInfo()
        assert vod_empty.get_line_count() == 0, "空对象线路数应为 0"
        assert vod_empty.parse_play_list() == [], "空对象播放列表应为空数组"

        str_repr = str(vod)
        assert "VodInfo" in str_repr, f"__str__ 应包含 VodInfo: {str_repr}"

        print("✅ test_vod_info 通过")
        return True

    except Exception as e:
        print(f"❌ test_vod_info 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mock_spider():
    """测试 MockSpider：home_content、category_content、detail_content、search_content 返回的数据结构是否正确"""
    print("\n" + "=" * 60)
    print("测试 MockSpider")
    print("=" * 60)

    try:
        spider = MockSpider()

        spider.init(None, "")

        home_data = spider.home_content()
        assert "class" in home_data, "home_content 应包含 class 字段"
        assert "list" in home_data, "home_content 应包含 list 字段"
        assert isinstance(home_data["class"], list), "class 应为列表"
        assert isinstance(home_data["list"], list), "list 应为列表"
        assert len(home_data["class"]) == 5, f"分类数量应为 5，实际: {len(home_data['class'])}"
        assert len(home_data["list"]) >= 1, f"推荐视频数量应 >= 1，实际: {len(home_data['list'])}"

        first_cat = home_data["class"][0]
        assert "type_id" in first_cat, "分类应包含 type_id"
        assert "type_name" in first_cat, "分类应包含 type_name"

        first_vod = home_data["list"][0]
        assert "vod_id" in first_vod, "视频应包含 vod_id"
        assert "vod_name" in first_vod, "视频应包含 vod_name"
        assert "vod_pic" in first_vod, "视频应包含 vod_pic"
        assert "vod_remarks" in first_vod, "视频应包含 vod_remarks"

        home_videos = spider.home_video_content()
        assert isinstance(home_videos, list), "home_video_content 应返回列表"
        assert len(home_videos) > 0, "home_video_content 应返回数据"

        cat_data = spider.category_content("1", "1")
        assert "page" in cat_data, "category_content 应包含 page"
        assert "pagecount" in cat_data, "category_content 应包含 pagecount"
        assert "limit" in cat_data, "category_content 应包含 limit"
        assert "total" in cat_data, "category_content 应包含 total"
        assert "list" in cat_data, "category_content 应包含 list"
        assert cat_data["page"] == 1, f"页码应为 1，实际: {cat_data['page']}"
        assert cat_data["total"] == 12, f"电影分类应有 12 个视频，实际: {cat_data['total']}"
        assert len(cat_data["list"]) <= 6, f"每页最多 6 个，实际: {len(cat_data['list'])}"

        cat_data_page2 = spider.category_content("1", "2")
        assert cat_data_page2["page"] == 2, f"第2页 page 应为 2，实际: {cat_data_page2['page']}"
        assert len(cat_data_page2["list"]) > 0, "第2页应有数据"

        first_vod_id = cat_data["list"][0]["vod_id"]
        detail_data = spider.detail_content([first_vod_id])
        assert "list" in detail_data, "detail_content 应包含 list"
        assert len(detail_data["list"]) == 1, f"应返回 1 个详情，实际: {len(detail_data['list'])}"

        vod_detail = detail_data["list"][0]
        assert "vod_id" in vod_detail, "详情应包含 vod_id"
        assert "vod_name" in vod_detail, "详情应包含 vod_name"
        assert "vod_pic" in vod_detail, "详情应包含 vod_pic"
        assert "vod_content" in vod_detail, "详情应包含 vod_content"
        assert "vod_director" in vod_detail, "详情应包含 vod_director"
        assert "vod_actor" in vod_detail, "详情应包含 vod_actor"
        assert "vod_year" in vod_detail, "详情应包含 vod_year"
        assert "vod_area" in vod_detail, "详情应包含 vod_area"
        assert "vod_remarks" in vod_detail, "详情应包含 vod_remarks"
        assert "vod_play_from" in vod_detail, "详情应包含 vod_play_from"
        assert "vod_play_url" in vod_detail, "详情应包含 vod_play_url"

        search_data = spider.search_content("流浪")
        assert "page" in search_data, "search_content 应包含 page"
        assert "pagecount" in search_data, "search_content 应包含 pagecount"
        assert "limit" in search_data, "search_content 应包含 limit"
        assert "total" in search_data, "search_content 应包含 total"
        assert "list" in search_data, "search_content 应包含 list"
        assert search_data["total"] >= 1, f"搜索'流浪'应至少有 1 个结果，实际: {search_data['total']}"

        search_data_none = spider.search_content("不存在的关键词12345")
        assert search_data_none["total"] == 0, f"搜索不存在的关键词应返回 0 结果，实际: {search_data_none['total']}"

        first_line_name = vod_detail["vod_play_from"].split("$")[0]
        player_data = spider.player_content(first_line_name, first_vod_id)
        assert "url" in player_data, "player_content 应包含 url"
        assert "parse" in player_data, "player_content 应包含 parse"
        assert "jx" in player_data, "player_content 应包含 jx"
        assert player_data["url"] != "", "播放地址不应为空"

        player_data_invalid = spider.player_content("不存在的线路", first_vod_id)
        assert player_data_invalid["url"] == "", "无效线路返回空地址"

        player_data_no_vod = spider.player_content(first_line_name, "不存在的ID")
        assert player_data_no_vod["url"] == "", "无效视频ID返回空地址"

        print("✅ test_mock_spider 通过")
        return True

    except Exception as e:
        print(f"❌ test_mock_spider 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_loader():
    """测试 ConfigLoader：加载本地 fty.json，验证视频源数量"""
    print("\n" + "=" * 60)
    print("测试 ConfigLoader")
    print("=" * 60)

    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fty.json")

        assert os.path.exists(config_path), f"配置文件不存在: {config_path}"

        loader = ConfigLoader()

        result = loader.load_from_file(config_path)
        assert result, "加载配置文件应返回 True"

        assert len(loader.sites) == 48, f"视频源数量应为 48，实际: {len(loader.sites)}"

        first_site = loader.sites[0]
        assert isinstance(first_site, SourceBean), "视频源应为 SourceBean 类型"
        assert first_site.key != "", "第一个视频源 key 不应为空"
        assert first_site.name != "", "第一个视频源 name 不应为空"

        assert len(loader.lives) > 0, "直播源列表不应为空"

        site_by_key = loader.get_site_by_key("site_001")
        assert site_by_key is not None, "应能通过 key 找到视频源"
        assert site_by_key.key == "site_001", f"找到的视频源 key 不匹配: {site_by_key.key}"

        site_by_key_none = loader.get_site_by_key("nonexistent_key")
        assert site_by_key_none is None, "不存在的 key 应返回 None"

        spider_sites = loader.get_sites_by_type(3)
        assert len(spider_sites) > 0, "应存在 spider 类型的视频源"
        for s in spider_sites:
            assert s.type == 3, f"类型应为 3 (spider)，实际: {s.type}"

        json_sites = loader.get_sites_by_type(1)
        assert len(json_sites) > 0, "应存在 json 类型的视频源"

        xml_sites = loader.get_sites_by_type(0)
        assert len(xml_sites) > 0, "应存在 xml 类型的视频源"

        assert isinstance(loader.config_data, dict), "config_data 应为字典"
        assert "sites" in loader.config_data, "config_data 应包含 sites"

        result_invalid = loader.load_from_file("nonexistent_file.json")
        assert not result_invalid, "加载不存在的文件应返回 False"

        print("✅ test_config_loader 通过")
        return True

    except Exception as e:
        print(f"❌ test_config_loader 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("TvBox Learn - 单元测试")
    print("=" * 60)

    tests = [
        ("SourceBean", test_source_bean),
        ("VodInfo", test_vod_info),
        ("MockSpider", test_mock_spider),
        ("ConfigLoader", test_config_loader),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        if test_func():
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {len(tests)}")

    if failed == 0:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查。")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
