
from time import sleep
from enum import Enum

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.firefox.service import Service as ff_Service
from selenium.webdriver.firefox.options import Options as ff_Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile as ff_Profile
from webdriver_manager.firefox import GeckoDriverManager

from fake_useragent import UserAgent

from common import logger
log = logger.make_logger(__name__)


class Browser(Enum):
    CHROME = 'chrome'
    FIREFOX = 'firefox'


class Selenium:

    def __init__(self):
        self.driver = self._create_driver(Browser.CHROME)


    def _create_driver(self, browser:Browser):

        # fake_useragent
        ua = UserAgent(use_cache_server=True)
        fake_user_agent = ua.random
        log.info(f'user-agent: {fake_user_agent}')

        if browser == Browser.FIREFOX:
            ff_options = ff_Options()
            ff_options.headless = True
            # ff_options.page_load_strategy = 'eager'

            ff_options.add_argument(f'user-agent={fake_user_agent}')
            # ff_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0')

            driver = webdriver.Firefox(
                service=ff_Service(GeckoDriverManager().install()),
                options=ff_options
            )

        else:
            options = Options()
            # options.add_argument("--headless")
            options.add_argument("--incognito")

            # options.add_argument("--disable-popup-blocking")
            # options.add_argument("--no-sandbox")
            # options.add_argument("--disable-gpu")
            # options.add_argument("--disable-dev-shm-usage")
            # options.add_argument("--disable-extensions")
            options.add_argument("--start-maximized")
            # options.add_argument(f'user-agent={fake_user_agent}')
            options.add_argument(
                f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36'
            )
            options.add_argument("--disable-blink-features=AutomationControlled")

            # devtool log option
            options.add_experimental_option("useAutomationExtension", False) 
            # options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
            # options.add_experimental_option('excludeSwitches', ['enable-logging', 'disable-popup-blocking'])
            # options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

            # options.page_load_strategy = 'eager'

            # popup
            options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 1})

            ### 크롬 
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )

            # log.info(f'Selenium Driver Create: browser ==> {browser_name}, type ==> {type(driver)}')

        ## Page load timeout
        driver.set_page_load_timeout(90)

        return driver


    def reset_driver(self, browser:Browser):
        self.driver.quit()
        sleep(5)
        self.driver = self._create_driver(browser)


    def get_driver(self):
        return self.driver


