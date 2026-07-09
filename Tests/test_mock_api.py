"""
模拟 API 服务器测试脚本
验证各个接口的返回数据格式是否正确
"""

import sys
import os
import json
import time
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.mock_api_server import start_server, stop_server, SERVER_PORT

BASE_URL = f"http://localhost:{SERVER_PORT}"


def test_home_page():
    """
    测试首页接口: GET /api.php?ac=list
    """
    print("\n" + "=" * 60)
    print("测试 1: 首页接口")
    print("=" * 60)

    url = f"{BASE_URL}/api.php?ac=list"
    resp = requests.get(url)

    print(f"请求 URL: {url}")
    print(f"状态码: {resp.status_code}")
    print(f"Content-Type: {resp.headers.get('Content-Type')}")

    assert resp.status_code == 200, "状态码应为 200"
    assert "application/json" in resp.headers.get("Content-Type", ""), "Content-Type 应为 application/json"

    data = resp.json()
    print(f"\n返回数据 keys: {list(data.keys())}")

    # 验证分类
    assert "class" in data, "应包含 class 字段"
    assert isinstance(data["class"], list), "class 应为列表"
    assert len(data["class"]) == 4, "应有 4 个分类"
    print(f"分类数量: {len(data['class'])}")
    for cat in data["class"]:
        assert "type_id" in cat, "分类应包含 type_id"
        assert "type_name" in cat, "分类应包含 type_name"
        print(f"  - {cat['type_id']}: {cat['type_name']}")

    # 验证推荐列表
    assert "list" in data, "应包含 list 字段"
    assert isinstance(data["list"], list), "list 应为列表"
    print(f"推荐视频数量: {len(data['list'])}")

    if data["list"]:
        vod = data["list"][0]
        print(f"\n第一个视频字段: {list(vod.keys())}")
        assert "vod_id" in vod, "视频应包含 vod_id"
        assert "vod_name" in vod, "视频应包含 vod_name"
        assert "vod_pic" in vod, "视频应包含 vod_pic"
        assert "vod_remarks" in vod, "视频应包含 vod_remarks"
        print(f"  vod_id: {vod['vod_id']}")
        print(f"  vod_name: {vod['vod_name']}")
        print(f"  vod_pic: {vod['vod_pic']}")
        print(f"  vod_remarks: {vod['vod_remarks']}")

    print("✅ 首页接口测试通过")


def test_category_list():
    """
    测试分类列表接口: GET /api.php?ac=detail&t={tid}&pg={pg}
    """
    print("\n" + "=" * 60)
    print("测试 2: 分类列表接口")
    print("=" * 60)

    # 测试电影分类第1页
    url = f"{BASE_URL}/api.php?ac=detail&t=1&pg=1"
    resp = requests.get(url)

    print(f"请求 URL: {url}")
    print(f"状态码: {resp.status_code}")

    assert resp.status_code == 200, "状态码应为 200"

    data = resp.json()
    print(f"\n返回数据 keys: {list(data.keys())}")

    # 验证分页字段
    assert "page" in data, "应包含 page 字段"
    assert "pagecount" in data, "应包含 pagecount 字段"
    assert "limit" in data, "应包含 limit 字段"
    assert "total" in data, "应包含 total 字段"
    assert "list" in data, "应包含 list 字段"

    print(f"当前页: {data['page']}")
    print(f"总页数: {data['pagecount']}")
    print(f"每页数量: {data['limit']}")
    print(f"总数: {data['total']}")
    print(f"当前页列表长度: {len(data['list'])}")

    assert data["page"] == 1, "当前页应为 1"
    assert data["limit"] == 5, "每页数量应为 5"
    assert data["total"] == 15, "电影分类应有 15 个视频"
    assert data["pagecount"] == 3, "应有 3 页"
    assert len(data["list"]) == 5, "第1页应有 5 个视频"

    # 测试第2页
    url2 = f"{BASE_URL}/api.php?ac=detail&t=1&pg=2"
    resp2 = requests.get(url2)
    data2 = resp2.json()
    assert data2["page"] == 2, "当前页应为 2"
    assert len(data2["list"]) == 5, "第2页应有 5 个视频"

    # 测试第3页（最后一页）
    url3 = f"{BASE_URL}/api.php?ac=detail&t=1&pg=3"
    resp3 = requests.get(url3)
    data3 = resp3.json()
    assert data3["page"] == 3, "当前页应为 3"
    assert len(data3["list"]) == 5, "第3页应有 5 个视频"

    # 测试电视剧分类
    url_tv = f"{BASE_URL}/api.php?ac=detail&t=2&pg=1"
    resp_tv = requests.get(url_tv)
    data_tv = resp_tv.json()
    assert data_tv["total"] == 15, "电视剧分类应有 15 个视频"
    print(f"\n电视剧分类总数: {data_tv['total']}")

    # 测试综艺分类
    url_variety = f"{BASE_URL}/api.php?ac=detail&t=3&pg=1"
    resp_variety = requests.get(url_variety)
    data_variety = resp_variety.json()
    assert data_variety["total"] == 15, "综艺分类应有 15 个视频"
    print(f"综艺分类总数: {data_variety['total']}")

    # 测试动漫分类
    url_anime = f"{BASE_URL}/api.php?ac=detail&t=4&pg=1"
    resp_anime = requests.get(url_anime)
    data_anime = resp_anime.json()
    assert data_anime["total"] == 15, "动漫分类应有 15 个视频"
    print(f"动漫分类总数: {data_anime['total']}")

    print("✅ 分类列表接口测试通过")


