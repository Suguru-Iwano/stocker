# coding: utf-8

import os
import time

from google.cloud.pubsub_v1 import PublisherClient
from google.cloud.pubsub_v1.futures import Future

from stocker.dba import Dba
from stocker.tools import get_logger

ENV_KEY_MAX_EXEC_SEC = 'MAX_EXEC_SEC'
ENV_KEY_PROJECT = 'PROJECT'
ENV_KEY_TOPIC = 'TOPIC'


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


def publish(project: str, topic: str, message='') -> Future:
    """Pub/Sub の Publish 実行

    Args:
        project (str): プロジェクト名
        topic (str): トピック名
        message (str): 送信するメッセージ
    """
    if not project or not topic:
        raise FatalException("Project or topic is None or blank.")

    publisher = PublisherClient()

    return publisher.publish(
        # トピックのパス
        publisher.topic_path(project, topic),
        # str -> byte に変換
        message.encode()
    )


def main():
    """エントリポイント
    """

    try:
        # 環境情報を取得とチェック
        max_exec_sec_str: str = os.getenv(ENV_KEY_MAX_EXEC_SEC)
        project_name: str = os.getenv(ENV_KEY_PROJECT)
        topic_name: str = os.getenv(ENV_KEY_TOPIC)
        if not max_exec_sec_str or not project_name or not topic_name:
            raise FatalException("Please set environment parameter.")

        dba = Dba()
        # 待ち時間：全体の実行時間 / 処理数
        wait_sec = float(max_exec_sec_str) / dba.get_code_count()

        # Publish(子の処理を起動)
        for code in dba.get_code_iter():
            future: Future = publish(
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
