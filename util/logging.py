import logging
import os
from datetime import datetime


def init_logging(verbose=False):
    if not os.path.exists("logs"):
        os.makedirs("logs")

    now = datetime.now()

    logger = "logs/partition-{}.log".format(now.strftime("%m-%d-%Y-%H:%M"))
    logging.basicConfig(
        filename=logger,
        filemode="w",
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.getLogger().addHandler(logging.StreamHandler())
