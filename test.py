from playwright.sync_api import sync_playwright
import json
import os
import logging
from time import sleep

"""
Script: Mercado Livre (e-commerce) scraper
Author: guilarde dev
Date: 21/04/2026
Description: extracts informations about mouse in the site Mercado Livre and persists in CSV, XLSX and Google Sheets
"""

# Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler('scrap_mercado_livre.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class Scraper:
    def __init__(self):
        self.datas = []
        self.browser = None
        self.page = None
        self.informations = None
        self.path_to_config = os.path.join(os.path.dirname(__file__), 'config.json')

    def open_json(self):
        # Open the filter
        if os.path.exists(self.path_to_config):
            with open(self.path_to_config, 'r', encoding='utf-8') as f:
                self.informations = json.load(f)
        else:
            logging.critical('Error opening the file JSON, check if the file exists')

    def run(self):
        with sync_playwright() as p:
            # Configuring browser and accessing website
            self.browser = p.chromium.launch(headless=False)
            self.page = self.browser.new_page()

            try:
                self.page.goto('https://www.mercadolivre.com.br/')
                self.page.wait_for_selector('#cb1-edit')
                
                # Search for the product and wait the site load
                self.page.fill('input[name="as_word"]', 'mouse')
                self.page.press('input[name="as_word"]', 'Enter')
                self.page.wait_for_load_state('networkidle')

                # Pagination loop
                for item in range(200):
                    boxes = self.page.locator('.poly-card__content').all()

                    if not boxes: # Boxes are the products, if the site doesn't have more products, the bot finishes
                        logging.info('Pages finished')
                        break

                    # Now extract and clean data
                    for box in boxes:
                        try:
                            title = box.locator('.poly-component__title-wrapper').inner_text()
                            price = box.locator('.andes-money-amount__fraction').first.inner_text()
                            brand = box.locator('.poly-component__seller').first.inner_text()
                            
                            # Data cleaning
                            clean_price = float(price.replace('.', ''))
                            link = box.locator('a').first.get_attribute("href")

                            # Saving in a dictionary and add in the list
                            product = {
                                'title': title,
                                'price': clean_price,
                                'brand': brand,
                                'link': link
                            }
                            self.datas.append(product)

                        except Exception:
                            logging.error('Error in data extraction, continuing process')
                            continue

                    # Attempt to click next button
                    try:
                        next_button = self.page.locator('a[title="Seguinte"]')
                        if next_button.is_visible():
                            next_button.click()
                            self.page.wait_for_load_state('networkidle')
                        else:
                            logging.info('Button didn´t find, end of the pages')
                            break
                    except Exception:
                        logging.info('Error navigating to next page, ending process')
                        break

            except Exception as e:
                logging.critical(f'Detected error in search product: {e}')

            self.browser.close()
            self.save_datas()

    def save_datas(self):
        logging.info("Process finished. Saving data...")
        # Save logic goes here

if __name__ == "__main__":
    bot = Scraper()
    bot.open_json()
    bot.run()
