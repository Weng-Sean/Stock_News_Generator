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
import re
import random

user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]

def get_headers():
    return {'User-Agent': random.choice(user_agent_list)}

def get_company_from_ticker(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}?p=TSLA&.tsrc=fin-srch"
    result = requests.get(url, headers=get_headers()).content
    company_str = bs(result, features="html.parser").find("h1", attrs={"class":"D(ib) Fz(18px)"}).get_text()
    pattern = re.compile("\(.*\)")
    company = pattern.split(company_str)[0]

    return company

# return a panda dataframe contains yahoo finance stock data
def get_df_bs(ticker, anaysis_period=365):
    try:
        current_epoch = 3000000000
        past_epoch = int((dt.now() - datetime.timedelta(anaysis_period)).timestamp())
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={past_epoch}&period2={current_epoch}&interval=1d&events=history&includeAdjustedClose=true"
        content = StringIO(requests.get(url, headers=get_headers()).text)
        df = pd.read_csv(content)
        return df

    except Exception as e:
        print(e)
        if "C error" in str(e):
            print("DF START")
            time.sleep(5)
            df = get_dataframe(ticker, anaysis_period)
            return df



def get_dataframe(ticker, anaysis_period=365):
    try:
        # A huge epoch that allows most up to date info
        current_epoch = 3000000000
        past_epoch = int((dt.now() - datetime.timedelta(anaysis_period)).timestamp())
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={past_epoch}&period2={current_epoch}&interval=1d&events=history&includeAdjustedClose=true"
        df = pd.read_csv(url)
        return df

    except Exception as e:
        if "401" in str(e):
            print("BS START")
            time.sleep(5)
            df = get_df_bs(ticker, anaysis_period)
            return df


def get_stock_beta(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}?p={ticker}&.tsrc=fin-srch"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    beta = bs(requests.get(url, headers=get_headers()).text, features="html.parser").find("td", attrs={"data-test":"BETA_5Y-value"}).get_text()
    try:
        return float(beta)
    except:
        return 1

def get_500_tickers():
    content = requests.get("https://en.wikipedia.org/wiki/List_of_S&P_500_companies").content
    soup = bs(content, features="html.parser").find("table", id="constituents")
    tickers_soup = soup.find_all("a", attrs = {"class":"external text", "rel":"nofollow"})
    tickers = [s.text for s in tickers_soup if "reports" not in s.text]
    return tickers

