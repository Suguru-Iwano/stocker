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
VPN_LIST_URL = 'http://www.vpngate.net/api/iphone/'
PROXY_LIST_URL = 'https://www.proxyscan.io/api/proxy?format=json&type=https,socks5&level=anonymous,elite&last_check=1500&uptime=100&ping=80&limit=20'
STOCK_INFO_URL = 'https://www.traders.co.jp/stocks_info/individual_info_basic.asp?SC={0}'


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


def random_sleep(max_sleep_sec) -> None:
    time.sleep(random.uniform(0, max_sleep_sec))


def _get_random_vps() -> str:
    """VPN Gate の VPN の中から、ランダムな1つのIPを返す

    Returns:
        str: Proxyの情報
    """
    vpn_data = requests.get(VPN_LIST_URL).text.replace('\r', '')
    servers = [line.split(',') for line in vpn_data.split('\n')]
    labels = servers[1]
    labels[0] = labels[0][1:]
    servers = [s for s in servers[2:] if len(s) > 1]
    return random.choice(servers)[1]


def _is_valid_ip(ip_str: str) -> bool:
    """文字列がIPアドレスのパターンかチェック
    """
    import ipaddress
    try:
        ipaddress.ip_address(ip_str)
        return True
    except:
        return False


def _get_proxy_url(proxy_list_url: str) -> str:
    proxies = json.loads(requests.get(proxy_list_url).text)
    p = random.choice(proxies)

    if not _is_valid_ip(p['Ip']):
        raise RetriableException('Illegal Proxy IP.')
    proxy_url = f"{p['Type'][0]}://{p['Ip']}:{p['Port']}"
    return proxy_url


@retry(RETRY_ERRORS, tries=10, delay=2)
def request_with_proxy(target_url: str, proxy_list_url: str) -> Response:
    """TradersWeb の 1銘柄のHTMLを返す

    Args:
        target_url (str): [description]
        proxy (str): [description]

    Returns:
        Response: [description]
    """
    # プロキシを設定
    proxy_url = _get_proxy_url(proxy_list_url)
    proxies = {}
    if proxy_url:
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"}

    return requests.get(
        target_url,
        proxies=proxies,
        headers=headers,
        verify=False,
        timeout=(7.0, 9.0))


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

        # サーバに負荷をかけないように、、、
        random_sleep(float(max_exec_sec_str))

        # pubsubからデータを取得
        stock_code: str = get_event_data(event)
        response = request_with_proxy(
            STOCK_INFO_URL.format(stock_code),
            PROXY_LIST_URL
        )
        stock_html_bytes: bytes = response.content
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
