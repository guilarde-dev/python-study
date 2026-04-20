from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto('https://www.mercadolivre.com.br/')

    page.wait_for_selector('#cb1-edit')

    page.fill('input[name="as_word"]', 'mouse logitech')
    page.press('input[name="as_word"]', 'Enter')

    page.wait_for_load_state('networkidle')
    input('')

    browser.close()
