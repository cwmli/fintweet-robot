import csv
import logging
import os
import random
import time
from datetime import datetime, timedelta, timezone
from urllib import parse

import pytz
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException

SEARCH_ENDPOINT = "https://twitter.com/search?"
FIELDNAMES = ["id", "time", "content"]
TWEET_TIMEOUT = 30

logger = logging.getLogger(__name__)

def collect_tweets(driver, output, symbol, limit, until_date=None, **_):
    """
    collect tweets from _date_ until time _limit_ is reached

    :param driver: web driver
    :param symbol: stock symbol
    :param limit: content of tweets to collect until (in minutes)
    :param until_date: date to scrape until
    """

    extra_args = ""
    if until_date:
        extra_args = "until:{}".format(until_date.strftime("%Y-%m-%d"))

    twitter_str = "${symbol} lang:en -filter:links -filter:replies {extra_args}".format(symbol=symbol, extra_args=extra_args)
    url = SEARCH_ENDPOINT + parse.urlencode({"q": twitter_str}) + "&src=typed_query&f=live&vertical=default"

    logger.info("Loading webpage...")
    driver.get(url)
    logger.info("Loaded...")

    tz_save = pytz.timezone("America/Toronto")
    ndate = datetime.now(timezone.utc) if not until_date else until_date

    try:
        os.makedirs(output, exist_ok=True)
        output = open("{output}/{symbol}_{date}_{limit}.csv".format(output=output, symbol=symbol, date=ndate.astimezone(tz_save), limit=limit), "w")
        writer = csv.DictWriter(output, FIELDNAMES)
        writer.writeheader()

    except OSError as e:
        logger.error("Could not open output file for writing: %s" % e)
        return

    logger.info("Collecting tweet information related to {symbol} after {date}".format(symbol=symbol, date=datetime.now().isoformat()))

    seen = []
    fetch = True
    dirty = True
    retries = 0
    while fetch:
        tweets = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
        for tweet in tweets:

            try:
                height = tweet.find_element_by_xpath('./../../../../../..').size['height']
                username = tweet.find_element_by_xpath('.//span').text
                handle = tweet.find_element_by_xpath('.//span[contains(text(), "@")]').text
                t_time = tweet.find_element_by_xpath('.//time').get_attribute('datetime')
                content = tweet.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
            except StaleElementReferenceException:
                if height:
                    driver.execute_script("window.scrollBy(0, {y})".format(y=height))
                    time.sleep(random.uniform(0.25, 0.5))
                continue

            id = ''.join([username, handle, t_time])
            if (id in seen):
                dirty = False
                continue
            else:
                dirty = True
                seen.append(id)
                # Arbitrary
                if (len(seen) > 20):
                    seen = seen[9:]

                # twitter shows time in UTC/GMT
                t_date = datetime.fromisoformat(t_time.replace("Z", "+00:00"))
                logger.info("Found tweet {id} at {time}".format(id=id, time=t_date))

                # Stop
                if (ndate - t_date > timedelta(minutes=limit)):
                    fetch = False
                    logger.info("Tweet time limit exceeded")
                    break

                writer.writerow({"id": id, "time": t_date.astimezone(tz_save).isoformat(), "content": content})

                driver.execute_script("window.scrollBy(0, {y})".format(y=height))
                time.sleep(random.uniform(0.25, 0.5))

        # perhaps still loading?
        if not dirty:
            if retries > TWEET_TIMEOUT:
                raise TimeoutException()
            retries += 1
            time.sleep(1)
        else:
            retries = 0

    output.close()        
    
