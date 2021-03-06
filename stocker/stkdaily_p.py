# coding: utf-8

import os
import time
from random import random
from typing import Any

import requests
from google.cloud import pubsub_v1

from stocker.dba import Dba
from stocker.tools import get_logger

ENV_KEY_MAX_EXEC_SEC = 'MAX_EXEC_SEC'
ENV_KEY_PROJECT = 'PROJECT'
ENV_KEY_TOPIC = 'TOPIC'

# VPN_LIST_URL = 'http://www.vpngate.net/api/iphone/'


class RetriableException(Exception):
    """
    リトライするエラー
    これ以外は、エラー吐いて終了
    """
    pass


class FatalException(Exception):
    """
    リトライするエラー
    これ以外は、エラー吐いて終了
    """
    pass


# def _get_vps_list() -> list:
#     """VPN Gate の VPN の中から、ランダムな1つのIPを返す

#     Returns:
#         str: Proxyの情報
#     """
#     vpn_data = requests.get(VPN_LIST_URL).text.replace('\r', '')
#     servers = [line.split(',') for line in vpn_data.split('\n')]
#     labels = servers[1]
#     labels[0] = labels[0][1:]
#     servers = [s for s in servers[2:] if len(s) > 1]
#     return servers


def random_sleep(max_sleep_sec) -> None:
    time.sleep(random.uniform(0, max_sleep_sec))


def publish(project: str, topic: str, message='') -> Any:
    """Pub/Sub の Publish 実行

    Args:
        project (str): プロジェクト名
        topic (str): トピック名
        message (str): 送信するメッセージ
    """
    if not project or not topic:
        raise FatalException("Project or topic is None or blank.")

    publisher = pubsub_v1.PublisherClient()
    topic_path: str = f'projects/{project}/topics/{topic}'

    return publisher.publish(
        # トピックのパス
        topic_path,
        # str -> byte に変換
        message.encode()
    )


def main():
    """エントリポイント
    """

    try:
        # 環境情報を取得とチェック
        max_exec_sec_str: str = os.getenv(ENV_KEY_MAX_EXEC_SEC) or ''
        project_name: str = os.getenv(ENV_KEY_PROJECT) or ''
        topic_name: str = os.getenv(ENV_KEY_TOPIC) or ''
        if not max_exec_sec_str or not project_name or not topic_name:
            raise FatalException("Please set environment parameter.")

        dba = Dba()
        # 待ち時間：全体の実行時間 / 処理数
        code_iter = dba.get_code_iter()
        wait_sec = float(max_exec_sec_str) / code_iter.total_rows

        # Publish(子の処理を起動)
        for code in code_iter:
            future = publish(
                project_name,
                topic_name,
                code
            )
            get_logger().info(str(future.result()))
            time.sleep(wait_sec)

    except RetriableException:
        raise

    except Exception:
        get_logger().exception('Cant retry.')
