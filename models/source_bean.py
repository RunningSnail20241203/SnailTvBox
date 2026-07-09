# -*- coding: utf-8 -*-
"""
数据模型模块 - 视频源信息
SourceBean 对应 TvBox 的视频源配置
"""


class SourceBean:
    """
    视频源数据模型
    对应 TvBox 配置中的 sites 数组元素

    type 类型说明:
        0 = xml 格式源
        1 = json 格式源
        3 = spider 爬虫源
    """

    def __init__(self):
        """初始化视频源对象，所有字段设置默认值"""
        self._key = ""
        self._name = ""
        self._api = ""
        self._type = 0
        self._searchable = 0
        self._quick_search = 0
        self._filterable = 0
        self._player_url = ""
        self._ext = ""
        self._jar = ""
        self._player_type = 0
        self._timeout = 0
        self._style = ""

    # key 属性
    @property
    def key(self):
        """视频源唯一标识"""
        return self._key

    @key.setter
    def key(self, value):
        self._key = str(value) if value is not None else ""

    # name 属性
    @property
    def name(self):
        """视频源名称"""
        return self._name

    @name.setter
    def name(self, value):
        self._name = str(value) if value is not None else ""

    # api 属性
    @property
    def api(self):
        """视频源 API 地址"""
        return self._api

    @api.setter
    def api(self, value):
        self._api = str(value) if value is not None else ""

    # type 属性
    @property
    def type(self):
        """
        视频源类型
        0=xml, 1=json, 3=spider
        """
        return self._type

    @type.setter
    def type(self, value):
        try:
            self._type = int(value)
        except (ValueError, TypeError):
            self._type = 0

    # searchable 属性
    @property
    def searchable(self):
        """是否支持搜索 0=不支持 1=支持"""
        return self._searchable

    @searchable.setter
    def searchable(self, value):
        try:
            self._searchable = int(value)
        except (ValueError, TypeError):
            self._searchable = 0

    # quickSearch 属性
    @property
    def quickSearch(self):
        """是否支持快速搜索 0=不支持 1=支持"""
        return self._quick_search

    @quickSearch.setter
    def quickSearch(self, value):
        try:
            self._quick_search = int(value)
        except (ValueError, TypeError):
            self._quick_search = 0

    # filterable 属性
    @property
    def filterable(self):
        """是否支持筛选 0=不支持 1=支持"""
        return self._filterable

    @filterable.setter
    def filterable(self, value):
        try:
            self._filterable = int(value)
        except (ValueError, TypeError):
            self._filterable = 0

    # playerUrl 属性
    @property
    def playerUrl(self):
        """播放器 URL"""
        return self._player_url

    @playerUrl.setter
    def playerUrl(self, value):
        self._player_url = str(value) if value is not None else ""

    # ext 属性
    @property
    def ext(self):
        """扩展配置"""
        return self._ext

    @ext.setter
    def ext(self, value):
        if isinstance(value, dict):
            import json
            self._ext = json.dumps(value, ensure_ascii=False)
        else:
            self._ext = str(value) if value is not None else ""

    # jar 属性
    @property
    def jar(self):
        """jar 包路径"""
        return self._jar

    @jar.setter
    def jar(self, value):
        self._jar = str(value) if value is not None else ""

    # playerType 属性
    @property
    def playerType(self):
        """播放器类型"""
        return self._player_type

    @playerType.setter
    def playerType(self, value):
        try:
            self._player_type = int(value)
        except (ValueError, TypeError):
            self._player_type = 0

    # timeout 属性
    @property
    def timeout(self):
        """超时时间（秒）"""
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        try:
            self._timeout = int(value)
        except (ValueError, TypeError):
            self._timeout = 0

    # style 属性
    @property
    def style(self):
        """样式配置"""
        return self._style

    @style.setter
    def style(self, value):
        if isinstance(value, dict):
            import json
            self._style = json.dumps(value, ensure_ascii=False)
        else:
            self._style = str(value) if value is not None else ""

    def get_type_name(self):
        """获取类型名称"""
        type_map = {
            0: "xml",
            1: "json",
            3: "spider"
        }
        return type_map.get(self._type, f"unknown({self._type})")

    def __str__(self):
        """字符串表示"""
        return f"SourceBean(key={self._key}, name={self._name}, type={self.get_type_name()})"

    def __repr__(self):
        """调试用表示"""
        return self.__str__()
