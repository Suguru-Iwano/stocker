# # coding: utf-8

# import pandas as pd

# from .config import *
# from .tools import *

# IDOUHEIKIN = [25, 75, 100, 200]


# def sma(pd, closeList=[], term=5):
#     '''単純移動平均の計算'''
#     return list(pd.Series(closeList).rolling(term).mean())


# def ema(pd, closeList=[], term=5):
#     '''指数平滑移動平均の計算'''
#     return list(pd.Series(closeList).ewm(span=term).mean())


# def ema1(pd, closeList=[], term=5):
#     '''指数平滑移動平均の計算(修正版)'''
#     s = pd.Series(closeList)
#     sma = s.rolling(term).mean()[:term]
#     return list(pd.concat([sma, s[term:]]).ewm(span=term, adjust=False).mean())


# def analize():
#     # 銘柄一覧

#     # PRO Marketは価格情報がないため除外
#     query = "select * from brand where market not in ('PRO Market')"
#     df_b = pd.read_sql(query, con=tools.get_dbengine(conDb.ENGINE_URL))

#     df_dic = {}  # {code:df}

#     # 銘柄でループ
#     for code in df_b['code']:
#         query = f"select * from raw_prices where code='{code}'"
#         df = pd.read_sql(query, con=tools.get_dbengine(
#             config.DBConfig.Db.ENGINE_URL))

#         # 移動平均を計算
#         for period in IDOUHEIKIN:
#             df[f'{period}MA前日比'] = 0
#             df[f'{period}MA'] = sma(pd, df['close'], period)
#             ma_index = df.columns.get_loc(f'{period}MA前日比')
#             # 移動平均の前日比を計算
#             df[f'{period}MA前日比'] = df[f'{period}MA'].pct_change() * 100
#             # 移動平均乖離率を計算（(当日の終値-移動平均値)÷移動平均値）×100
#             df[f'{period}MA乖離率'] = (
#                 df['close'] - df[f'{period}MA']) / df[f'{period}MA'] * 100

#         df_dic[code] = df
