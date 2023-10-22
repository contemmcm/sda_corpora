"""
Module for holding all configuration settings and constants used for
downloading this corpus.
"""
import os

BASE_URL = "https://m.egwwritings.org"
DOWNLOAD_DIRECTORY = os.path.join("corpora", "egwwritings")
INDEX_FILE = os.path.join(DOWNLOAD_DIRECTORY, "index.jsonl")

if not os.path.exists(DOWNLOAD_DIRECTORY):
    os.makedirs(DOWNLOAD_DIRECTORY)
