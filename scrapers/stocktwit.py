import csv
import logging
import os
import random
import re
import time
from datetime import datetime, timedelta, timezone
from urllib import parse

import pytz
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

STOCKTWIT_ENDPOINT = "http://stocktwits.com/symbol/{symbol}"
FIELDNAMES = ["id", "time", "content"]

MMDDYY_RE = re.compile(r"([1-9]+\/[0-9]+\/[1-9]{2}), ([0-9]{2}:[0-9]{2}) (AM|PM)")
MINUTE_RE = re.compile(r"[0-9]+m")
TIME_RE = re.compile(r"([0-9]{2}:[0-9]{2}) (AM|PM)")

logger = logging.getLogger(__name__)

def collect_tweets(driver, output, symbol, limit, delay=0.25, **_):
    """
    collect tweets from current time until time _limit_ is reached

    :param driver: web driver
    :param symbol: stock symbol
    :param limit: content of tweets to collect until (in minutes)
    :param delay: delay to wait until scrolling
    """

    logger.info("Loading webpage...")
    driver.get(STOCKTWIT_ENDPOINT.format(symbol=symbol))
    logger.info("Loaded...")

    try:
        driver.find_element_by_class_name("infinite-scroll-component")
    except NoSuchElementException as e:
        raise Exception("Unexpected page for {}".format(symbol))

    # Retrieve proxy's local timezone
    # In the case of proxies, the timezone can be different and thus our limit will not be applicable
    tz = driver.execute_script("return Intl.DateTimeFormat().resolvedOptions().timeZone")
    tz_browser = pytz.timezone(tz)
    browser_date = datetime.now(tz=tz_browser)
    logger.info("timezone detected: {zone}, local time is {time}".format(zone=tz, time=browser_date.isoformat()))

    # We want to save in EST
    tz_save = pytz.timezone("America/Toronto")

    try:
        os.makedirs(output, exist_ok=True)
        output = open("{output}/{symbol}_{date}_{limit}.csv".format(output=output, symbol=symbol, date=browser_date.astimezone(tz_save), limit=limit), "w")
        writer = csv.DictWriter(output, FIELDNAMES)
        writer.writeheader()

    except OSError as e:
        logger.error("Could not open output file for writing: %s" % e)
        return

    logger.debug("Collecting tweet information related to {symbol} after {date}".format(symbol=symbol, date=browser_date.isoformat()))

    seen_tweets = 0
    fetch = True
    while fetch:
        timeline = driver.find_element_by_class_name("infinite-scroll-component")
        tweets = timeline.find_elements_by_xpath("//div/div/div/article")

        for tweet in tweets:
            try:
                core = tweet.find_element_by_xpath(".//div/div[2]")
                t_time = core.find_element_by_xpath(".//div/a").text
                content = core.find_element_by_xpath(".//div[2]").text
                height = tweet.size['height']

                # Try to delete nodes to lighten element rendering
                try:
                    driver.execute_script("""
                    var element = arguments[0];
                    element.parentNode.removeChild(element);
                    """, tweet.find_element_by_xpath('./../../..'))
                except StaleElementReferenceException:
                    logger.error("Could not delete tweet node")
                    pass

                if t_time == "now":
                    t_date = browser_date
                elif m := MMDDYY_RE.match(t_time):
                    mdy = m.group(1).split("/")
                    hm = m.group(2).split(":")
                    i = m.group(3)

                    hm[0] = int(hm[0])
                    if (i == "PM"):
                        if hm[0] < 12:
                            hm[0] = (int(hm[0]) + 12) % 24
                    else:
                        hm[0] = 0 if hm[0] == 12 else hm[0]
                        
                    t_date = datetime(int("20" + mdy[2]), int(mdy[0]), int(mdy[1]), 
                        hm[0], int(hm[1]), tzinfo=tz_browser)
                elif m := TIME_RE.match(t_time):
                    hm = m.group(1).split(":")
                    i = m.group(2)

                    hm[0] = int(hm[0])
                    if (i == "PM"):
                        if hm[0] < 12:
                            hm[0] = (int(hm[0]) + 12) % 24
                    else:
                        hm[0] = 0 if hm[0] == 12 else hm[0]

                    t_date = browser_date.replace(hour = int(hm[0]), minute = int(hm[1]))
                elif m:= MINUTE_RE.match(t_time):
                    min_ago = m.group(0)[:-1]
                    t_date = browser_date - timedelta(minutes = int(min_ago))
                else:
                    fetch = False
                    logger.info("Could not retrieve timestamp: {time}".format(time=t_time))
                    continue

                logger.info("Found tweet {num} at {time}".format(num=seen_tweets, time=t_date))

                # Stop
                if (browser_date - t_date > timedelta(minutes=limit)):
                    fetch = False
                    logger.info("Tweet time limit exceeded")
                    break
                
                # Convert timezone to EST before writing
                writer.writerow({"id": seen_tweets, "time": t_date.astimezone(tz_save).isoformat(), "content": content})

                logger.debug("Scrolling by {num}".format(num=height))

                time.sleep(random.uniform(0, delay))
                driver.execute_script("window.scrollBy(0, {y})".format(y=height))

            except Exception:
                logger.exception("Could not parse tweet, skipping...")

            seen_tweets += 1

    output.close()
