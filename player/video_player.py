# -*- coding: utf-8 -*-
"""
视频播放器模块

调用系统外部播放器（VLC、mpv）播放视频。
"""

import os
import subprocess
import shutil
from typing import List, Dict, Optional
from pathlib import Path


class VideoPlayer:
    """视频播放器
    
    自动检测系统安装的播放器，调用播放器播放视频。
    
    支持的播放器：
    - VLC: 功能最全，支持 m3u8/mp4 等各种格式
    - mpv: 轻量高效，支持 m3u8/mp4
    
    播放器在独立进程中运行，不阻塞主程序。
    """
    
    # VLC 的常见安装路径
    VLC_PATHS = [
        r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
        r"D:\Program Files\VideoLAN\VLC\vlc.exe",
        r"D:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
    ]
    
    # mpv 的常见安装路径
    MPV_PATHS = [
        r"C:\Program Files\mpv\mpv.exe",
        r"C:\Program Files (x86)\mpv\mpv.exe",
        r"C:\mpv\mpv.exe",
        r"D:\Program Files\mpv\mpv.exe",
        os.path.expanduser(r"~\scoop\apps\mpv\current\mpv.exe"),  # Scoop 安装
        os.path.expanduser(r"~\AppData\Local\Microsoft\WindowsApps\mpv.exe"),  # Microsoft Store
    ]
    
    def __init__(self):
        """初始化播放器"""
        self._available_players: List[Dict] = []
        self._detected = False
    
    def detect_players(self) -> List[Dict]:
        """检测系统中可用的播放器
        
        返回：
            播放器信息列表，每个元素包含：
            {
                "name": "VLC",
                "path": "C:\\Program Files\\...\\vlc.exe",
                "type": "vlc"
            }
        """
        if self._detected:
            return self._available_players.copy()
        
        self._available_players = []
        
        # 检测 VLC
        vlc_path = self._find_vlc()
        if vlc_path:
            self._available_players.append({
                "name": "VLC",
                "path": vlc_path,
                "type": "vlc"
            })
        
        # 检测 mpv
        mpv_path = self._find_mpv()
        if mpv_path:
            self._available_players.append({
                "name": "mpv",
                "path": mpv_path,
                "type": "mpv"
            })
        
        self._detected = True
        return self._available_players.copy()
    
    def _find_vlc(self) -> Optional[str]:
        """查找 VLC 播放器路径
        
        返回：
            VLC 可执行文件路径，未找到返回 None
        """
        # 先检查 PATH
        vlc_in_path = shutil.which("vlc")
        if vlc_in_path:
            return vlc_in_path
        
        # 检查常见安装路径
        for path in self.VLC_PATHS:
            if os.path.isfile(path):
                return path
        
        return None
    
    def _find_mpv(self) -> Optional[str]:
        """查找 mpv 播放器路径
        
        返回：
            mpv 可执行文件路径，未找到返回 None
        """
        # 先检查 PATH
        mpv_in_path = shutil.which("mpv")
        if mpv_in_path:
            return mpv_in_path
        
        # 检查常见安装路径
        for path in self.MPV_PATHS:
            if os.path.isfile(path):
                return path
        
        return None
    
    def has_player(self) -> bool:
        """检查是否有可用的播放器
        
        返回：
            True 表示至少有一个播放器可用
        """
        players = self.detect_players()
        return len(players) > 0
    
    def get_default_player(self) -> Optional[Dict]:
        """获取默认播放器（优先 VLC）
        
        返回：
            播放器信息，没有返回 None
        """
        players = self.detect_players()
        if not players:
            return None
        
        # 优先 VLC
        for p in players:
            if p["type"] == "vlc":
                return p
        
        return players[0]
    
    def play(self, url: str, player_type: str = None) -> Dict:
        """播放视频
        
        在独立进程中启动播放器，不阻塞主程序。
        
        参数：
            url: 视频地址（支持 m3u8/mp4 等）
            player_type: 播放器类型（"vlc" 或 "mpv"），None 自动选择
            
        返回：
            {
                "success": True/False,
                "player": "VLC",
                "error": ""
            }
        """
        if not url:
            return {
                "success": False,
                "player": None,
                "error": "视频地址为空"
            }
        
        # 检测播放器
        players = self.detect_players()
        if not players:
            return {
                "success": False,
                "player": None,
                "error": "未检测到播放器。请安装 VLC 或 mpv。\n"
                         "VLC 下载: https://www.videolan.org/vlc/\n"
                         "mpv 下载: https://mpv.io/installation/"
            }
        
        # 选择播放器
        player_info = None
        if player_type:
            for p in players:
                if p["type"] == player_type:
                    player_info = p
                    break
            if not player_info:
                return {
                    "success": False,
                    "player": None,
                    "error": f"未找到 {player_type} 播放器"
                }
        else:
            player_info = self.get_default_player()
        
        # 启动播放器
        player_path = player_info["path"]
        player_name = player_info["name"]
        
        try:
            print(f"[VideoPlayer] 正在启动 {player_name}...")
            print(f"[VideoPlayer] 播放地址: {url}")
            
            # 使用 subprocess 启动播放器
            # Popen 不等待进程结束，所以不会阻塞
            if player_info["type"] == "vlc":
                # VLC 参数：--no-interact 不弹出交互界面
                subprocess.Popen(
                    [player_path, "--no-interact", url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:  # mpv
                subprocess.Popen(
                    [player_path, url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            
            return {
                "success": True,
                "player": player_name,
                "error": ""
            }
            
        except FileNotFoundError:
            return {
                "success": False,
                "player": player_name,
                "error": f"播放器不存在: {player_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "player": player_name,
                "error": f"启动播放器失败: {str(e)}"
            }
    
    def get_install_hint(self) -> str:
        """获取播放器安装提示
        
        返回：
            安装说明文本
        """
        return """
未检测到视频播放器，请安装以下任一播放器：

1. VLC Media Player（推荐）
   - 官网: https://www.videolan.org/vlc/
   - 支持格式全，无需额外配置
   - 支持 m3u8、mp4、flv 等各种格式

2. mpv Player
   - 官网: https://mpv.io/installation/
   - 轻量高效，启动快
   - 支持 m3u8、mp4 等格式

安装后重新运行程序即可。
""".strip()