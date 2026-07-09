# -*- coding: utf-8 -*-
"""
TvBox Learn 项目入口文件
启动命令行交互界面
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.cli_app import CliApp
from server import start_server, stop_server


def main():
    """主函数，启动本地 API 服务器，然后启动 CliApp"""
    config_path = None
    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    start_server()

    try:
        app = CliApp(config_path)
        app.run()
    finally:
        stop_server()


if __name__ == "__main__":
    main()
