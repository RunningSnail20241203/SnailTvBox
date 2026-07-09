# -*- coding: utf-8 -*-
"""
Spider 基类模块
定义 TvBox 爬虫源的标准接口规范
所有自定义爬虫源都需要继承 BaseSpider 并实现相应方法
"""


class BaseSpider:
    """
    TvBox 爬虫源基类

    定义了爬虫源需要实现的标准接口方法，所有方法都有默认空实现。
    子类可以根据需要重写相应的方法来提供具体功能。

    返回值格式遵循 TvBox 的 JSON 数据格式规范，
    详细格式说明见各方法文档注释。
    """

    def __init__(self):
        """初始化基类，预留扩展空间"""
        pass

    def init(self, context, extend=""):
        """
        初始化爬虫

        在爬虫首次使用前调用，用于进行初始化操作。

        参数:
            context: 上下文对象，TvBox 传入的上下文环境
            extend (str): 扩展参数，对应视频源配置中的 ext 字段

        返回:
            None
        """
        pass

    def home_content(self, filter=False):
        """
        获取首页内容

        返回首页的分类列表和推荐视频列表。

        参数:
            filter (bool): 是否启用筛选功能，默认 False

        返回:
            dict: 首页内容数据，格式如下：
                {
                    "class": [          # 分类列表
                        {
                            "type_id": "1",      # 分类ID
                            "type_name": "电影"   # 分类名称
                        },
                        ...
                    ],
                    "list": [           # 首页推荐视频列表
                        {
                            "vod_id": "movie_1",    # 视频ID
                            "vod_name": "视频名称",  # 视频名称
                            "vod_pic": "https://...",  # 封面图
                            "vod_remarks": "HD"      # 备注/更新状态
                        },
                        ...
                    ]
                }
        """
        return {
            "class": [],
            "list": []
        }

    def home_video_content(self):
        """
        获取首页推荐视频列表（可选实现）

        部分场景下只需要获取首页推荐视频，不需要分类信息时使用。

        参数:
            无

        返回:
            list: 首页推荐视频列表，每个元素是视频信息字典
                [
                    {
                        "vod_id": "movie_1",
                        "vod_name": "视频名称",
                        "vod_pic": "https://...",
                        "vod_remarks": "HD"
                    },
                    ...
                ]
        """
        return []

    def category_content(self, tid, pg, filter=False, extend=None):
        """
        获取分类视频列表

        根据分类ID获取该分类下的视频列表，支持分页。

        参数:
            tid (str): 分类ID，对应 type_id
            pg (str): 页码，从1开始
            filter (bool): 是否启用筛选，默认 False
            extend (dict): 扩展筛选参数，默认为 None

        返回:
            dict: 分类视频列表数据，格式如下：
                {
                    "page": 1,              # 当前页码
                    "pagecount": 10,        # 总页数
                    "limit": 20,            # 每页数量
                    "total": 200,           # 总条数
                    "list": [               # 视频列表
                        {
                            "vod_id": "movie_1",
                            "vod_name": "视频名称",
                            "vod_pic": "https://...",
                            "vod_remarks": "HD"
                        },
                        ...
                    ]
                }
        """
        return {
            "page": int(pg) if pg else 1,
            "pagecount": 0,
            "limit": 20,
            "total": 0,
            "list": []
        }

    def detail_content(self, ids):
        """
        获取视频详情

        根据视频ID列表获取视频的详细信息，包括简介、演员、播放线路等。

        参数:
            ids (list): 视频ID列表，例如 ["movie_1", "movie_2"]

        返回:
            dict: 视频详情数据，格式如下：
                {
                    "list": [
                        {
                            "vod_id": "movie_1",              # 视频ID
                            "vod_name": "视频名称",            # 视频名称
                            "vod_pic": "https://...",         # 封面图
                            "vod_content": "视频简介...",     # 视频简介
                            "vod_director": "导演1,导演2",     # 导演
                            "vod_actor": "演员1,演员2",       # 演员
                            "vod_year": "2024",               # 年份
                            "vod_area": "大陆",               # 地区
                            "vod_remarks": "HD",              # 备注/状态
                            "vod_play_from": "无尽$闪电",     # 播放线路名称，用$分隔
                            "vod_play_url": "第1集@https://...#第2集@https://...$第1集@https://..."
                                                              # 播放地址，线路间用$分隔，剧集间用#分隔
                                                              # 单集格式: 集名@URL
                        },
                        ...
                    ]
                }
        """
        return {
            "list": []
        }

    def search_content(self, key, quick=False, pg="1"):
        """
        搜索视频

        根据关键词搜索视频，支持分页。

        参数:
            key (str): 搜索关键词
            quick (bool): 是否快速搜索，默认 False
            pg (str): 页码，默认 "1"

        返回:
            dict: 搜索结果数据，格式如下：
                {
                    "page": 1,              # 当前页码
                    "pagecount": 10,        # 总页数
                    "limit": 20,            # 每页数量
                    "total": 200,           # 总条数
                    "list": [               # 视频列表
                        {
                            "vod_id": "movie_1",
                            "vod_name": "视频名称",
                            "vod_pic": "https://...",
                            "vod_remarks": "HD"
                        },
                        ...
                    ]
                }
        """
        return {
            "page": int(pg) if pg else 1,
            "pagecount": 0,
            "limit": 20,
            "total": 0,
            "list": []
        }

    def player_content(self, flag, id, vip_flags=None):
        """
        获取播放地址

        根据播放线路和视频ID获取实际的播放地址。

        参数:
            flag (str): 播放线路标识，对应 vod_play_from 中的线路名称
            id (str): 视频ID
            vip_flags (list): VIP 线路标识列表，默认为 None

        返回:
            dict: 播放地址数据，格式如下：
                {
                    "url": "https://.../index.m3u8",   # 实际播放地址
                    "parse": 0,                         # 是否需要解析 0=不需要 1=需要
                    "jx": 0                             # 是否需要解析 0=不需要 1=需要
                }
        """
        return {
            "url": "",
            "parse": 0,
            "jx": 0
        }
