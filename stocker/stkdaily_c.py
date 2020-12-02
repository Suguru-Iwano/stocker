# coding: utf-8

import base64
import random
import time
import requests
from requests import Request
import random
import os

from tools import get_logger

ENV_KEY_MAX_EXEC_SEC = 'MAX_EXEC_SEC'
VPN_LIST_URL = 'http://www.vpngate.net/api/iphone/'
STOCK_INFO_URL = 'https://www.traders.co.jp/stocks_info/individual_info_basic.asp?SC={0}'


class RetriableException(Exception):
    """
    リトライするエラー
    これ以外は、エラー吐いて終了
    """

    def __init__(self):
        pass

    def __str__(self):
        return "リトライ用（異常終了させる）"

class FatalException(Exception):
    """
    リトライするエラー
    これ以外は、エラー吐いて終了
    """

    def __init__(self):
        pass

    def __str__(self):
        return "リトライ用（異常終了させる）"

def get_event_data(event) -> str:
    return base64.b64decode(event['data']).decode('utf-8')


def random_sleep(max_sleep_sec) -> None:
    time.sleep(random.random(0, max_sleep_sec))


def get_random_vpn_ip() -> str:
    """VPN Gate の VPN の中から、ランダムな1つのIPを返す

    Returns:
        str: VPNのIP
    """
    vpn_data = requests.get(VPN_LIST_URL).text.replace('\r', '')
    servers = [line.split(',') for line in vpn_data.split('\n')]
    labels = servers[1]
    labels[0] = labels[0][1:]
    servers = [s for s in servers[2:] if len(s) > 1]
    return random.choice(servers)[1]


def _check_ip(ip_str: str) -> bool:
    """文字列がIPアドレスのパターンかチェック
    """
    import socket
    try:
        socket.inet_aton(ip_str)
        return True
    except socket.error:
        return False


def request_with_proxy(target_url: str, proxy='') -> Request:
    """TradersWeb の 1銘柄のHTMLを返す

    Args:
        target_url (str): [description]
        proxy (str): [description]

    Returns:
        Response: [description]
    """
    # プロキシを設定
    proxies = None
    if proxy:
        if _check_ip(proxy):
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
        else:
            raise FatalException('Iregal proxy.')

    return requests.get(target_url, proxies=proxies)


def save_bytes_to_gdrive(target_bytes: bytes, code: str):
    pass


def insert_stock_data(html_bytes: bytes, code: str):
    pass


def main(event, context):
    """Pub/Subから起動
    stocker_daily_subのエントリポイント
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    try:
        # 環境情報を取得とチェック
        max_exec_sec_str: str = os.getenv(ENV_KEY_MAX_EXEC_SEC)
        if not max_exec_sec_str:
            raise FatalException("Please set environment parameter.")

        # サーバに負荷をかけないように、、、
        random_sleep(float(max_exec_sec_str))

        # pubsubからデータを取得
        stock_code: str = get_event_data(event)
        response = request_with_proxy(
            STOCK_INFO_URL.format(stock_code),
            get_random_vpn_ip()
        )
        stock_html_bytes: bytes = response.context
        status_code: int = response.status_code

        # 正常
        if 200 == status_code:
            save_bytes_to_gdrive(stock_html_bytes, stock_code)

        # 銘柄がない
        elif 500 == status_code:
            get_logger().warning(f'skipped {stock_code}: 500')

        else:
            raise RetriableException(
                f'Return {status_code} when get stock html.')

    # リトライ可能エラーは、異常終了させてFunctionsを再実行
    except RetriableException:
        raise

    # 意図しないエラーは、ログ吐くだけで異常終了にしない
    except Exception:
        get_logger().exception('Cant retry.')
