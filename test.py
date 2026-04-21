from playwright.sync_api import sync_playwright
import pandas as pd
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

"""
Script: Mercado Livre (e-commerce) scraper
Author: guilarde dev
Date: 21/04/2026
Description: extracts informations about mouse in the site Mercado Livre and persists in CSV, XLSX and Google Sheets
"""

"""
CONFIGURATION
"""

#configurating logging
logging.basicConfig(
    level= logging.INFO,
    format= '%(asctime)s - [%(levelname)s] - %(message)s',
    handlers= [
        logging.FileHandler('scrap_mercado_livre.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

#path to acess files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
path_to_creds = os.path.join(BASE_DIR, 'creds.json')

BASE_DIRE = os.path.dirname(os.path.abspath(__file__))
path_to_config = os.path.join(BASE_DIR, 'config.json')

#setup of google sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(path_to_creds, scope)
client = gspread.authorize(creds)
planner = client.open('planner mercado livre').sheet1



class Scraper:
    def __init__(self):
        self.datas = []
        self.browser = None
        self.page = None # self.page will be a page of browser
        self.informations = None #filter of prices

    def open_json(self):
        #open the filter
        with open(path_to_config, 'r', encoding='utf-8') as f:
            self.informations = json.load(f)

    def acess_site(self):
        with sync_playwright() as p:
            while True:
                try:
                    #configuring browser and acessing website
                    self.browser = p.chromium.launch(headless=False)

                    self.page = self.browser.new_page()

                    self.page.goto('https://www.mercadolivre.com.br/')

                    self.page.wait_for_selector('#cb1-edit')
                except

    '''
    DATA EXTRACTION AND DATA CLEANING
    '''
    def take_datas(self):
            # search for the product and wait the site load
            self.page.fill('input[name="as_word"]', 'mouse')
            self.page.press('input[name="as_word"]', 'Enter')
            self.page.wait_for_load_state('networkidle')

            boxes = self.page.locator('.poly-card__content').all()

            #now extract and clean data
            for box in boxes:
                try:
                    title = box.locator('.poly-component__title-wrapper').inner_text()
                    price = box.locator('.andes-money-amount__fraction').first.inner_text()
                    clean_price = float(price.replace('R$', ''))
            
                    product = {
                        'title': title,
                        'price': clean_price
                    }

                    self.datas.append(product)

                except Exception as e:
                    print(f'detected error: {e}')

    try:
        df = pd.DataFrame(self.datas)
        df.to_excel('test1.xlsx', index=False)
        df.to_csv('test1.csv', encoding='utf-8-sig', sep=';', index=False)
    except Exception as e:
        print(f'detected error: {e}')

    browser.close()
