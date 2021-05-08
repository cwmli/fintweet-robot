import logging
import logging.handlers
import multiprocessing
import copy
from itertools import chain

from . import utils, jobs


def _logging_process(queue):
    root = logging.getLogger()
    h = logging.handlers.RotatingFileHandler('workers.log', 'a+', 10000, 3)
    f = logging.Formatter('%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')
    h.setFormatter(f)
    root.addHandler(h)

    while True:
        try:
            record = queue.get()
            if record is None:
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)
        except Exception:
            break

def _job_wrapper(j, queue):
    root = logging.getLogger()

    if root.handlers == []:
        handle = logging.handlers.QueueHandler(queue)
        root.addHandler(handle)
    
    root.setLevel(logging.INFO)

    try:
        return j.run()
    except Exception as e:
        logger.exec(e)


def scrape_worker(num_procs, symbols, scrape_opts, phist_file=None):
    """
    :param num_procs: Number of processes to use
    :param symbols: Symbols to query
    :param scrape_opts: Dict of scraper options:
        stocktwit: {time_limit, output_path}
        twitter: {time_limit, output_path, until_date}
    :param phist_file: File containing proxies to first from
    """
    logger = logging.getLogger(__name__)

    f = open(phist_file, "r+")
    content = f.read()
    rec_plist = content.split(",") if len(content) > 0 else []
    logger.info("Loaded last proxies: {t}".format(t=rec_plist))
    plist = utils.proxy_list()

    m = multiprocessing.Manager()
    queue = m.Queue(-1)
    lock = m.Lock()
    logp = multiprocessing.Process(target=_logging_process, args=(queue,))
    logp.start()

    with multiprocessing.Pool(processes=num_procs) as pool:
        futures = []

        for symbol in symbols:
            print("Setting up jobs for {}".format(symbol))
            if "stocktwit" in scrape_opts:
                j1 = jobs.StocktwitJob(
                    {**scrape_opts["stocktwit"], "symbol": symbol},
                    plist,
                    rec_plist,
                    lock)

                futures.append(pool.apply_async(_job_wrapper, (j1, queue)))

            if "twitter" in scrape_opts:
                j2 = jobs.TwitterJob(
                    {**scrape_opts["twitter"], "symbol": symbol},
                    plist,
                    rec_plist,
                    lock)

                futures.append(pool.apply_async(_job_wrapper, (j2, queue)))
    
        v_plists = [ f.get() for f in futures ]

    queue.put_nowait(None)
    logp.join()

    f.seek(0)
    f.truncate()
    f.write(",".join(
        set(list(chain(*v_plists)))
    ))
    f.close()
