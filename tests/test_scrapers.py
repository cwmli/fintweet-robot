import glob
import os
import shutil
import unittest

import chromedriver_autoinstaller
import src.fintweet_robot.scrapers as scrapers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class TestScrapers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup selenium webdriver
        driver_path = chromedriver_autoinstaller.install()
        opts = Options()
        opts.headless = True

        cls.driver = webdriver.Chrome(options=opts, executable_path=driver_path)

        os.makedirs("./tmptests", exist_ok=True)
    
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree("./tmptests")

    def test_stocktwit(self):

        args = {
            "limit": 5, 
            "output": "./tmptests",
            "symbol": "SPY"
        }
        
        scrapers.collect_stocktwit(self.driver, **args)

        output = glob.glob("./tmptests/SPY_*.csv")[0]
        self.assertTrue(os.path.isfile(output))
        with open(output) as o:
            self.assertEqual(o.readline(), "id,time,content\n")

    # def test_twitter(self):

    #     args = {
    #         "limit": 5, 
    #         "output": "./tmptests",
    #         "symbol": "TSLA"
    #     }

    #     scrapers.collect_twitter(self.driver, **args)
