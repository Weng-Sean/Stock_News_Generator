# This file adds result (label) to previous gathered news
import datetime
from datetime import datetime as dt
import os
from os.path import *
import requests
import pandas as pd
from io import StringIO
from tqdm import tqdm
import time
from bs4 import BeautifulSoup as bs
from stock_tools import *


# input a date string and period returns a date string on specified future period
def get_trading_day(date_str, period):
    d = date_str.split("-")
    date_obj = dt(year=int(d[0]), month=int(d[1]), day=int(d[2]))
    for _ in range(period):
        date_obj += datetime.timedelta(days=1)
        while date_obj.isoweekday() > 5:
            date_obj += datetime.timedelta(days=1)
    return date_obj.strftime("%Y-%m-%d")


# calculate difference b/w expected return and actual return
def get_score(stock_df, market_df, article_time_stamp, period, beta):
    past_price = stock_df[stock_df.Date == article_time_stamp]["Close"].to_list()[0]
    past_price_market = market_df[market_df.Date == article_time_stamp]["Close"].to_list()[0]
    future_price = stock_df[stock_df.Date == get_trading_day(article_time_stamp, period)]["Close"].to_list()[0]
    future_price_market = market_df[market_df.Date == get_trading_day(article_time_stamp, period)]["Close"].to_list()[0]

    stock_return = (future_price - past_price) / past_price
    market_return = (future_price_market - past_price_market) / past_price_market

    expected_return = market_return * beta

    return stock_return - expected_return

# add a file names period_day_change.txt (where period is a parameter) and records percentage changed divided by its beta during the period
def add_result(DATA_PATH, date_str):

    FDR_PATH = join(DATA_PATH, date_str)
    # list all the directories in FDR_PATH
    fdrs = os.listdir(FDR_PATH)

    market_return_df = get_dataframe("SPY")

    for f in tqdm(fdrs):
        print(f)
        if "." in f:
            continue
        if f == "DISCA":
            continue

        FINISHED = False
        while not FINISHED:
            try:
                df = get_dataframe(f)
                time.sleep(1)
                beta = get_stock_beta(f)
                FINISHED = True

            except Exception as e:
                print(e)
                time.sleep(10)

        for period in [1,2,3,7]:
            score = get_score(df, market_return_df, date_str, period, beta)
            try:
                with open(join(FDR_PATH, f, f"{period}_day_score.txt"), "w") as file:
                    file.write(str(score))
            except Exception as e:
                print(e)

            time.sleep(1)

date = "2022-04-05"
add_result(join(os.getcwd(), "Data"), date)
