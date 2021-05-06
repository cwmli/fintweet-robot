import logging
import time
import datetime

import schedule

import workers

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
        
        workers.scrape_worker(3,
            ["TSLA", "AAPL", "MSFT"],
            {"stocktwit": {"limit": 1440, "output": "../../data/testing/stocktwit"},
             "twitter": {"limit": 1440, "output": "../../data/testing/twitter"} },
            "proxy_hist_stocktwit.txt")

    except KeyboardInterrupt:
        print("Stopping scheduler")