def test_detail():
    """
    测试详情接口: GET /api.php?ac=detail&ids={vod_id}
    """
    print("\n" + "=" * 60)
    print("测试 3: 详情接口")
    print("=" * 60)

    # 测试单个视频详情
    url = f"{BASE_URL}/api.php?ac=detail&ids=1"
    resp = requests.get(url)

    print(f"请求 URL: {url}")
    print(f"状态码: {resp.status_code}")

    assert resp.status_code == 200, "状态码应为 200"

    data = resp.json()
    assert "list" in data, "应包含 list 字段"
    assert len(data["list"]) == 1, "应返回 1 个视频"

    vod = data["list"][0]
    print(f"\n视频详情字段: {list(vod.keys())}")

    # 验证所有必填字段
    required_fields = [
        "vod_id", "vod_name", "vod_pic", "vod_content",
        "vod_director", "vod_actor", "vod_year", "vod_area",
        "vod_remarks", "vod_play_from", "vod_play_url"
    ]

    for field in required_fields:
        assert field in vod, f"视频详情应包含 {field}"
        print(f"  {field}: {str(vod[field])[:50]}...")

    # 验证播放线路
    play_from = vod["vod_play_from"]
    play_url = vod["vod_play_url"]
    print(f"\n  vod_play_from: {play_from}")

    sources = play_from.split("$")
    url_groups = play_url.split("$")
    assert len(sources) == 2, "应有 2 条播放线路"
    assert len(url_groups) == 2, "应有 2 组播放地址"
    assert sources[0] == "无尽", "第一条线路应为 无尽"
    assert sources[1] == "闪电", "第二条线路应为 闪电"
    print(f"  线路数量: {len(sources)}")
    print(f"  线路1: {sources[0]}")
    print(f"  线路2: {sources[1]}")

    # 电影应该只有1集
    episodes = url_groups[0].split("#")
    print(f"  电影集数: {len(episodes)}")
    assert len(episodes) == 1, "电影应有 1 集"
    assert ".m3u8" in episodes[0], "播放地址应为 m3u8 格式"

    # 测试多个视频详情
    url_multi = f"{BASE_URL}/api.php?ac=detail&ids=1,2,3"
    resp_multi = requests.get(url_multi)
    data_multi = resp_multi.json()
    assert len(data_multi["list"]) == 3, "应返回 3 个视频"
    print(f"\n批量查询 (ids=1,2,3) 返回: {len(data_multi['list'])} 个视频")

    # 测试电视剧详情（验证集数）
    url_tv = f"{BASE_URL}/api.php?ac=detail&ids=16"
    resp_tv = requests.get(url_tv)
    data_tv = resp_tv.json()
    vod_tv = data_tv["list"][0]
    tv_episodes = vod_tv["vod_play_url"].split("$")[0].split("#")
    print(f"\n电视剧集数 (id=16): {len(tv_episodes)} 集")
    assert 20 <= len(tv_episodes) <= 40, "电视剧集数应在 20-40 之间"

    print("✅ 详情接口测试通过")


