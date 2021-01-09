# coding: utf-8

import base64
import json
import os
import random
import time

import requests
import urllib3
from requests import Response
from requests.exceptions import (ConnectTimeout, ProxyError, ReadTimeout,
                                 SSLError)
from retry import retry

from stocker.tools import get_logger

# SSLのWarningを無視する
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


ENV_KEY_MAX_EXEC_SEC = 'MAX_EXEC_SEC'

#PROXY_LIST_URL = 'https://www.proxyscan.io/api/proxy?format=json&last_check=1500&uptime=100&ping=100&type=https,socks5&level=anonymous,elite&limit=20'
PROXY_LIST_URL = 'https://www.proxyscan.io/api/proxy?format=json&last_check=9800&uptime=50&ping=120&type=https,socks5&level=anonymous,elite&limit=20'
STOCK_INFO_URL = 'https://www.traders.co.jp/stocks_info/individual_info_basic.asp?SC={0}'

# proxy_listを取得
proxy_list: list = get_proxy_list(PROXY_LIST_URL)


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


RETRY_ERRORS = (RetriableException, SSLError, ProxyError,
                ConnectionError, ReadTimeout, ConnectTimeout)


def get_event_data(event) -> str:
    return base64.b64decode(event['data']).decode('utf-8')


def _is_valid_ip(ip_str: str) -> bool:
    """文字列がIPアドレスのパターンかチェック
    """
    import ipaddress
    try:
        ipaddress.ip_address(ip_str)
        return True
    except:
        return False


def get_proxy_list(proxy_list_url: str) -> list:
    return json.loads(requests.get(proxy_list_url).text)


def _get_proxy(proxies: list) -> str:
    p = proxies.pop()

    if not _is_valid_ip(p['Ip']):
        raise RetriableException('Illegal Proxy IP.')
    proxy = f"{p['Type'][0]}://{p['Ip']}:{p['Port']}"
    return proxy


@retry(RETRY_ERRORS, tries=len(proxy_list))
def request_with_proxy(target_url: str, proxy_list: list) -> Response:
    """TradersWeb の 1銘柄のHTMLを返す

    Args:
        target_url (str): [description]
        proxy (str): [description]

    Returns:
        Response: [description]
    """
    # プロキシを設定
    proxy: str = _get_proxy(proxy_list)
    proxies = {
        'http': proxy,
        'https': proxy
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"}
# TODO:headers:複数ランダム
    return requests.get(
        target_url,
        proxies=proxies,
        headers=headers,
        verify=False,
        timeout=(10.0, 12.0))


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
        max_exec_sec_str: str = os.getenv(ENV_KEY_MAX_EXEC_SEC) or ''
        if not max_exec_sec_str:
            raise FatalException("Please set environment parameter.")

        # pubsubからデータを取得
        stock_code: str = get_event_data(event)

        # リクエスト
        response = request_with_proxy(
            STOCK_INFO_URL.format(stock_code),
            proxy_list
        )
        stock_html_bytes: bytes = response.content
        status_code: int = response.status_code

        # ステータスコードチェック
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
