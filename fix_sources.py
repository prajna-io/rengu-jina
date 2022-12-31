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
import dpath.exceptions as dpath_exceptions
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
        log.info(f"{parent_id} Skipping Handling URL")
        return False

    for path, isbn in dpath.search(source, "**.ISBN", separator=".", yielded=True):
        if isinstance(isbn, list):
            isbn = isbn[0]
        if isinstance(isbn, float):
            isbn = int(isbn)
        isbn = str(isbn).replace("-", "")
        if len(isbn) == 9:
            isbn = "0" + isbn

        if source_id := get_one(store, [f"ISBN={isbn}"]):
            log.info(f"{parent_id} matched {source_id} to ISBN {isbn}")
            return source_id
        else:
            log.error(f"{parent_id} missing ISBN reference to {isbn}")
            # CREATE

    if title := source.get("Title"):

        # First try simple title match
        results = [u for u in store.query([f"Title={title}", "Category=work"])]

        # Try an alternate title
        if len(results) == 0:
            log.info(f"{parent_id} no results on Title, trying AlternateTitles")
            results = [
                u for u in store.query([f"AlternateTitles={title}", "Category=work"])
            ]

        # Process
        if not results:
            log.error(f"{parent_id} unresolved match for >{title}<")
            return False

        if len(results) == 1:
            log.info(f"{parent_id} one match for {title} {results[0]}")
            return results[0]

        if len(results) > 0:

            result_set = [store.get(result) for result in results]

            # Check match for by
            by = source.get("By", source.get("_try_By"))
            if by:
                for result in result_set:
                    if result.get("By") == by:
                        log.info(f"{parent_id} found match {result.get('ID')} with By=")
                        return result.get("ID")

            # check Media=prime
            for result in result_set:
                if result.get("Media") == "prime":
                    log.info(
                        f"{parent_id} found match {result.get('ID')} with Media=prime"
                    )
                    return result.get("ID")

            log.error(
                f"{parent_id} ambigious matches for >{title}< count {len(results)}"
            )
            return False

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

        # FIX References
        REFS = ["References", "SeeAlso", "Commentary", "Variants"]

        # CHECK CHANGES AND SAVE
        try:
            _ = dpath.delete(data, "**._try_By", separator=".")
        except dpath_exceptions.PathNotFound:
            # ok, ignore
            pass

        if DeepDiff(orig, data, ignore_order=True):
            log.info(f"{_id} UPDATED")
            print(dumps(data))
        else:
            log.info(f"{_id} unmodified")


if __name__ == "__main__":

    from os import environ
    from rengu.cli.common import storage_handler

    store = storage_handler(environ["RENGU_BASE"])

    main(store)
