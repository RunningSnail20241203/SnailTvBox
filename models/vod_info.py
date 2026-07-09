# -*- coding: utf-8 -*-
"""
数据模型模块 - 视频信息
VodInfo 对应视频详情数据
"""

import logging

logger = logging.getLogger(__name__)


class VodInfo:
    """
    视频信息数据模型
    存储视频的基本信息和播放线路数据
    """

    def __init__(self):
        """初始化视频信息对象，所有字段设置默认值"""
        self._vod_id = ""
        self._vod_name = ""
        self._vod_pic = ""
        self._vod_remarks = ""
        self._vod_year = ""
        self._vod_area = ""
        self._vod_director = ""
        self._vod_actor = ""
        self._vod_content = ""
        self._vod_play_from = ""
        self._vod_play_url = ""

    # vod_id 属性
    @property
    def vod_id(self):
        """视频ID"""
        return self._vod_id

    @vod_id.setter
    def vod_id(self, value):
        self._vod_id = str(value) if value is not None else ""

    # vod_name 属性
    @property
    def vod_name(self):
        """视频名称"""
        return self._vod_name

    @vod_name.setter
    def vod_name(self, value):
        self._vod_name = str(value) if value is not None else ""

    # vod_pic 属性
    @property
    def vod_pic(self):
        """视频封面图"""
        return self._vod_pic

    @vod_pic.setter
    def vod_pic(self, value):
        self._vod_pic = str(value) if value is not None else ""

    # vod_remarks 属性
    @property
    def vod_remarks(self):
        """视频备注（更新状态等）"""
        return self._vod_remarks

    @vod_remarks.setter
    def vod_remarks(self, value):
        self._vod_remarks = str(value) if value is not None else ""

    # vod_year 属性
    @property
    def vod_year(self):
        """年份"""
        return self._vod_year

    @vod_year.setter
    def vod_year(self, value):
        self._vod_year = str(value) if value is not None else ""

    # vod_area 属性
    @property
    def vod_area(self):
        """地区"""
        return self._vod_area

    @vod_area.setter
    def vod_area(self, value):
        self._vod_area = str(value) if value is not None else ""

    # vod_director 属性
    @property
    def vod_director(self):
        """导演"""
        return self._vod_director

    @vod_director.setter
    def vod_director(self, value):
        self._vod_director = str(value) if value is not None else ""

    # vod_actor 属性
    @property
    def vod_actor(self):
        """演员"""
        return self._vod_actor

    @vod_actor.setter
    def vod_actor(self, value):
        self._vod_actor = str(value) if value is not None else ""

    # vod_content 属性
    @property
    def vod_content(self):
        """视频简介"""
        return self._vod_content

    @vod_content.setter
    def vod_content(self, value):
        self._vod_content = str(value) if value is not None else ""

    # vod_play_from 属性
    @property
    def vod_play_from(self):
        """
        播放线路名称，多个线路用 $ 分隔
        例如: "线路1$线路2$线路3"
        """
        return self._vod_play_from

    @vod_play_from.setter
    def vod_play_from(self, value):
        self._vod_play_from = str(value) if value is not None else ""

    # vod_play_url 属性
    @property
    def vod_play_url(self):
        """
        播放地址列表，多个线路用 $ 分隔
        每个线路内部的剧集用 # 分隔
        单集格式: 名称@URL
        例如: "第1集@url1#第2集@url2$第1集@url3"
        """
        return self._vod_play_url

    @vod_play_url.setter
    def vod_play_url(self, value):
        self._vod_play_url = str(value) if value is not None else ""

    def parse_play_list(self):
        """
        解析播放线路数据

        数据格式说明:
            vod_play_from: 线路名称用 $ 分隔，例如 "无尽$闪电$量子"
            vod_play_url:  线路间用 $ 分隔，剧集间用 # 分隔，单集格式为 名称@URL
                          例如: "第1集@url1#第2集@url2$第1集@url3#第2集@url4$..."

        返回:
            list: 播放线路列表，每个元素是字典
                {
                    "from": "线路名称",
                    "episodes": [
                        {"name": "第1集", "url": "播放地址"},
                        ...
                    ]
                }
        """
        play_list = []

        if not self._vod_play_from or not self._vod_play_url:
            logger.debug("parse_play_list: vod_play_from 或 vod_play_url 为空, from=%r, url=%r",
                         self._vod_play_from[:50], self._vod_play_url[:100])
            return play_list

        logger.debug("parse_play_list: 开始解析, vod_play_url=%s", self._vod_play_url[:100])

        from_list = self._vod_play_from.split("$")
        url_list = self._vod_play_url.split("$")

        min_len = min(len(from_list), len(url_list))

        for i in range(min_len):
            line_name = from_list[i].strip()
            line_urls = url_list[i].strip()

            if not line_name or not line_urls:
                continue

            episodes = []
            episode_list = line_urls.split("#")

            for episode_str in episode_list:
                episode_str = episode_str.strip()
                if not episode_str:
                    continue

                if "@" in episode_str:
                    parts = episode_str.split("@", 1)
                    ep_name = parts[0].strip()
                    ep_url = parts[1].strip()
                else:
                    ep_name = episode_str
                    ep_url = ""
                    logger.warning("剧集 URL 为空: name=%r, 原始字符串=%r", ep_name, episode_str)

                episodes.append({
                    "name": ep_name,
                    "url": ep_url
                })

            if episodes:
                play_list.append({
                    "from": line_name,
                    "episodes": episodes
                })
                logger.debug("解析线路: from=%s, 剧集数=%d", line_name, len(episodes))

        return play_list

    def get_line_count(self):
        """
        获取播放线路数量

        返回:
            int: 线路数量
        """
        if not self._vod_play_from:
            return 0
        return len([x for x in self._vod_play_from.split("$") if x.strip()])

    def __str__(self):
        """字符串表示"""
        return f"VodInfo(id={self._vod_id}, name={self._vod_name}, lines={self.get_line_count()})"

    def __repr__(self):
        """调试用表示"""
        return self.__str__()
