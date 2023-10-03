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
USER_PROFILE_PATH = "C:\\Users\\ahmed\\AppData\\Local\\Google\\Chrome\\User Data" # Change this to your user
RLG_USERNAME = 'Momtazzz' # Change this to your RLG username

class RLGTradeBumper:
    def __init__(self):
        self.state_running = False
        self.driver = None
        signal.signal(signal.SIGINT, self.stop)

    def run(self):
        self.driver = self.init_driver()
        self.main_window_handle = self.driver.current_window_handle
        self.wait = WebDriverWait(self.driver, 1)
        self.start()

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
        while self.state_running:
            try:
                self.switch_to_rlg_page()
                self.driver.refresh()
            except NoSuchWindowException:
                print("The main window has been closed. The application cannot proceed.")
                return
            self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight);")
            bump_after_sec = self.get_wait_seconds_before_bump()
            while bump_after_sec > 0:
                if not self.state_running:
                    return
                time.sleep(1)
                bump_after_sec -= 1
            self.bump_trade()

    def get_wait_seconds_before_bump(self):
        element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'rlg-trade__time')))
        span_element = element.find_element_by_tag_name('span')
        trade_age_text = span_element.text
        wait_for = 0
        if 'hour' in trade_age_text or 'day' in trade_age_text:
            wait_for = 0
        elif 'minute' in trade_age_text:
            match = re.search(r'(\d+) minute', trade_age_text)
            minutes = int(match.group(1))
            wait_for = (15 - minutes) * 60 if minutes < 15 else 0
        elif 'second' in trade_age_text:
            match = re.search(r'(\d+) second', trade_age_text)
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
                button.click()
                break

    def start(self):
        print('Starting the application...')
        self.state_running = True
        self.trade_thread = threading.Thread(target=self.trade_handler)
        self.trade_thread.daemon = True
        self.trade_thread.start()

    def pause(self):
        print('Pausing the application...')
        self.state_running = False
        self.trade_thread.join()

    def stop(self, *args):
        self.pause()
        print('Stopping the application...')
        if self.driver:
            self.driver.quit()
        sys.exit(0)

    def get_state_text(self):
        return 'running' if self.state_running else 'paused'

if __name__ == '__main__':
    bumper = RLGTradeBumper()
    commands = {
        'pause': bumper.pause,
        'start': bumper.start,
        'stop': bumper.stop,
        'state': lambda: print(f"The application is currently {bumper.get_state_text()}.")
    }
    try:
        bumper.run()
    except Exception as e:
        print(type(e))
        print(e)
        bumper.stop()

    while True:
        command = input(f"Enter a command ({', '.join(commands.keys())}) or press Enter to exit:\n").lower().strip("\r\n")
        if command == '':
            bumper.stop()
        elif command in commands:
            commands[command]()
        else:
            print(f"Command '{command}' not supported.")
