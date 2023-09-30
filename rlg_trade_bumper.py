import re
import signal
import sys
import threading
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

CHROME_PATH = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
USER_PROFILE_PATH = "C:\\Users\\ahmed\\AppData\\Local\\Google\\Chrome\\User Data"
RLG_USERNAME = 'Momtazzz'

class RLGTradeBumper:
    def __init__(self):
        self.driver = None
        signal.signal(signal.SIGINT, self.stop)

    def run(self):
        self.driver = self.init_driver()
        self.main_window_handle = self.driver.current_window_handle
        self.wait = WebDriverWait(self.driver, 1)
        trade_thread = threading.Thread(target=self.trade_handler)
        trade_thread.daemon = True
        trade_thread.start()

    def init_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = CHROME_PATH
        chrome_options.add_argument(f'--user-data-dir={USER_PROFILE_PATH}')
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--start-maximized")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        return driver

    def switch_to_rlg_page(self):
        self.driver.switch_to.window(self.main_window_handle)
        profile_url = f'https://rocket-league.com/player/{RLG_USERNAME}'
        if self.driver.current_url != profile_url:
            self.driver.get(profile_url)

    def trade_handler(self):
        while True:
            try:
                self.switch_to_rlg_page()
                self.driver.refresh()
            except NoSuchWindowException:
                print("The main window has been closed. The application cannot proceed.")
                return
            self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight);")
            bump_after_sec = self.get_wait_seconds_before_bump()
            if bump_after_sec > 0:
                time.sleep(bump_after_sec)
            else:
                self.bump_trade()

    def get_wait_seconds_before_bump(self):
        element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'rlg-trade__time')))
        span_element = element.find_element_by_tag_name('span')
        trade_age_text = span_element.text
        wait_for = 0
        if 'hours' in trade_age_text:
            wait_for = 0
        elif 'minutes' in trade_age_text:
            match = re.search(r'(\d+) minutes', trade_age_text)
            minutes = int(match.group(1))
            wait_for = (15 - minutes) * 60 if minutes < 15 else 0
        elif 'seconds' in trade_age_text:
            match = re.search(r'(\d+) seconds', trade_age_text)
            seconds = int(match.group(1))
            wait_for = 900 - seconds
        else:
            wait_for = 900
        print(f"[{time.ctime()}] Oldest trade has been bumped {trade_age_text}. Waiting for {wait_for} seconds before bumping...")
        return wait_for

    def bump_trade(self):
        buttons = self.driver.find_elements_by_tag_name('button')
        for button in buttons:
            if button.text == 'Bump':
                print(f"Bumping the trade with data alias {button.get_attribute('data-alias')}.")
                # button.click()
                break

    def stop(self, *args):
        print('Stopping the application...')
        if self.driver:
            self.driver.quit()
        sys.exit(0)

if __name__ == '__main__':
    bumper = RLGTradeBumper()
    try:
        bumper.run()
    except Exception as e:
        print(type(e))
        print(e)
    finally:
        input("Press enter to exit the application...\n")
        bumper.stop()
