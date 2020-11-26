# coding: utf-8

from logging import StreamHandler, Formatter, Logger, getLogger

from google.cloud.logging_v2.client import Client
from google.cloud.logging_v2.handlers import CloudLoggingHandler

from retry import retry

from config import LogConfig


def get_logger() -> Logger:

    s_handler = StreamHandler()
    s_handler.setFormatter(Formatter(LogConfig.FORMAT))
    s_handler.setLevel(LogConfig.LOG_LEVEL_STREAM)

    # client = Client(project=ProjectConfig.ID,
    #                 credentials=ProjectConfig.CREDENTIAL)
    client = Client()
    g_handler = CloudLoggingHandler(client)
    g_handler.setFormatter(Formatter(LogConfig.FORMAT))
    g_handler.setLevel(LogConfig.LOG_LEVEL_CLOUD)

    logger = getLogger('stocker')
    logger.setLevel(LogConfig.LOG_LEVEL)
    logger.addHandler(g_handler)
    logger.propagate = False

    return logger
