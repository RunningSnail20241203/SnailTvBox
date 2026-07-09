# -*- coding: utf-8 -*-
"""
MockSpider 模拟数据源模块
提供模拟的视频数据，用于测试和开发
"""

import random
from .base_spider import BaseSpider


class MockSpider(BaseSpider):
    """
    模拟数据源爬虫

    生成模拟的视频数据，用于测试 TvBox 爬虫接口的各个功能。
    包含完整的分类、视频列表、详情、搜索、播放地址等模拟数据。

    数据规模:
        - 5个分类（电影、电视剧、综艺、动漫、纪录片）
        - 每个分类12个视频
        - 每页6个视频，共2页
        - 每个视频2-3条播放线路
    """

    def __init__(self):
        """初始化 MockSpider，生成模拟数据"""
        super().__init__()

        self._categories = [
            {"type_id": "1", "type_name": "电影"},
            {"type_id": "2", "type_name": "电视剧"},
            {"type_id": "3", "type_name": "综艺"},
            {"type_id": "4", "type_name": "动漫"},
            {"type_id": "5", "type_name": "纪录片"},
        ]

        self._play_lines = ["无尽", "闪电", "量子", "极速", "卧龙"]

        self._movie_names = [
            "流浪地球3", "满江红", "孤注一掷", "消失的她", "封神第一部",
            "八角笼中", "长安三万里", "热烈", "巨齿鲨2", "奥本海默",
            "碟中谍7", "速度与激情10"
        ]

        self._tv_names = [
            "狂飙", "三体", "去有风的地方", "漫长的季节", "繁花",
            "我的人间烟火", "长相思", "莲花楼", "一念关山", "问心",
            "以法之名", "小日子"
        ]

        self._variety_names = [
            "奔跑吧第12季", "极限挑战第10季", "向往的生活第7季", "王牌对王牌第8季",
            "歌手2024", "中国好声音第12季", "乘风破浪的姐姐第4季", "披荆斩棘的哥哥第3季",
            "脱口秀大会第6季", "奇葩说第8季", "最强大脑第11季", "声生不息第3季"
        ]

        self._anime_names = [
            "斗罗大陆", "斗破苍穹", "完美世界", "凡人修仙传", "吞噬星空",
            "画江湖之不良人", "天行九歌", "武庚纪", "狐妖小红娘", "一人之下",
            "刺客伍六七", "灵笼"
        ]

        self._doc_names = [
            "地球脉动第三季", "蓝色星球第二季", "王朝", "我们的星球", "七个世界一个星球",
            "河西走廊", "舌尖上的中国第三季", "我在故宫修文物", "航拍中国第四季", "大国崛起",
            "辉煌中国", "创新中国"
        ]

        self._directors = [
            "张艺谋", "陈凯歌", "冯小刚", "吴京", "陈思诚",
            "郭帆", "宁浩", "贾玲", "邓超", "韩寒"
        ]

        self._actors = [
            "吴京", "刘德华", "沈腾", "马丽", "易烊千玺",
            "张译", "雷佳音", "于和伟", "黄渤", "徐峥",
            "杨幂", "赵丽颖", "刘亦菲", "迪丽热巴", "杨紫"
        ]

        self._areas = ["大陆", "香港", "台湾", "美国", "韩国", "日本", "英国"]
        self._years = ["2021", "2022", "2023", "2024"]

        self._all_videos = {}
        self._video_dict = {}

        self._generate_all_videos()

    def _generate_all_videos(self):
        """生成所有分类的视频数据"""
        name_lists = {
            "1": self._movie_names,
            "2": self._tv_names,
            "3": self._variety_names,
            "4": self._anime_names,
            "5": self._doc_names,
        }

        for tid, names in name_lists.items():
            videos = []
            for i, name in enumerate(names):
                video = self._generate_video_detail(tid, i + 1, name)
                videos.append(video)
                self._video_dict[video["vod_id"]] = video
            self._all_videos[tid] = videos

    def _generate_video_detail(self, tid, index, name):
        """
        生成单个视频的详细信息

        参数:
            tid (str): 分类ID
            index (int): 视频序号
            name (str): 视频名称

        返回:
            dict: 视频详情字典
        """
        vod_id = f"vod_{tid}_{index}"

        pic_url = f"https://picsum.photos/seed/{vod_id}/300/420.jpg"

        random.seed(hash(vod_id))

        director = random.choice(self._directors)
        actor_count = random.randint(3, 6)
        actors = random.sample(self._actors, min(actor_count, len(self._actors)))
        actor_str = ",".join(actors)

        year = random.choice(self._years)
        area = random.choice(self._areas)

        content_templates = [
            f"《{name}》是一部由{director}执导，{actor_str}等主演的影视作品。",
            f"该片讲述了一个关于成长与奋斗的故事，{name}以其独特的叙事方式和精彩的表演赢得了观众的广泛好评。",
            f"故事发生在{year}年，主人公在{area}经历了一系列的挑战与机遇，最终实现了自我价值。"
        ]
        content = "".join(content_templates)

        line_count = random.randint(2, 3)
        play_from_list = random.sample(self._play_lines, line_count)

        if tid == "1":
            episode_count = 1
            remarks = "HD"
        elif tid == "2":
            episode_count = random.randint(20, 40)
            remarks = f"更新至{episode_count}集"
        elif tid == "3":
            episode_count = random.randint(10, 20)
            remarks = f"第{episode_count}期"
        elif tid == "4":
            episode_count = random.randint(30, 100)
            remarks = f"第{episode_count}集"
        else:
            episode_count = random.randint(5, 15)
            remarks = f"全{episode_count}集"

        play_url_list = []
        play_lines_struct = []
        for line_idx, line_name in enumerate(play_from_list):
            episodes = []
            ep_list = []
            for ep in range(1, episode_count + 1):
                if tid == "1":
                    ep_name = "正片"
                elif tid == "3":
                    ep_name = f"第{ep}期"
                else:
                    ep_name = f"第{ep}集"
                ep_url = f"https://mock.example.com/{vod_id}/{line_idx}/{ep}.m3u8"
                episodes.append(f"{ep_name}@{ep_url}")
                ep_list.append({"name": ep_name, "url": ep_url})
            play_url_list.append("#".join(episodes))
            play_lines_struct.append({"from": line_name, "episodes": ep_list})

        return {
            "vod_id": vod_id,
            "vod_name": name,
            "vod_pic": pic_url,
            "vod_content": content,
            "vod_director": director,
            "vod_actor": actor_str,
            "vod_year": year,
            "vod_area": area,
            "vod_remarks": remarks,
            "vod_play_from": "$".join(play_from_list),
            "vod_play_url": "$".join(play_url_list),
            "_play_lines": play_lines_struct,
        }

    def _get_video_brief(self, video):
        """
        从完整视频信息中提取简要信息（用于列表展示）

        参数:
            video (dict): 完整视频详情

        返回:
            dict: 视频简要信息
        """
        return {
            "vod_id": video["vod_id"],
            "vod_name": video["vod_name"],
            "vod_pic": video["vod_pic"],
            "vod_remarks": video["vod_remarks"],
        }

    def init(self, context, extend=""):
        """
        初始化 MockSpider

        参数:
            context: 上下文对象
            extend (str): 扩展参数
        """
        pass

    def home_content(self, filter=False):
        """
        获取首页内容

        返回分类列表和首页推荐视频（6个，从各分类中随机选取）

        参数:
            filter (bool): 是否启用筛选

        返回:
            dict: 首页内容数据
        """
        recommend_videos = []
        for tid in ["1", "2", "3", "4", "5"]:
            if self._all_videos.get(tid):
                recommend_videos.append(self._get_video_brief(self._all_videos[tid][0]))

        if len(recommend_videos) < 6 and self._all_videos.get("1"):
            recommend_videos.append(self._get_video_brief(self._all_videos["1"][1]))

        return {
            "class": self._categories,
            "list": recommend_videos[:6]
        }

    def home_video_content(self):
        """
        获取首页推荐视频列表

        返回:
            list: 首页推荐视频列表
        """
        home_data = self.home_content()
        return home_data.get("list", [])

    def category_content(self, tid, pg, filter=False, extend=None):
        """
        获取分类视频列表

        参数:
            tid (str): 分类ID
            pg (str): 页码
            filter (bool): 是否启用筛选
            extend (dict): 扩展参数

        返回:
            dict: 分类视频列表数据
        """
        page = int(pg) if pg else 1
        page_size = 6

        videos = self._all_videos.get(tid, [])
        total = len(videos)
        pagecount = (total + page_size - 1) // page_size if total > 0 else 0

        start = (page - 1) * page_size
        end = start + page_size
        page_videos = videos[start:end]

        brief_list = [self._get_video_brief(v) for v in page_videos]

        return {
            "page": page,
            "pagecount": pagecount,
            "limit": page_size,
            "total": total,
            "list": brief_list
        }

    def detail_content(self, ids):
        """
        获取视频详情

        参数:
            ids (list): 视频ID列表

        返回:
            dict: 视频详情数据
        """
        result_list = []

        for vid in ids:
            found = False
            for tid, videos in self._all_videos.items():
                for video in videos:
                    if video["vod_id"] == vid:
                        result_list.append(video)
                        found = True
                        break
                if found:
                    break

        return {
            "list": result_list
        }

    def search_content(self, key, quick=False, pg="1"):
        """
        搜索视频

        匹配视频名称中包含关键词的视频。

        参数:
            key (str): 搜索关键词
            quick (bool): 是否快速搜索
            pg (str): 页码

        返回:
            dict: 搜索结果数据
        """
        page = int(pg) if pg else 1
        page_size = 6

        all_results = []
        for tid, videos in self._all_videos.items():
            for video in videos:
                if key.lower() in video["vod_name"].lower():
                    all_results.append(video)

        total = len(all_results)
        pagecount = (total + page_size - 1) // page_size if total > 0 else 0

        start = (page - 1) * page_size
        end = start + page_size
        page_videos = all_results[start:end]

        brief_list = [self._get_video_brief(v) for v in page_videos]

        return {
            "page": page,
            "pagecount": pagecount,
            "limit": page_size,
            "total": total,
            "list": brief_list
        }

    def player_content(self, flag, id, vip_flags=None):
        """
        获取播放地址

        根据线路名称和视频ID返回模拟的播放地址。

        参数:
            flag (str): 播放线路名称
            id (str): 视频ID
            vip_flags (list): VIP 线路列表

        返回:
            dict: 播放地址数据
        """
        video = self._video_dict.get(id)
        if not video:
            return {"url": "", "parse": 0, "jx": 0}

        play_lines = video.get("_play_lines", [])
        for line in play_lines:
            if line["from"] == flag:
                if line["episodes"]:
                    return {
                        "url": line["episodes"][0]["url"],
                        "parse": 0,
                        "jx": 0
                    }

        return {"url": "", "parse": 0, "jx": 0}
