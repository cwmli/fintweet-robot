# Fintweet Robot 
## Prerequisites

* anaconda 3
* chrome

## Setup:

1. `conda env create -f scraping_env.yml`

2. `conda activate scraper`

## Run:

The scraper can be run with a python script that operates on multiple symbols in a multiprocessed manner by using the __scrape_worker__ function defined in `worker.py`

For instance running the worker once can be done by calling this function as:

```python
# Parameter details located in workers.py
workers.scrape_worker(3,
    ["TSLA", "AAPL", "MSFT"],
    {"stocktwit": {"limit": 1440, "output": "../../data/testing/stocktwit"},
        "twitter": {"limit": 1440, "output": "../../data/testing/twitter"} },
    "proxy_hist_stocktwit.txt")
```

The `main.py` script contains an example on running the workers on scheduled times (similar to crontabs) using the `schedule` package

Alternatively, we can simply run the scrape on a single symbol by creating an instance of __ScrapeJob__ in `jobs.py`

```python
import jobs

j = jobs.StocktwitJob({
    "limit": 1440, 
    "output": "../../data/testing/stocktwit",
    "symbol": "TSLA"},
    <proxy_list>,
    <recommended_proxies>)

j.run()
```
