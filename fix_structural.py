#!/usr/bin/env python

import sys
from datetime import datetime
from uuid import uuid4, UUID
from json import dumps, loads
import logging
from copy import deepcopy

import urllib3
import urllib3.connectionpool

import dpath.util as dpath
from deepdiff import DeepDiff
from splitstream import splitfile
from rich.logging import RichHandler


# https://github.com/cdgriffith/Box
# https://scrapfly.io/blog/parse-json-jmespath-python/
# https://github.com/dpath-maintainers/dpath-python

# Setting up log handler


class MyFilter(logging.Filter):
    def filter(self, record):
        if record.name != "fixer":
            return False
        return True


class MyLogger(logging.Logger):
    def __init__(self, name):
        logging.Logger.__init__(self, name)
        self.addFilter(MyFilter())


logging.setLoggerClass(MyLogger)

logging.basicConfig(
    level="INFO",
    format="[%(asctime)s %(levelname) 8s] %(message)s",
    datefmt="%Y%m%d:%H%M%S",
    handlers=[
        logging.FileHandler("rengu_fix.log"),
        # RichHandler(rich_tracebacks=True, tracebacks_suppress=[urllib3])
        logging.StreamHandler(),
    ],
)

log = logging.getLogger("fixer")


def get_one(store, query):

    try:
        result = next(store.query(query))
        return result
    except StopIteration:
        return None


def main(store):

    for data in [loads(j) for j in splitfile(sys.stdin, format="json")]:

        orig = deepcopy(data)

        _id = data.get("ID")
        _type = data.get("Category")
        _by = data.get("By")

        # FIX STRUCTURAL

        ARRAYS = ["References", "SeeAlso", "Commentary"]

        for check in ARRAYS:
            for path, source in dpath.search(
                data, f"**.{check}", separator=".", yielded=True
            ):

                if not isinstance(source, (list, str)):
                    log.exception(f"FATAL {_id} is {type(source)}")
                    raise TypeError


if __name__ == "__main__":

    from os import environ
    from rengu.cli.common import storage_handler

    store = storage_handler(environ["RENGU_BASE"])

    main(store)
