import threading
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def init_driver():
    chrome_path = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
    user_profile_path = "C:\\Users\\ahmed\\AppData\\Local\\Google\\Chrome\\User Data"

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = chrome_path
    chrome_options.add_argument(f'--user-data-dir={user_profile_path}')

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def bump_trades(driver, trade_count):
    handled = set()
    while len(handled) < trade_count:
        driver.refresh()
        driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        buttons = driver.find_elements_by_tag_name('button')
        for button in buttons:
            data_alias = button.get_attribute('data-alias')
            if button.text == 'Bump' and data_alias not in handled:
                handled.add(data_alias)
                button.click()
                break
    print(f"Bumped {trade_count} trades. Time: {time.ctime()}\n")
    driver.refresh()
    driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight/1.2);")
    threading.Timer(905, bump_trades, [driver, trade_count]).start()


if __name__ == '__main__':
    driver = init_driver()
    driver.get('https://rocket-league.com/player/Momtazzz')
    try:
        bump_trades(driver, 15)
    except:
        pass
    driver.quit()
