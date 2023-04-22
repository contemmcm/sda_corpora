"""
Module for holding all configuration settings and constants used for
downloading this corpus.
"""
import os

from decouple import config


BASE_URL = "https://m.egwwritings.org"

COOKIES = {
    "phpsession": config("EGWWRITINGS_PHPSESSION")
}

INDEX_DIRECTORY = ".egwwritings_indexes"
DOWNLOAD_DIRECTORY = os.path.join("corpora", "egwwritings")


if not os.path.exists(INDEX_DIRECTORY):
    os.makedirs(INDEX_DIRECTORY)

if not os.path.exists(DOWNLOAD_DIRECTORY):
    os.makedirs(DOWNLOAD_DIRECTORY)
