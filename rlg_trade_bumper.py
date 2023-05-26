import signal
import sys
import threading
import time

from selenium import webdriver

CHROME_PATH = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
USER_PROFILE_PATH = "C:\\Users\\ahmed\\AppData\\Local\\Google\\Chrome\\User Data"
RLG_USERNAME = 'Momtazzz'

class RLGTradeBumper:
    def __init__(self, trade_count):
        self.trade_count = trade_count
        self.timer = None
        signal.signal(signal.SIGINT, self.stop)

    def run(self):
        self.driver = self.init_driver()
        self.driver.get(f'https://rocket-league.com/player/{RLG_USERNAME}')
        try:
            self.bump_trades()
        except Exception as e:
            print(e)
            self.stop()

    def init_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = CHROME_PATH
        chrome_options.add_argument(f'--user-data-dir={USER_PROFILE_PATH}')
        chrome_options.add_argument("--log-level=3")
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def bump_trades(self):
        handled = set()
        while len(handled) < self.trade_count:
            self.driver.refresh()
            self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            buttons = self.driver.find_elements_by_tag_name('button')
            for button in buttons:
                data_alias = button.get_attribute('data-alias')
                if button.text == 'Bump' and data_alias not in handled:
                    handled.add(data_alias)
                    button.click()
                    break
        print(f"Bumped {len(handled)} trades. Time: {time.ctime()}\n")
        self.driver.refresh()
        self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight/1.2);")
        self.timer = threading.Timer(902, self.bump_trades)
        self.timer.setDaemon(True)
        self.timer.start()

    def stop(self, *args):
        print('Stopping the application...')
        if self.timer:
            self.timer.cancel()
        if self.driver:
            self.driver.quit()
        sys.exit(0)

if __name__ == '__main__':
    bumper = RLGTradeBumper(15)
    bumper.run()
    input("Press enter to exit the application...\n")
    bumper.stop()
