"""
import selenium

class Scraper:
    def __init__(self):
        pass
""""    
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException
import requests
import pandas as pd
import numpy as np
import time

options = Options()
options.headless = True
#For Linux
#driver = webdriver.Chrome('/usr/bin/chromedriver',options=options)
path = "/usr/local/bin/chromedriver"

def seed(ticker):
    return f'https://etfdb.com/etf/{ticker}/#holdings'

def get_holdings(ticker):
    driver = webdriver.Chrome(path)
    link = seed(ticker)
    get_succeed = False
    driver.get(link)
    time.sleep(2)
    bs = BeautifulSoup(driver.page_source,'html.parser')
    try:
        table = bs.find('table', attrs={'id':'etf-holdings'})
        table_rows = table.find_all('tr')
    except:
        print(f'############ Fail to retrieve data ############')
        print(f'############ {ticker} Passed ############')
        return
    l = []
    for tr in table_rows[1:-1]:
        sym = tr.find('td', attrs={'data-th':'Symbol'})
        pct = tr.find('td', attrs={'data-th':'% Assets'})
        row = [sym.text,pct.text]
        l.append(row)
    df = pd.DataFrame(l,columns=['ticker','percentage'])
    driver.close()
    return df

tick_list = []
for tick in tick_list:
    temp = get_holdings(tick)
    exec(f'temp.to_pickle("{tick}_holdings.pkl","gzip")')
