# coding: utf-8

from stocker.stkdaily_c import *
from stocker.stkdaily_c import _is_valid_ip


def test_random_sleep_no_err():
    try:
        random_sleep(0.005)
    except:
        assert False
    else:
        assert True


def test_is_valid_ip_true_all_0():
    assert _is_valid_ip('000.000.000.000')


def test_is_valid_ip_true_all_9():
    assert _is_valid_ip('999.999.999.999')


def test_is_valid_ip_true_random():
    assert _is_valid_ip('123.456.789.012')


def test_is_valid_ip_false_a():
    assert not _is_valid_ip('000.0a0.000.000')


def test_is_valid_ip_false_a_ja():
    assert not _is_valid_ip('000.0あ0.000.000')


def test_is_valid_ip_false_none():
    assert not _is_valid_ip('000.00.000.000')


def test_is_valid_ip_false_all_space():
    assert not _is_valid_ip('000.0 0.000.000')


def test_get_random_vpn_ip_is_valid_ip():
    assert _is_valid_ip(get_random_vpn_ip())


def test_request_with_proxy_no_proxy():
    assert 200 == request_with_proxy(
        'https://www.google.com/search').status_code


def test_request_with_proxy_random_proxy():
    proxy = get_random_vpn_ip()
    # proxy が None でないことを保証
    assert proxy
    assert 200 == request_with_proxy(
        'https://www.google.com/search', proxy).status_code


def test_request_with_proxy_err_illegal_proxy():
    try:
        request_with_proxy('https://www.google.com/search', 'dummy_proxy')
    except FatalException:
        assert True
    else:
        assert False

# TODO:save_bytes_to_gdrive
# TODO:insert_stock_data
