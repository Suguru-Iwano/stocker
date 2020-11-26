# coding: utf-8

import pathlib
import time
from configparser import Error
from datetime import datetime as dt

import requests
from bs4 import BeautifulSoup
from retry import retry

from config import TwebConfig, DBConfig
from tools import *
from dba import *


class TwebWalker():

    def __init__(self):
        self.logger = get_logger()
        self.conf = TwebConfig()
        self.date: dt = dt.today()  # ファイル読み書き用

    @retry(tries=10, delay=60, backoff=2)
    def _get_stockHtml_byte(self, code):
        target_url = self.conf.Url.STOCK_INFO.format(code)
        # Requestsを使って、webから取得
        res = requests.get(target_url)
        if 500 == res.status_code:
            self.logger.warning(f'skipped {code}: 500')
            return
        elif 200 != res.status_code:
            raise Error

        return res.content  # html

    def save_all_stockhtml(self):
        """TradersWebからHMTLを取得
        """
        code_cursor = get_code_cursol(get_connection())
        date_str = self.date.strftime('%Y%m%d')

        code_rows = code_cursor.fetchall()
        for row in code_rows:
            code = row[0]
            html: bytes = self._get_stockHtml_byte(code)

            if html:
                with open(f'{self.conf.HTML_DIR}{code}_{date_str}.html', 'wb') as file:
                    file.write(html)
                self.logger.debug(f'downloaded html {code}')
            time.sleep(0.3)

    def _get_col_info_dic(self, lx_soup, col_xpath_dic):
        # キーだけ複製（DBの列名のみの辞書になる）
        col_info_dic = dict.fromkeys(col_xpath_dic.copy())
        for column, xpath in col_xpath_dic.items():
            col_info_dic[column] = lx_soup.xpath(xpath)
        return col_info_dic

    def bef_castnum(self, text: str):
        return text.strip().replace(',', '')

    def _save_stockinfo(self, str_html, code, test=False):
        # 要素を抽出
        soup = BeautifulSoup(str_html, 'html.parser')
        lx_soup = lxml.html.fromstring(str(soup))

        print(lx_soup.xpath(
            "/html/body/table/tbody/tr/td[2]/div/table/tbody/tr[2]/td/div[1]/div[2]/table/tbody/tr/td/text()"))

        print(lx_soup.xpath(
            "/html/body/table/tbody/tr/td[2]/div/table/tbody/tr[2]/td/div[2]/table/tbody/tr/td[1]/table/tbody/tr[6]/td[2]/text()"))

        # 銘柄テーブルの更新
        brand_dic = self._get_col_info_dic(
            lx_soup, self.conf.Xpath.brand)
        sql = f"""
            REPLACE {DBConfig.Table.Name.BRAND}
            SET TOKUSYOKU = '{brand_dic['TOKUSYOKU']}'
            WHERE CODE = '{code}'
        """
        self.logger.debug(sql)
        if not test:
            with get_connection() as conn:
                conn.cursor().execute(sql)
                conn.commit()

        # 価格テーブルの更新
        price_dic = self._get_col_info_dic(
            lx_soup, self.conf.Xpath.raw_prices)
        o = float(self.bef_castnum(price_dic['OPEN']))  # 始値
        h = float(self.bef_castnum(price_dic['HIGH']))  # 高値
        l = float(self.bef_castnum(price_dic['LOW']))  # 安値
        c = float(self.bef_castnum(price_dic['CLOSE']))  # 終値
        v = int(self.bef_castnum(price_dic['VOLUME']))   # 出来高
        sql = f"""
        INSERT INTO {DBConfig.Table.Name.RAW_PRICE}
        values(%s,%s,%s,%s,%s,%s,%s)
        """
        self.logger.debug(sql)
        if not test:
            with get_connection() as conn:
                conn.cursor().execute(sql, (code, self.date, o, h, l, c, v))
                conn.commit()

        # 詳細情報テーブルの更新
        detail_dic = self._get_col_info_dic(
            lx_soup, self.conf.Xpath.detail)
        tick = int(self.bef_castnum(detail_dic['TICK']))
        unit = int(self.bef_castnum(detail_dic['UNIT'].replace('百万', '')))
        tanisu = int(self.bef_castnum(detail_dic['TANISU']))
        haito = float(self.bef_castnum(detail_dic['HAITO']))
        kaizan = int(self.bef_castnum(detail_dic['KAIZAN']))
        urizan = int(self.bef_castnum(detail_dic['URIZAN']))
        kashistock = int(self.bef_castnum(detail_dic['KASHISTOCK']))
        yushi = int(self.bef_castnum(detail_dic['YUSHI']))
        gyakuhibu = float(self.bef_castnum(detail_dic['GYAKUHIBU']))
        sql = f"""
        INSERT INTO {DBConfig.Table.Name.DETAIL}
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        self.logger.debug(sql)
        if not test:
            with get_connection() as conn:
                conn.cursor().execute(sql, (code, self.date, tick, unit, tanisu,
                                            haito, kaizan, urizan, kashistock, yushi, gyakuhibu))
                conn.commit()

    def get_all_stockdata_fromhtml(self, test=False):
        """保存したHTMLから要素を抜き出し、DBに保存
        """
        date_str = self.date.strftime('%Y%m%d')
        for path in pathlib.Path(self.conf.HTML_DIR).glob(f'*_{date_str}.html'):
            code = path.name[:4]
            with open(path, 'r', encoding='sjis') as file:
                html = file.read()
                self._save_stockinfo(html, code, self.date, test=test)
            self.logger.debug(f'installed html {code}')
