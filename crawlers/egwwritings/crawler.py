import json
import os
import re

from functools import lru_cache
from multiprocessing import Pool
from pathlib import Path

from bs4 import BeautifulSoup

import requests

from . import settings


class BookDownloader:

    def __init__(self, book):
        self.book = book
    
    def _ensure_directory_exists(self):
        parent_path = os.path.dirname(self.book["Path"])
        if not os.path.exists(parent_path):
            Path(parent_path).mkdir( parents=True)


    def save_book(self):
        """
        Download and save a book to the file system.
        """
        content = self.fetch_book_content()

        self._ensure_directory_exists()

        with open(self.book["Path"], 'w', encoding="utf8") as fout:
            fout.write(content)

    def fetch_book_content(self):
        """
        Fetch the book content, going from page to page.
        """
        url = self.book["Url"]
        content = ""

        while url:
            page, url = self.parse_page_content(url)
            content += page

        return content

    def parse_page_content(self, url):
        """
        Download and parse a single page
        """
        n_max_attempts = 1000
        for attempt in range(1, n_max_attempts):
            try:
                page = requests.get(url, timeout=120)
                break
            except requests.exceptions.ReadTimeout as err:
                print(str(err), f"new attempt: {attempt}")
                continue

        page_content = page.content.decode()

        # Replacing <br> with newline
        page_content = re.sub(r"<br />", "\n", page_content)

        # HTML parser
        soup = BeautifulSoup(page_content, "html.parser")

        # Page content
        content = ""

        for item in soup.findAll("span", {"class": ["egw_content"]}):
            content += item.text + (os.linesep * 2)

        # Next page
        new_button = soup.find("a", {"class": "btn-large"}, string="Next")

        if not new_button or new_button.attrs['href'] == "#":
            return (content, None)

        next_url = settings.BASE_URL + new_button.attrs['href']

        return content, next_url


@lru_cache
def load_indexes(fname=settings.INDEX_FILE):    
    with open(fname, 'r', encoding="utf8") as fin:
        return [json.loads(line) for line in fin.readlines()]


def download_book(book):
    BookDownloader(book).save_book()


def start_or_resume_download(processes=1):
    # selecting only books that have not been downloaded yet
    books = [book for book in load_indexes() if not os.path.exists(book["Path"])]

    with Pool(processes) as p:
        p.map(download_book, books)


if __name__ == "__main__":
    start_or_resume_download(processes=os.cpu_count())
