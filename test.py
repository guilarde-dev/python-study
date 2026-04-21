from playwright.sync_api import sync_playwright
import pandas as pd
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
from requests.exceptions import ConnectionError, HTTPError
from time import sleep
from datetime import datetime

"""
Script: Mercado Livre (e-commerce) scraper
Author: guilarde dev
Date: 21/04/2026
Description: extracts informations about mouse in the site Mercado Livre and persists in CSV, XLSX and Google Sheets
"""

"""
CONFIGURATION
"""

try:
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
    logging.info('setup concluded with successfully.')
except Exception as e:
    logging.critical('error in setup and configuration. check the paths to files or if the planner exists in google sheets')
    #error handling with setup, remember of share the planner with the service account in google sheets


class Scraper:
    def __init__(self):
        self.datas = []
        self.browser = None
        self.page = None # self.page will be a page of browser
        self.informations = None #filter of prices

    def open_json(self):
        #open the filter
        if path_to_config:
            with open(path_to_config, 'r', encoding='utf-8') as f:
                self.informations = json.load(f)
        else:
            logging.critical('error opening the file JSON, check if the file exists') #error handling with config.json

    '''
    ACESSING SITE
    '''
    def acess_site(self):
        with sync_playwright() as p:
            while True:
                try:
                    #configuring browser and acessing website
                    self.browser = p.chromium.launch(headless=False)
                    self.page = self.browser.new_page()

                    self.page.goto('https://www.mercadolivre.com.br/')
                    self.page.wait_for_selector('#cb1-edit')
                    
                    break
                except (ConnectionError, HTTPError) as e:
                    logging.error(f'error in acess site, check your internet or URL of the site, trying again in 5 seconds. error : {e}') #error handling for bad connection of internet or change in URL
                    sleep(5)
                    continue
    '''
    DATA EXTRACTION AND DATA CLEANING
    '''
    def take_datas(self):
            while True:
                try:
                    # search for the product and wait the site load
                    self.page.fill('input[name="as_word"]', 'mouse')
                    self.page.press('input[name="as_word"]', 'Enter')
                    self.page.wait_for_load_state('networkidle')

                    break
                    
                    
                except Exception as e:
                    logging.critical('detected error in search product, trying again in 10 seconds.')
                    sleep(10)
                    continue

            for item in range(200):
                    boxes = self.page.locator('.poly-card__content').all()

                    if not boxes: #boxes are the products, if the site doesn´t have more products, the bot finish
                        logging.info('pages finished')
                        break
                    

                    #now extract and clean data
                    for box in boxes:
                        title, price, brand, rating = 'N/A', 'N/A', 'N/A', 'N/A'
                        try:
                            title = box.locator('.poly-component__title-wrapper').inner_text() if title else 'N/A'
                            price = box.locator('.andes-money-amount__fraction').first.inner_text() if price else 'N/A'
                            brand = box.locator('.poly-component__seller').first.inner_text() if brand else 'N/A'
                            rating = box.locator('.poly-component__review-compacted').first.inner_text() if rating else 'N/A'
                            clean_price = float(price.replace('R$', '')) if price else 'N/A'
                            link = self.page.locator("a.product-title").get_attribute("href") if link else 'N/A'

                        except Exception as e:
                            logging.error('error in datas, continuing process') #error handling if there's an error in take datas
                            continue
                            
                        try: #saving in a dictionary and add in the list
                            product = {
                                'title': title,
                                'price': clean_price,
                                'brand': brand,
                                'rating': rating,
                                'link': link
                            }

                            self.datas.append(product)
                        
                        except Exception as e:
                            logging.error('error in save data in a dictionary, continuing process') #error handling with save data in dictionary
                            continue

                    try:
                        self.page.get_by_role("button", name="Nome do Botão").click()
                    except Exception as e:
                        logging.info('button didn´t find, end of the pages')
                        break

                        

            self.browser.close()
