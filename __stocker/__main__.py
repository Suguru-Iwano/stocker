#!/usr/bin/env python3
# coding: utf-8

from datetime import datetime as dt
from argparse import ArgumentParser, Namespace

from walker import *
from tools import *

JPX_BRAND_EXCELL = 'https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls'


def get_option() -> Namespace:
    """コマンドライン引数を取得
    """
    argparser = ArgumentParser()
    argparser.add_argument('-m', '--mode', type=str,
                           help='INIT')
    argparser.add_argument('-d', '--date', type=str,
                           help='INIT')
    return argparser.parse_args()


def main():
    logger = get_logger()

    args = get_option()

    mode = args.mode or ''
    mode = mode.upper()

    if not mode:
        logger.error('please set mode.')
        raise Exception

    date = None
    if args.date:
        date = dt.strptime(args.date, '%Y%m%d')

    logger.info('START ' + mode)

    try:
        if mode == 'DOWNLOAD_DAILY_DATA':
            walker = TwebWalker()
            walker.save_all_stockhtml()
            logger.debug('daily data download is complete.')

        elif mode == 'INSTALL_DAILY_DATA':
            walker = TwebWalker()
            if date:
                walker.date = date
            walker.get_all_stockdata_fromhtml()
            logger.debug('daily data install is complete.')

        # elif mode == 'GET_NEW_BRAND':
        #     insert_brands_to_db(mode='new')

        # elif mode == 'GET_DELETE_BRAND':
        #     insert_brands_to_db(mode='delete')

    except Exception as e:
        logger.exception(e)
        logger.info('END_WITH_ERROR ' + mode)

    else:
        logger.info('END ' + mode)


if __name__ == '__main__':
    main()
