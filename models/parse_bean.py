# -*- coding: utf-8 -*-
"""
ParseBean 数据模型

对应 TvBox 配置文件中的 parses 数组元素。
parses 定义了多个解析源，用于将不能直接播放的地址解析成真实视频地址。

参考 TvBox 配置格式：
{
    "parses": [
        {
            "name": "解析源名称",
            "type": 0,           // 0=Web嗅探, 1=JSON接口, 3=Spider解析
            "url": "解析接口地址",
            "ext": { ... },      // 扩展参数
            "flag": ["qq", "腾讯"]  // 适用平台标识
        }
    ]
}
"""


class ParseBean:
    """解析源数据模型

    对应 TvBox 配置中 parses 数组的单个元素。
    每个 ParseBean 代表一个解析源，用于将视频地址解析成可播放的真实地址。
    """

    def __init__(self):
        """初始化 ParseBean"""
        self.name = ""           # 解析源名称
        self.type = 0            # 解析类型: 0=Web嗅探, 1=JSON接口, 2=JSON扩展, 3=Spider, 4=混合
        self.url = ""            # 解析接口地址（type=0/1/2时使用）
        self.ext = {}            # 扩展参数（如header、flag等）
        self.flag = []           # 适用平台标识列表（如 ["qq", "腾讯", "iqiyi"]）

    def __repr__(self):
        return f"<ParseBean(name='{self.name}', type={self.type}, flag={self.flag})>"

    def get_type_name(self):
        """获取解析类型的名称"""
        type_names = {
            0: "Web嗅探",
            1: "JSON接口",
            2: "JSON扩展",
            3: "Spider解析",
            4: "混合解析",
        }
        return type_names.get(self.type, f"未知类型({self.type})")

    def has_flag(self, flag):
        """判断是否包含指定平台标识

        参数:
            flag: 平台标识字符串（如 "qq"）

        返回:
            bool: 是否包含
        """
        return flag.lower() in [f.lower() for f in self.flag]

    def match_url(self, url):
        """判断该解析源是否适用于给定的 URL

        判断逻辑：
        1. 如果有 flag，检查 URL 中是否包含 flag 对应的关键词
        2. 如果没有 flag，表示万能解析，适用所有 URL

        参数:
            url: 待解析的视频地址

        返回:
            bool: 是否适用
        """
        if not self.flag:
            return True  # 没有 flag 限制，万能解析

        url_lower = url.lower()
        for f in self.flag:
            if f.lower() in url_lower:
                return True
        return False