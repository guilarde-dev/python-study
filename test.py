from playwright.sync_api import sync_playwright
import pandas as pd

datas = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto('https://www.mercadolivre.com.br/')

    page.wait_for_selector('#cb1-edit')

    page.fill('input[name="as_word"]', 'mouse logitech')
    page.press('input[name="as_word"]', 'Enter')

    page.wait_for_load_state('networkidle')
    boxes = page.locator('.poly-card__content').all()

    for box in boxes:
        try:
            title = box.locator('.poly-component__title-wrapper').inner_text()
            price = box.locator('.andes-money-amount__fraction').first.inner_text()
            clean_price = float(price.replace('R$', ''))
            
            product = {
                'title': title,
                'price': clean_price
            }

            datas.append(product)

        except Exception as e:
            print(f'detected error: {e}')

    try:
        df = pd.DataFrame(datas)
        df.to_excel('test1.xlsx', index=False)
        df.to_csv('test1.csv', encoding='utf-8-sig', sep=';', index=False)
    except Exception as e:
        print(f'detected error: {e}')

    browser.close()
