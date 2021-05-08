# Fintweet Robot 

## Run:

The scraper can be run with a python script that operates on multiple symbols in a multiprocessed manner by using the __scrape_worker__ function defined in `worker.py`

For instance running the worker once can be done by calling this function as:

```python
import logging
import time
import datetime

import schedule

import fintweet_robot

from multiprocessing import freeze_support

if __name__ == "__main__":
    freeze_support()

    try:
        # does not handle exceptions
        # need to add a exception decorator to job
        # schedule.every(10).minutes.do(jobs.stocktwit_scrape, 
        #   symbols=[ "TSLA", "AAPL", "MSFT" ], 
        #   time_limit=10, 
        #   output_path="../../data", 
        #   phist_file="proxy_hist_stocktwit.txt")

        # while True:
        #     schedule.run_pending()
        #     time.sleep(1)
        # jobs.stocktwit_scrape([ "TSLA", "AAPL", "MSFT" ], 1440, "../../data", "proxy_hist_stocktwit.txt")
        # jobs.twitter_scrape(["TSLA"], 1440, "../../data/twitter", datetime.datetime(2021,4,15, tzinfo=datetime.timezone.utc), "proxy_hist_stocktwit.txt")
        
        fintweet_robot.scrape_worker(3,
            ["TSLA", "AAPL", "MSFT"],
            {"stocktwit": {"limit": 1440, "output": "../../data/testing/stocktwit"},
             "twitter": {"limit": 1440, "output": "../../data/testing/twitter"} },
            "proxy_hist_stocktwit.txt")

    except KeyboardInterrupt:
        print("Stopping scheduler")

```

The `main.py` script contains an example on running the workers on scheduled times (similar to crontabs) using the `schedule` package

Alternatively, we can simply run the scrape on a single symbol by creating an instance of __ScrapeJob__ in `jobs.py`

```python
import fintweet_robot

j = fintweet_robot.StocktwitJob({
    "limit": 1440, 
    "output": "../../data/testing/stocktwit",
    "symbol": "TSLA"},
    <proxy_list>,
    <recommended_proxies>)

j.run()
```
