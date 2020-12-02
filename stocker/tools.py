# coding: utf-8

from logging import StreamHandler, Formatter, Logger, getLogger, DEBUG, INFO

from google.cloud.logging_v2.client import Client
from google.cloud.logging_v2.handlers import CloudLoggingHandler


def get_logger(logger_name='stocker') -> Logger:
    foramt = Formatter("%(asctime)s %(levelname)s: %(message)s")

    s_handler = StreamHandler()
    s_handler.setFormatter(foramt)
    s_handler.setLevel(INFO)

    # client = Client(project=ProjectConfig.ID,
    #                 credentials=ProjectConfig.CREDENTIAL)
    client = Client()
    g_handler = CloudLoggingHandler(client)
    g_handler.setFormatter(foramt)
    g_handler.setLevel(DEBUG)

    logger = getLogger(logger_name)
    logger.setLevel(DEBUG)
    logger.addHandler(g_handler)
    logger.propagate = False

    return logger
