# coding: utf-8

from typing import Any, Iterator

from google.cloud.bigquery import Client
from google.cloud.bigquery.table import RowIterator


class Dba():
    def __init__(self) -> None:
        self.client: Client = Client()

    def _execute(self, query: str) -> Any:
        query_job = self.client.query(query)
        result_iter = query_job.result()
        return result_iter

    def get_code_iter(self) -> RowIterator:
        """銘柄のiteratorを返す
        """
        return self._execute(f"""
            SELECT DISTINCT code FROM stocker_dataset.brand;
        """)

    # def insert_brands_to_db(self, mode: str):
    #     """新規/廃止銘柄を格納
    #     Args:
    #         mode ([type]): 'new' or 'delete'
    #     """
    #     sql = f'INSERT INTO brands_{mode}(code,date) VALUES(?,?)'
    #     with get_connection() as conn:
    #         conn.executemany(sql, brands_generator(mode))
    #         conn.commit()

    # def table_isexist(self, conn, dbName, tableName):
    #     """
    #     テーブルが存在しているか
    #     """
    #     if 0 == conn.cursor().execute(f"""
    #         SELECT TABLE_NAME
    #         FROM information_schema.tables
    #         WHERE table_schema='{dbName}'
    #         AND table_name='{tableName}'
    #         LIMIT 1;
    #         """):
    #         return False
    #     return True

    # def brands_generator(self, mode):
    #     """新規/廃止する銘柄をゲット

    #     Yields:
    #         [type]: [description]
    #     """
    #     url_new = 'http://www.jpx.co.jp/listing/stocks/new/index.html'
    #     url_delete = 'http://www.jpx.co.jp/listing/stocks/delisted/index.html'

    #     query = None
    #     if mode == 'new':
    #         query = PyQuery(url_new)
    #     elif mode == 'delete':
    #         query = PyQuery(url_delete)
    #     else:
    #         raise Exception("argument [mode] set 'new' or 'delete'")

    #     for d, i in zip(query.find('tbody > tr:even > td:eq(0)'),
    #                     query.find('tbody > tr:even span')):
    #         date = dt.strptime(d.text, '%Y/%m/%d').date()
    #         yield (i.get('id'), date)
