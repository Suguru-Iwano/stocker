# coding: utf-8

import configparser
# ファイルの存在チェック用モジュール
import os

SETTING_INI_PATH = os.path.join(os.path.dirname(__file__), '../setting.ini')

# いろんなコンフィグクラスから使うかもだから、globalに置いとく
# 書き換えるなよって意味で、定数表記してる
_INI = configparser.ConfigParser()
# 指定したiniファイルが存在しない場合、エラー発生
if not os.path.exists(SETTING_INI_PATH):
    raise FileNotFoundError()
# iniファイルの読み込み
_INI.read(SETTING_INI_PATH, encoding='utf-8')


class DBConfig():
    class Db():
        _db_conf = _INI['DB']
        USER = _db_conf.get('USER')
        PASS = _db_conf.get('PASS')
        HOST = _db_conf.get('HOST')
        PORT = int(_db_conf.get('PORT'))
        NAME = _db_conf.get('DB')

        ENGINE_URL = f'mysql+pymysql://{USER}:{PASS}@{HOST}:{PORT}/{NAME}?charset=utf8'

    class Table():
        class Brand():
            NAME = 'brand'
            COL_NAMES = ('code', 'name', 'market',
                         'sector33', 'sector17', 'size', 'feature')
            COL_ORDER = {
                'CODE':     0,
                'NAME':     1,
                'MARKET':   2,
                'SECTOR33': 3,
                'SECTOR17': 4,
                'SIZE':     5,
                'FEATURE':  6
            }

        class Price():
            NAME = 'dayly_price'


class LogConfig():
    from logging import DEBUG, INFO

    LOG_LEVEL = DEBUG
    LOG_LEVEL_STREAM = DEBUG
    LOG_LEVEL_FILE = DEBUG
    LOG_LEVEL_CLOUD = INFO
    FORMAT = "%(asctime)s %(levelname)s: %(message)s"
    USE_SLACK = True
    LOG_DIR = '/var/log/stock/'
    LOG_FILE = f'{LOG_DIR}stock.log'


class TwebConfig():
    class Url():
        STOCK_INFO = "https://www.traders.co.jp/stocks_info/individual_info_basic.asp?SC={0}"

    HTML_DIR = "/tmp/stock/tweb_html/"

    class Xpath():
        brand = {
            "TOKUSYOKU": "/html/body/table/tbody/tr/td[2]/div/table/tbody/tr[2]/td/div[2]/table/tbody/tr/td[1]/table/tbody/tr[6]/td[2]/text()"
        }

        raw_prices = {
            "OPEN": "/html/body/table/tbody/tr/td[2]/div/table/tbody/tr[2]/td/div[2]/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/text()",
            "HIGH": "/html/body/table/tbody/tr/td[2]/div/table/tbody/tr[2]/td/div[2]/table/tbody/tr/td[1]/table/tbody/tr[2]/td[2]/text()",
            "LOW": "/html/body/table/tbody/tr/td[2]/div/table/tbody/tr[2]/td/div[2]/table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/text()",
            "CLOSE": "/html/body/table/tbody/tr/td[2]/div/table/tbody/tr[2]/td/div[1]/table/tbody/tr/td[2]/span[1]/text()",
            "VOLUME": "/html/body/table/tbody/tr/td[2]/div/table/tbody/tr[2]/td/div[2]/table/tbody/tr/td[1]/table/tbody/tr[4]/td[4]/text()[1]/text()"
        }

        detail = {
            "TICK": "/html/body/table/tbody/tr/td[2]/div/table/tbody/tr[2]/td/div[2]/table/tbody/tr/td[1]/table/tbody/tr[1]/td[4]/text()",
            # 発行株数
            "UNIT": "/html/body/table/tbody/tr/td[2]/div/table/tbody/tr[2]/td/div[2]/table/tbody/tr/td[2]/table/tbody/tr[2]/td[2]/text()",
            "TANISTOCKSU": "/html/body/table/tbody/tr/td[2]/div/table/tbody/tr[2]/td/div[2]/table/tbody/tr/td[2]/table/tbody/tr[4]/td[2]/text()",
            "HAITO": "/html/body/table/tbody/tr/td[2]/div/table/tbody/tr[2]/td/div[2]/table/tbody/tr/td[2]/table/tbody/tr[6]/td[4]/text()",
            "URIZAN": "/html/body/table/tbody/tr/td[2]/div/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[3]/td[2]/text()",
            "KAIZAN": "/html/body/table/tbody/tr/td[2]/div/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[5]/td[2]/text()",
            "KASHISTOCK": "/html/body/table/tbody/tr/td[2]/div/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[9]/td[2]/text()",
            "YUSHI": "/html/body/table/tbody/tr/td[2]/div/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[11]/td[2]/text()",
            "GYAKUHIBU": "/html/body/table/tbody/tr/td[2]/div/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[14]/td[3]/text()"
        }
