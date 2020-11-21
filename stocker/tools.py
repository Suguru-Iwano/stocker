# coding: utf-8

import datetime
from configparser import Error
from logging import Logger, FileHandler, Formatter, StreamHandler, getLogger
from pymysql.cursors import Cursor

import sqlalchemy as sqa
from pymysql import connect
from pymysql import connections as connections
from pyquery import PyQuery

from config import DBConfig, LogConfig
from slack import SlackHandler


def get_logger() -> Logger:

    conf = LogConfig()
    logger = getLogger(__name__)
    logger.setLevel(conf.LOG_LEVEL)
    f_handler = FileHandler(conf.LOG_FILE)
    f_handler.setLevel(conf.LOG_LEVEL_FILE)
    f_handler.setFormatter(Formatter(conf.FORMAT))
    s_handler = StreamHandler()
    s_handler.setLevel(conf.LOG_LEVEL_STREAM)
    s_handler.setFormatter(Formatter(conf.FORMAT))
    logger.addHandler(f_handler)
    logger.addHandler(s_handler)
    logger.propagate = False

    if conf.USE_SLACK:
        # Slack Handler の作成
        slack_handler = SlackHandler()
        slack_handler.setLevel(conf.LOG_LEVEL_SLACK)
        logger.addHandler(slack_handler)

    return logger


def get_connection() -> connections.Connection:
    conf = DBConfig()
    con = connect(
        user=conf.Db.USER,
        passwd=conf.Db.PASS,
        host=conf.Db.HOST,
        port=conf.Db.PORT,
        db=conf.Db.NAME
    )
    return con


def get_dbengine(url):
    # mysqlのto_sqlは、engineを使わないとエラーになる
    engine = sqa.create_engine(url, echo=True)
    return engine


def get_code_cursol(conn: connections.Connection) -> Cursor:
    """銘柄のCursorを返す
    """
    cur: Cursor = conn.cursor()
    cur.execute(f"""
        SELECT DISTINCT code from {DBConfig.Table.Name.BRAND};
    """)
    return cur


def brands_generator(mode):
    """新規/廃止する銘柄をゲット

    Yields:
        [type]: [description]
    """
    url_new = 'http://www.jpx.co.jp/listing/stocks/new/index.html'
    url_delete = 'http://www.jpx.co.jp/listing/stocks/delisted/index.html'

    query = None
    if mode == 'new':
        query = PyQuery(url_new)
    elif mode == 'delete':
        query = PyQuery(url_delete)
    else:
        raise Error("argument [mode] set 'new' or 'delete'")

    for d, i in zip(query.find('tbody > tr:even > td:eq(0)'),
                    query.find('tbody > tr:even span')):
        date = datetime.datetime.strptime(d.text, '%Y/%m/%d').date()
        yield (i.get('id'), date)


def insert_brands_to_db(mode: str):
    """新規/廃止銘柄を格納

    Args:
        mode ([type]): 'new' or 'delete'
    """
    sql = f'INSERT INTO {mode}_brands(code,date) VALUES(?,?)'
    with get_connection() as conn:
        conn.executemany(sql, brands_generator(mode))
        conn.commit()


def table_isexist(conn, dbName, tableName):
    """
    テーブルが存在しているか
    """
    if 0 == conn.cursor().execute(f"""
        SELECT TABLE_NAME
        FROM information_schema.tables
        WHERE table_schema='{dbName}'
        AND table_name='{tableName}'
        LIMIT 1;
        """):
        return False
    return True
