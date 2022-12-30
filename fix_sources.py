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
    level="ERROR",
    # level="INFO",
    format="[%(asctime)s %(levelname) 5s] %(message)s",
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


def check_source(store, source, parent_id):

    if _id := source.get("ID"):

        if get_one(store, [f"ID={_id}"]):
            return _id
        else:
            log.error(f"{parent_id} dangling reference {_id}")
            return False

    if url := source.get("URL"):
        log.info(f"{parent_id} Handling URL {url}")
        return False

    for path, isbn in dpath.search(source, "**.ISBN", separator=".", yielded=True):
        isbn = str(isbn).replace("-", "")

        if source_id := get_one(store, [f"ISBN={isbn}"]):
            log.info(f"{parent_id} matched {source_id} to ISBN {isbn}")
            return source_id
        else:
            log.error(f"{parent_id} missing ISBN reference to {isbn}")
            # CREATE

    if title := source.get("Title"):

        results = [u for u in store.query([f"Title={title}", "Category=work"])]
        if len(results) > 0:
            log.info(f"{parent_id} checking title >{title}< count {len(results)}")

            if len(results) == 1:
                result = get_one(store, [f"Title={title}", "Category=work"])
                log.info(f"{parent_id} one match for {title} {result}")
                return result

            # Check match for by
            by = source.get("By", source.get("_try_By"))
            if by:
                if result := get_one(
                    store, [f"Title={title}", f"By={by}", "Category=work"]
                ):
                    log.info(f"{parent_id} found match {result}")
                    return result

            if result := get_one(
                store, [f"Title={title}", f"Media=prime", "Category=work"]
            ):
                log.info(f"{parent_id} found PRIME match {result}")
                return result

            log.error(f"{parent_id} unresolved match for >{title}<")
            return False

        else:
            log.error(f"{parent_id} missing title >{title}<")
            # CREATE

    log.error(f"{parent_id} exhausted all source lookups")
    return


def main(store):

    for data in [loads(j) for j in splitfile(sys.stdin, format="json")]:

        orig = deepcopy(data)

        _id = data.get("ID")
        _type = data.get("Category")
        _by = data.get("By")

        # FIX SOURCES
        for path, source in dpath.search(
            data, "**.Source", separator=".", yielded=True
        ):

            if not isinstance(source, dict):
                log.exception(f"FATAL {_id}")
                raise TypeError("{_id} {path} not dict")

            if not source.get("By"):
                source["_try_By"] = _by

            source_id = check_source(store, source, _id)
            if not source_id:
                log.error(f"{_id} Unresolved {path} source")
            else:
                log.info(f"{_id} Reference {path}.ID={source_id}")
                dpath.new(data, path + ".ID", str(source_id), separator=".")

            if source.get("_try_By"):
                del source["_try_By"]

        # FIX References
        REFS = ["References", "SeeAlso", "Commentary", "Variants"]

        # CHECK CHANGES AND SAVE
        if DeepDiff(orig, data, ignore_order=True):
            log.info(f"{_id} UPDATED")
            print(dumps(data))
        else:
            log.info(f"{_id} unmodifed")


if __name__ == "__main__":

    from os import environ
    from rengu.cli.common import storage_handler

    store = storage_handler(environ["RENGU_BASE"])

    main(store)
