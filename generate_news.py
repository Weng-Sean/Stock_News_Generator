import os
import requests
from bs4 import BeautifulSoup as bs
import pickle
import regex as re
from tqdm import tqdm
import nltk
import datetime
from datetime import datetime as dt
from os.path import *
# nltk.download('stopwords')
# from nltk.corpus import stopwords
from stock_tools import *


current_path = os.getcwd()

# returns an url to google news page with specified query
def get_google_news_url(query):
    return f"https://www.google.com/search?q={query}&rlz=1C1RXQR_enUS994US994&source=lnms&tbm=nws&sa=X&ved=" \
           f"2ahUKEwj1tYzKx7_2AhUdl4kEHQvMB-EQ_AUoAXoECAMQAw&biw=1280&bih=601&dpr=1.5"

# returns news articles in google news page with specified query
def get_news_url_list(query):
    if type(query) != list:
        url = get_google_news_url(query)
        html_content = requests.get(url,headers=get_headers()).content
        soup = bs(html_content, features="html.parser")

        news_urls = []
        existed_urls = {}

        for link in soup.find_all("a"):
            link_str = str(link)
            if re.match(".*url=https://.*ved=.*", link_str):
                l = link_str.split("url=")[1].split("&amp")[0]
                if "google" not in l and l not in existed_urls:
                    existed_urls[l] = True
                    news_urls.append(l)

    else:
        news_urls = []
        existed_urls = {}

        for q in query:
            url = get_google_news_url(q)
            html_content = requests.get(url, headers=get_headers()).content
            soup = bs(html_content, features="html.parser")

            for link in soup.find_all("a"):
                link_str = str(link)
                if re.match(".*url=https://.*ved=.*", link_str):
                    l = link_str.split("url=")[1].split("&amp")[0]
                    if "google" not in l and l not in existed_urls:
                        existed_urls[l] = True
                        news_urls.append(l)

    return news_urls



# clean javascript code in html in case being considered to be a paragraph
def clean_html(html):

    # First we remove inline JavaScript/CSS:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
    # Then we remove html comments. This has to be done before removing regular
    # tags since comments can contain '>' characters.
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)

    return cleaned.strip()


# generate a data folder contains all articles being stores as txt files in the folder
# input fdr_name -> the name of the data folder being created (default is query)
# input fdr_path -> the path you want to save the folder (default is current path address)
# ouput dictionary -> return a dictionary which key is the article number (int) and value is the article text string (str)

def generate_data_folder(ticker, fdr_name=None, fdr_path=current_path):
    try:
        company = get_company_from_ticker(ticker)
        query = [ticker + " stock", company, company + " stock"]
    except:
        print("FAILED TO CONVERT TICKER TO COMPANY")
        query = ticker + " stock"
    if not fdr_name:
        fdr_name = ticker
    full_path = join(fdr_path, fdr_name)

    urls = get_news_url_list(query)
    if not exists(full_path):
        os.mkdir(full_path)
    count = 1


    for u in urls:
        if "nasdaq" in u:
            continue
        print(f"Processing {u}")
        try:
            text = requests.get(u, headers=get_headers(), timeout=15).text
        except Exception as e:
            print(e)
            continue
        tags = bs(clean_html(text), features="html.parser").find_all(re.compile("p"))

        article_txt = ""
        for tag in tags:
            para_text = tag.get_text()
            if len(para_text.split()) > 20:
                article_txt += para_text


        if len(article_txt.split()) > 200:

            # break article_txt from one long line to several lines for reading in txt file
            char_per_line = 100
            formatted_txt = ""
            line = ""
            for wrd in article_txt.split():
                if len(line) + len(wrd) < char_per_line:
                    line += " " + wrd
                else:
                    formatted_txt += line + "\n"
                    line = ""

            with open(join(full_path, f"article#{count}.txt"), "w", encoding="utf-8") as f:
                f.write(formatted_txt)
            count += 1

    # try:
    #     with open(join(full_path, "article_time.txt"), "w") as f:
    #         f.write(get_df_bs(ticker)["Date"].to_list()[-1])
    # except Exception as e:
    #     print(e)

if __name__ == "__main__":
    recent_trading_date = get_dataframe("SPY")["Date"].to_list()[-1]
    DATA_FDR_PATH = join(current_path, "Data", recent_trading_date)
    if not exists(DATA_FDR_PATH):
        os.mkdir(DATA_FDR_PATH)

    for tk in tqdm(get_500_tickers()):
        output_dic = generate_data_folder(tk, fdr_name=tk, fdr_path=DATA_FDR_PATH)