def test_search():
    """
    测试搜索接口: GET /api.php?ac=detail&wd={keyword}
    """
    print("\n" + "=" * 60)
    print("测试 4: 搜索接口")
    print("=" * 60)

    # 搜索"流浪"
    keyword = "流浪"
    url = f"{BASE_URL}/api.php?ac=detail&wd={keyword}"
    resp = requests.get(url)

    print(f"请求 URL: {url}")
    print(f"状态码: {resp.status_code}")

    assert resp.status_code == 200, "状态码应为 200"

    data = resp.json()
    print(f"\n搜索关键词: {keyword}")
    print(f"搜索结果数: {data['total']}")
    print(f"返回数量: {len(data['list'])}")

    # 验证搜索结果
    for vod in data["list"]:
        assert keyword in vod["vod_name"], f"搜索结果应包含关键词: {vod['vod_name']}"
        print(f"  - {vod['vod_name']} (id={vod['vod_id']})")

    # 搜索"地球"（应该找到流浪地球）
    keyword2 = "地球"
    url2 = f"{BASE_URL}/api.php?ac=detail&wd={keyword2}"
    resp2 = requests.get(url2)
    data2 = resp2.json()
    print(f"\n搜索关键词: {keyword2}")
    print(f"搜索结果数: {data2['total']}")
    assert data2["total"] >= 1, "至少应找到 1 个结果"

    # 搜索不存在的关键词
    keyword3 = "不存在的视频12345"
    url3 = f"{BASE_URL}/api.php?ac=detail&wd={keyword3}"
    resp3 = requests.get(url3)
    data3 = resp3.json()
    print(f"\n搜索关键词: {keyword3}")
    print(f"搜索结果数: {data3['total']}")
    assert data3["total"] == 0, "不应找到结果"

    print("✅ 搜索接口测试通过")


def test_invalid_requests():
    """
    测试无效请求
    """
    print("\n" + "=" * 60)
    print("测试 5: 无效请求处理")
    print("=" * 60)

    # 无效路径
    url = f"{BASE_URL}/invalid_path"
    resp = requests.get(url)
    print(f"无效路径状态码: {resp.status_code}")
    assert resp.status_code == 404, "无效路径应返回 404"

    # 缺少 ac 参数
    url2 = f"{BASE_URL}/api.php"
    resp2 = requests.get(url2)
    print(f"缺少 ac 参数状态码: {resp2.status_code}")
    assert resp2.status_code == 400, "缺少参数应返回 400"

    # 无效分类
    url3 = f"{BASE_URL}/api.php?ac=detail&t=999&pg=1"
    resp3 = requests.get(url3)
    print(f"无效分类状态码: {resp3.status_code}")
    assert resp3.status_code == 400, "无效分类应返回 400"

    print("✅ 无效请求处理测试通过")


def main():
    """
    主测试函数
    """
    print("=" * 60)
    print("  模拟 API 服务器测试")
    print("=" * 60)

    # 启动服务器
    print("\n正在启动服务器...")
    success = start_server()
    if not success:
        print("❌ 服务器启动失败")
        return

    # 等待服务器启动
    time.sleep(1)

    try:
        # 运行所有测试
        test_home_page()
        test_category_list()
        test_detail()
        test_search()
        test_invalid_requests()

        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 停止服务器
        print("\n正在停止服务器...")
        stop_server()


if __name__ == "__main__":
    main()
