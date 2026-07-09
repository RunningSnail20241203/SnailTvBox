# -*- coding: utf-8 -*-
"""
日志配置模块

集中配置项目的日志系统，提供：
- setup_logging(): 初始化日志系统（控制台 + 滚动文件）
- get_logger(): 获取命名 logger

日志输出：
- 控制台：INFO 级别，简洁格式
- 文件：DEBUG 级别，详细格式（含文件名、行号），写入 logs/tvbox.log
- 文件滚动：单文件 5MB，保留 3 个备份，UTF-8 编码
"""

import os
import logging
from logging.handlers import RotatingFileHandler

# 全局标记，避免重复初始化
_initialized = False

# 控制台日志格式（简洁）
_CONSOLE_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_CONSOLE_DATE_FMT = "%Y-%m-%d %H:%M:%S"

# 文件日志格式（详细，含文件名行号）
_FILE_FORMAT = "%(asctime)s,%(msecs)03d [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
_FILE_DATE_FMT = "%Y-%m-%d %H:%M:%S"


def setup_logging(log_dir="logs", console_level=logging.INFO, file_level=logging.DEBUG,
                  max_bytes=5 * 1024 * 1024, backup_count=3):
    """初始化日志系统

    配置根 logger，添加控制台 handler 和滚动文件 handler。
    首次调用后重复调用会被忽略（幂等）。

    参数:
        log_dir: 日志文件目录（相对路径基于项目根目录或绝对路径）
        console_level: 控制台日志级别（默认 INFO）
        file_level: 文件日志级别（默认 DEBUG）
        max_bytes: 单个日志文件最大字节数（默认 5MB）
        backup_count: 保留的备份文件数量（默认 3）
    """
    global _initialized
    if _initialized:
        return

    # 解析日志目录为绝对路径（相对于项目根目录）
    if not os.path.isabs(log_dir):
        # 项目根目录：本文件所在目录的上一级
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(project_root, log_dir)

    # 创建日志目录
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "tvbox.log")

    # 配置根 logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # 设为最低级别，由各 handler 分别过滤

    # 清除已有 handler（避免重复添加）
    root_logger.handlers.clear()

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter(_CONSOLE_FORMAT, datefmt=_CONSOLE_DATE_FMT)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 文件 handler（滚动）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter(_FILE_FORMAT, datefmt=_FILE_DATE_FMT)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    _initialized = True

    # 使用 logging.getLogger 而非 get_logger，避免循环引用
    init_logger = logging.getLogger(__name__)
    init_logger.info("日志系统初始化完成，日志文件: %s", log_file)


def get_logger(name):
    """获取命名 logger

    参数:
        name: logger 名称（通常传 __name__）

    返回:
        logging.Logger 实例
    """
    return logging.getLogger(name)
