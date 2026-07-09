# -*- coding: utf-8 -*-
"""
TvBox Learn 项目入口文件
启动命令行交互界面
"""

import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import setup_logging, get_logger
from ui.cli_app import CliApp
from server import start_server, stop_server


def main():
    """主函数，启动本地 API 服务器，然后启动 CliApp"""
    # 初始化日志系统（必须在所有其他模块使用 logger 之前完成）
    setup_logging()
    logger = get_logger(__name__)

    config_path = None
    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    logger.info("TvBox 启动，config_path=%s", config_path)
    logger.info("Python 版本: %s", sys.version.replace("\n", " "))
    logger.info("工作目录: %s", os.getcwd())

    logger.info("启动本地 API 服务器...")
    start_server()
    logger.info("本地 API 服务器已启动")

    try:
        logger.info("创建 CliApp 实例...")
        app = CliApp(config_path)
        logger.info("CliApp 创建成功，进入主循环")
        app.run()
        logger.info("CliApp 主循环正常退出")
    except Exception:
        logger.critical("程序异常退出", exc_info=True)
        raise
    finally:
        logger.info("正在关闭本地 API 服务器...")
        stop_server()
        logger.info("本地 API 服务器已关闭，程序退出")


if __name__ == "__main__":
    main()
