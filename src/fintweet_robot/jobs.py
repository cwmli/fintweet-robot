import concurrent.futures
import datetime
import logging
import random
from abc import ABC, abstractmethod

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options

from . import scrapers


class ScrapeJob(ABC):
    """
    Abstract class ScrapeJob for defining further jobs based on _scrape_method; shuffles proxies

    :param scrape_options: dictionary containing options to pass to _scrape_method
    :param proxy_list: list of proxies to shuffle from
    :param rec_plist: recommended proxies to first shuffle from
    :param lock: lock for multithreaded or multiprocessed use case; used during webdriver init
    :param headless: headless mode
    """

    def __init__(self, scrape_options, proxy_list = [], rec_plist = [], lock = None, headless = True):
        random.seed(datetime.datetime.now())

        self._webdriver_lock = lock
        self._headless = headless

        self._logger = logging.getLogger(__name__)

        self._plist = proxy_list
        self._rec_plist = rec_plist

        self._n_plist = len(self._plist)
        self._n_rec_plist = len(self._rec_plist)

        self._use_proxies = self._n_plist + self._n_rec_plist > 0

        if self._use_proxies:
            self._retry_limit = self._n_plist + self._n_rec_plist
        else:
            # Default to 3 retries without proxies
            self._retry_limit = 3

        self._v_plist = []

        self._scrape_options = scrape_options

        random.shuffle(self._rec_plist)
        random.shuffle(self._plist)


    def run(self):
        retries = 0
        done = False
        while retries < self._retry_limit and not done:
            try:

                if self._use_proxies:
                    if retries > self._n_rec_plist - 1:
                        proxy = self._plist[retries - self._n_rec_plist]
                    else:
                        proxy = self._rec_plist[retries]
                    self._logger.info("Using proxy: %s for %s" % (proxy, self._scrape_options["symbol"]))
                else:
                    proxy = None

                self._try_lock()

                t = self._chrome_driver(self._headless, proxy=proxy)

                self._try_unlock()

                self._scrape_method(t, self._scrape_options)
                done = True

                self._v_plist.append(proxy)

                t.close()
                break
            except WebDriverException as e:
                self._logger.exception(str(e), exc_info=None, stack_info=False)
                retries += 1
            except Exception as e:
                self._logger.exception(str(e), exc_info=None, stack_info=False)
                t.close()
                retries += 1

        return self._v_plist

    @abstractmethod
    def _scrape_method(self, driver, kwargs):
        pass

    def _try_lock(self):
        if self._webdriver_lock:
            self._webdriver_lock.acquire()

    def _try_unlock(self):
        if self._webdriver_lock:
            self._webdriver_lock.release()

    def _chrome_driver(self, headless=True, proxy=None, timeout=30):

        driver_path = chromedriver_autoinstaller.install()
        opts = Options()

        if proxy:
            opts.add_argument('--proxy-server=%s' % proxy)

        if headless:
            opts.add_argument('--user-data-dir=/tmp/user-data')
            opts.add_argument('--hide-scrollbars')
            opts.add_argument('--enable-logging')
            opts.add_argument('--v=99')
            opts.add_argument('--single-process')
            opts.add_argument('--data-path=/tmp/data-path')
            opts.add_argument('--ignore-certificate-errors')
            opts.add_argument('--homedir=/tmp')
            opts.add_argument('--disk-cache-dir=/tmp/cache-dir')
            opts.add_argument('--disable-gpu')
            opts.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36')
            opts.headless = True

        opts.add_argument('log-level=3')

        driver = webdriver.Chrome(options=opts, executable_path=driver_path)
        driver.set_page_load_timeout(timeout)

        return driver

class StocktwitJob(ScrapeJob):

    def _scrape_method(self, driver, kwargs):
        scrapers.collect_stocktwit(driver, **kwargs)

class TwitterJob(ScrapeJob):

    def _scrape_method(self, driver, kwargs):
        scrapers.collect_twitter(driver, **kwargs)
