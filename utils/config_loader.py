# -*- coding: utf-8 -*-
"""
工具类模块 - 配置加载器
ConfigLoader 负责从本地文件或 URL 加载 TvBox 配置
"""

import json
import os
import sys

from models.source_bean import SourceBean
from models.parse_bean import ParseBean


class ConfigLoader:
    """
    TvBox 配置加载器
    支持从本地文件和 URL 加载配置，解析视频源、直播源等信息
    """

    def __init__(self):
        """初始化配置加载器"""
        self._config_data = {}
        self._sites = []
        self._lives = []
        self._parses = []
        self._spider = ""
        self._wallpaper = ""

    @property
    def sites(self):
        """视频源列表"""
        return self._sites

    @property
    def lives(self):
        """直播源列表"""
        return self._lives

    @property
    def parses(self):
        """解析源列表"""
        return self._parses

    @property
    def spider(self):
        """爬虫配置"""
        return self._spider

    @property
    def wallpaper(self):
        """壁纸地址"""
        return self._wallpaper

    @property
    def config_data(self):
        """原始配置数据"""
        return self._config_data

    def load_from_file(self, file_path):
        """
        从本地文件加载 JSON 配置

        参数:
            file_path: 配置文件路径

        返回:
            bool: 是否加载成功
        """
        if not os.path.exists(file_path):
            print(f"[错误] 文件不存在: {file_path}")
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self._config_data = json.load(f)
            return self._parse_config()
        except json.JSONDecodeError as e:
            print(f"[错误] JSON 格式错误: {e}")
            return False
        except Exception as e:
            print(f"[错误] 读取文件失败: {e}")
            return False

    def load_from_url(self, url, timeout=10):
        """
        从 URL 下载并加载 JSON 配置

        参数:
            url: 配置文件 URL
            timeout: 超时时间（秒）

        返回:
            bool: 是否加载成功
        """
        try:
            import requests
        except ImportError:
            print("[错误] 缺少 requests 库，请先安装: pip install requests")
            return False

        try:
            print(f"[信息] 正在下载配置: {url}")
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            response.encoding = "utf-8"
            self._config_data = response.json()
            return self._parse_config()
        except requests.exceptions.ConnectionError:
            print(f"[错误] 网络连接失败，请检查网络: {url}")
            return False
        except requests.exceptions.Timeout:
            print(f"[错误] 请求超时: {url}")
            return False
        except requests.exceptions.HTTPError as e:
            print(f"[错误] HTTP 请求失败: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"[错误] JSON 格式错误: {e}")
            return False
        except Exception as e:
            print(f"[错误] 下载配置失败: {e}")
            return False

    def _parse_config(self):
        """
        解析配置数据

        返回:
            bool: 是否解析成功
        """
        if not isinstance(self._config_data, dict):
            print("[错误] 配置数据格式错误，应为字典类型")
            return False

        self._sites = []
        self._lives = []
        self._parses = []
        self._spider = ""
        self._wallpaper = ""

        try:
            self._parse_sites()
            self._parse_lives()
            self._parse_parses()
            self._parse_other_fields()
            return True
        except Exception as e:
            print(f"[错误] 解析配置失败: {e}")
            return False

    def _parse_sites(self):
        """解析视频源列表"""
        sites_data = self._config_data.get("sites", [])
        if not isinstance(sites_data, list):
            print("[警告] sites 字段格式错误，应为数组")
            return

        for site_data in sites_data:
            if not isinstance(site_data, dict):
                continue

            source = SourceBean()

            source.key = site_data.get("key", "")
            source.name = site_data.get("name", "")
            source.api = site_data.get("api", "")
            source.type = site_data.get("type", 0)
            source.searchable = site_data.get("searchable", 0)
            source.quickSearch = site_data.get("quickSearch", 0)
            source.filterable = site_data.get("filterable", 0)
            source.playerUrl = site_data.get("playerUrl", "")
            source.ext = site_data.get("ext", "")
            source.jar = site_data.get("jar", "")
            source.playerType = site_data.get("playerType", 0)
            source.timeout = site_data.get("timeout", 0)
            source.style = site_data.get("style", "")

            self._sites.append(source)

        print(f"[信息] 成功解析 {len(self._sites)} 个视频源")

    def _parse_lives(self):
        """解析直播源列表"""
        lives_data = self._config_data.get("lives", [])
        if not isinstance(lives_data, list):
            return

        for live_data in lives_data:
            if isinstance(live_data, dict):
                self._lives.append(live_data)

        if self._lives:
            print(f"[信息] 成功解析 {len(self._lives)} 个直播源")

    def _parse_parses(self):
        """解析解析源列表（parses字段）"""
        parses_data = self._config_data.get("parses", [])
        if not isinstance(parses_data, list):
            return

        for parse_data in parses_data:
            if not isinstance(parse_data, dict):
                continue

            parse_bean = ParseBean()
            parse_bean.name = parse_data.get("name", "")
            parse_bean.type = parse_data.get("type", 0)
            parse_bean.url = parse_data.get("url", "")
            parse_bean.ext = parse_data.get("ext", {})

            # flag 可能在 ext 中，也可能在顶层
            flag = parse_data.get("flag", [])
            if not flag and isinstance(parse_bean.ext, dict):
                flag = parse_bean.ext.get("flag", [])
            parse_bean.flag = flag if isinstance(flag, list) else []

            self._parses.append(parse_bean)

        if self._parses:
            print(f"[信息] 成功解析 {len(self._parses)} 个解析源")

    def _parse_other_fields(self):
        """解析其他字段"""
        self._spider = self._config_data.get("spider", "")
        self._wallpaper = self._config_data.get("wallpaper", "")

        if self._spider:
            print(f"[信息] 爬虫配置: {self._spider}")
        if self._wallpaper:
            print(f"[信息] 壁纸配置: {self._wallpaper}")

    def get_site_by_key(self, key):
        """
        根据 key 查找视频源

        参数:
            key: 视频源 key

        返回:
            SourceBean or None: 找到的视频源
        """
        for site in self._sites:
            if site.key == key:
                return site
        return None

    def get_sites_by_type(self, site_type):
        """
        根据类型筛选视频源

        参数:
            site_type: 类型 (0=xml, 1=json, 3=spider)

        返回:
            list: 符合类型的视频源列表
        """
        return [site for site in self._sites if site.type == site_type]
