import threading
import unittest
from unittest.mock import MagicMock, PropertyMock, patch

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from src.fintweet_robot.jobs import StocktwitJob, TwitterJob


class TestJobs(unittest.TestCase):

    def test_no_proxy_is_default_retries(self):
        s = StocktwitJob({})
        self.assertEqual(s._retry_limit, 3)

    def test_proxies_is_retries(self):
        p_list = [1, 2]
        rec_p_list = [3, 4, 5]
        s = StocktwitJob({}, p_list, rec_p_list)
        self.assertEqual(s._retry_limit, len(p_list) + len(rec_p_list))

    def test_retry_on_webdriver_exc(self):
        s = StocktwitJob({})
        s._chrome_driver = MagicMock(side_effect=WebDriverException())

        with self.assertLogs(level='ERROR') as log:
            s.run()
            self.assertEqual(len(log.output), 3)

    @patch('selenium.webdriver.Chrome')
    def test_retry_on_exc(self, mock_driver):
        mock_driver.close = MagicMock()

        s = StocktwitJob({})
        s._chrome_driver = MagicMock(return_value=mock_driver)
        s._scrape_method = MagicMock(side_effect=Exception())

        with self.assertLogs(level='ERROR') as log:
            s.run()
            self.assertEqual(len(log.output), 3)

    @patch('threading.Lock')
    @patch('selenium.webdriver.Chrome')
    def test_use_lock_if_provided(self, mock_lock, mock_driver):
        mock_lock.acquire = MagicMock(return_value=True)
        mock_lock.release = MagicMock()

        mock_driver.close = MagicMock()

        s = StocktwitJob({}, lock=mock_lock) 
        s._chrome_driver = MagicMock(return_value=mock_driver)
        s._scrape_method = MagicMock()
        
        s.run()

        mock_lock.acquire.assert_called_once()
        mock_lock.release.assert_called_once()

    @patch('threading.Lock')
    @patch('selenium.webdriver.Chrome')
    def test_dont_use_lock_if_not_provided(self, mock_lock, mock_driver):
        mock_lock.acquire = MagicMock(return_value=True)
        mock_lock.release = MagicMock()

        mock_driver.close = MagicMock()

        s = StocktwitJob({}) 
        s._chrome_driver = MagicMock(return_value=mock_driver)
        s._scrape_method = MagicMock()
        
        s.run()

        mock_lock.acquire.assert_not_called()
        mock_lock.release.assert_not_called()

