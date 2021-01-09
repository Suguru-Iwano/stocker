# coding: utf-8

import time

from stocker.stkdaily_c import (PROXY_LIST_URL, FatalException, _get_proxy_list,
                                _is_valid_ip, request_with_proxy)


def test_is_valid_ip_true_min():
    assert _is_valid_ip('000.000.000.000')


def test_is_valid_ip_true_max():
    assert _is_valid_ip('255.255.255.255')


def test_is_valid_ip_false_a():
    assert not _is_valid_ip('000.0a0.000.000')


def test_is_valid_ip_false_a_ja():
    assert not _is_valid_ip('000.0あ0.000.000')


def test_is_valid_ip_false_none():
    assert not _is_valid_ip('000..000.000')


def test_is_valid_ip_false_all_space():
    assert not _is_valid_ip('000.0 0.000.000')


def test_request_with_proxy_random_proxy():
    time.sleep(1)
    proxy_list_url = PROXY_LIST_URL
    assert 200 == request_with_proxy(
        'https://www.bing.com/', proxy_list_url).status_code


def test_request_with_proxy_http_proxy():
    time.sleep(1)
    proxy_list_url = "https://www.proxyscan.io/api/proxy?type=http&format=json&limit=20"
    assert 200 == request_with_proxy(
        'https://www.bing.com/', proxy_list_url).status_code


def test_request_with_proxy_https_proxy():
    time.sleep(1)
    proxy_list_url = "https://www.proxyscan.io/api/proxy?type=https&format=json&limit=20"
    assert 200 == request_with_proxy(
        'https://www.bing.com/', proxy_list_url).status_code


def test_request_with_proxy_socks4_proxy():
    time.sleep(1)
    proxy_list_url = "https://www.proxyscan.io/api/proxy?type=socks4&format=json&limit=20"
    assert 200 == request_with_proxy(
        'https://www.bing.com/', proxy_list_url).status_code


def test_request_with_proxy_socks5_proxy():
    time.sleep(1)
    proxy_list_url = "https://www.proxyscan.io/api/proxy?type=socks5&format=json&limit=20"
    assert 200 == request_with_proxy(
        'https://www.bing.com/', proxy_list_url).status_code

# TODO:save_bytes_to_gdrive
# TODO:insert_stock_data
