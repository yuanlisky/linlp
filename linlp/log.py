# -*- coding: utf-8 -*-
"""
日志处理,简单的输出的console,样式为sys.stderr,级别为debug
"""
import sys
import logging


log_console = logging.StreamHandler(sys.stderr)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(log_console)
