# BUILT-IN LIBS
import os
import sys
import zipfile
import datetime
from time import sleep
from random import choice
from datetime import timedelta

# AUTOMATION
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains

# UNDETECTED AUTOMATION
import undetected_chromedriver as uc

# ERRORS
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchWindowException, WebDriverException, StaleElementReferenceException, \
    UnexpectedAlertPresentException, NoAlertPresentException

# LOCAL
from loader import *
try:
    from .add_proxy import set_authenticated_proxy_through_plugin
    from .utils import *
except ImportError:
    from add_proxy import set_authenticated_proxy_through_plugin
    from utils import *

WIN32_BASE_PATH = 'drivers/win32'


class Base:
    def __init__(self, homepage, proxy, driver_type='base'):
        # MAIN VARS
        self.status = None
        self.url = homepage

        # SELENIUM SETTINGS
        cdriver_path = ''
        if 'win' in sys.platform.lower():
            cdriver_path = WIN32_BASE_PATH + 'chromedriver.exe'
        self.opt = uc.ChromeOptions()
        self.opt.add_argument('--mute-audio')
        self.opt.add_argument('--disable-infobars')
        self.opt.add_argument('--disable-notifications')
        self.opt.add_argument('--disable-dev-shm-usage')
        self.opt.add_argument('--no-sandbox')
        self.opt.add_argument('--no-first-run --no-service-autorun --password-store=basic')
        self.opt.add_argument("--lang=en")
        self.caps = webdriver.DesiredCapabilities.CHROME
        self.caps['acceptSslCerts'] = True

        # Add proxies
        if proxy:
            proxy_file = set_authenticated_proxy_through_plugin(proxy)
            with zipfile.ZipFile(proxy_file, 'r') as zip_obj:
                zip_obj.extractall(f'{proxy_file.replace(".zip", "")}')
                zip_obj.close()
            self.opt.add_argument(f'--load-extension={os.getcwd()}/{proxy_file.replace(".zip", "")}')
            try:
                os.remove(proxy_file)
            except FileNotFoundError:
                pass

        # START NAVIGATOR
        self.driver = uc.Chrome(options=self.opt, desired_capabilities=self.caps)
        self.driver.implicitly_wait(10)
        self.wait = lambda x: WebDriverWait(self.driver, x)
        self.driver.maximize_window()
        self.rs = lambda: sleep(choice([x / 100 for x in range(3 * 100)]))  # Random time of sleep. rs = random sleep.
        self.chain = ActionChains(self.driver)

    def wait_until_profile_loads(self, tries: int = 3, delay: int = 1, text: str = 'profile.php'):
        # First of all, this function needed to search elements from the navigation bar in Twitter.
        # But it is also useful in FaceBook.
        for _ in range(tries):
            if text in self.driver.current_url:
                return
            sleep(delay)

    def scroll_down_by_hands(self, direction: str = 'Down', timeout: int = 10):
        self.chain.reset_actions()
        if direction == 'Down':
            self.chain.key_down(Keys.ARROW_DOWN)
            sleep(timeout)
            self.chain.key_up(Keys.ARROW_DOWN)
        else:
            self.chain.key_up(Keys.ARROW_UP)
            sleep(timeout)
            self.chain.key_up(Keys.ARROW_UP)

    def open_homepage(self):
        self.driver.get(self.url)

    def scroll_to_the_end(self):
        self.driver.execute_script(f'window.scrollTo(0, document.body.scrollHeight);')

    def scroll_to(self, x=0, y=0):
        self.driver.execute_script(f'window.scrollTo({x}, {y});')

    def scroll_by(self, x=0, y=0):
        self.driver.execute_script(f'window.scrollBy({x}, {y});')

    def scroll_into_view(self, element=None):
        self.driver.execute_script("arguments[0].scrollIntoView();", element)

    def move_and_click(self, element, text=None, y=0, to_click=True):
        # Simple way to click on the element 'by hands'.
        # Needs to make our actions more 'human'.
        self.chain.reset_actions()  # Reset ActionChains' moves from both sides just in case.
        self.chain.move_to_element(element)
        if y:
            self.scroll_by(y=y)
        if to_click:
            self.chain.click()
        if text:
            self.chain.send_keys(text)
        self.chain.perform()
        self.chain.reset_actions()


if __name__ == '__main__':
    pass
