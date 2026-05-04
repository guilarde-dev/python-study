import requests
from bs4 import BeautifulSoup
from time import sleep
import logging
import json
import os

acess_token = 'token'
search_query = 'mouse'

logging.basicConfig(
    level= logging.INFO,
    format= '%(asctime)s - [%(levelname)s] - %(message)s',
    handlers= [
        logging.FileHandler('scrap_mercado_livre.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
path_to_config = os.path.join(BASE_DIR, 'config.json')

class Scraper():
    def __init__(self):
        self.datas = []
        self.url = None

    def open_json(self):
        with open(path_to_config, 'r', encoding='utf-8') as f:
            self.information = json.load(f)
            self.products_name = self.information['product_name']

    def search_product(self):
        self.url = f"https://api.mercadolibre.com/sites/MLB/search?q={self.products_name}"
        headers = {'authorization': f'Bearer {acess_token}'}

        while True:
            try:
                response = requests.get(self.url, headers=headers)
                logging.info('starting extraction')
                break
            except Exception as e:
                logging.critical('error in acess site, trying again in 10 seconds')
                sleep(10)
                continue
        
        if response == 200:
            return response.json()['results']
        else:
            logging.error(f'error in request the HTML. {response.status_code}')
            return []
        
    def take_datas(self):
