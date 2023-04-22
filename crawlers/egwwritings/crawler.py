"""
This script is used to download all books and publications available at
https://m.egwwritings.org/ using a multi-thread approach.

Usage:

$ python3 -u -m crawlers.egwwritings.crawler
"""
import glob
import argparse
import os
import re
import sys
import json
import threading

import requests

from bs4 import BeautifulSoup
from slugify import slugify

from .settings import BASE_URL, COOKIES, INDEX_DIRECTORY, DOWNLOAD_DIRECTORY


class BookDownloader:
    """
    Class for downloading a single book, all its pages.
    """

    def __init__(self, book, url, path):
        self.title = book
        self.url = BASE_URL + url
        self.prefix = path

    def save_book(self):
        """
        Download and save a book to the file system.
        """
        # Download book content
        content = self.fetch_book_content()

        # Saving the downloaded content
        book_id = os.path.basename(self.url)
        book_title_slug = slugify(self.title)
        download_dir = os.path.join(DOWNLOAD_DIRECTORY, self.prefix)

        # Creating download directory if it does not exist
        if not os.path.isdir(download_dir):
            os.mkdir(download_dir)

        basename = f"{book_id}-{book_title_slug}.txt"
        fpath = os.path.join(download_dir, basename)

        with open(fpath, 'w', encoding="utf8") as fout:
            fout.write(content)

    def fetch_book_content(self):
        """
        Fetch the book content, going from page to page.
        """
        url = self.url
        content = ""

        while url:
            page, url = self.parse_page_content(url)
            content += page

        return content

    def parse_page_content(self, url):
        """
        Download and parse a single page
        """
        for attempt in range(1000):
            try:
                page = requests.get(url, timeout=120, cookies=COOKIES)
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

        next_url = BASE_URL + new_button.attrs['href']

        return content, next_url


def create_corpus_threaded(input_obj, n_threads):
    """
    Download books using multi-thread approach.
    """
    if isinstance(input_obj, str):
        # Download books from single index file
        path = input_obj
        with open(path, 'r', encoding="utf8") as fin:
            books = json.loads(fin.read())
    else:
        books = input_obj

    # Split books into n_threads
    book_lists = split_book_list(books, n_threads)

    # Creating download threads
    threads = []
    for book_list in book_lists:
        thread = threading.Thread(target=download_book_list, args=(book_list,))
        threads.append(thread)
        thread.start()

    # Wait threads to finish
    for thread in threads:
        thread.join()


def split_book_list(books, n_groups):
    """
    Split the book list into N groups.
    """
    if n_groups == 1:
        return [books]

    if len(books) < n_groups:
        n_groups = len(books)

    while (len(books) / n_groups) < 1:
        n_groups -= 1

    length, remainder = len(books) // n_groups, len(books) % n_groups
    book_lists = []
    start = 0
    for i in range(n_groups):
        end = start + length
        if i < remainder:
            end += 1
        book_lists.append(books[start:end])
        start = end

    return book_lists


def download_book_list(book_list):
    """
    Download a list of books sequentially.
    """
    for book in book_list:
        print(f'Downloading book "{book.get("book")}"')
        downloader = BookDownloader(**book)
        downloader.save_book()


def load_combined_indexes():
    """
    Load all index files to memory
    """
    books = []
    for file in glob.glob(os.path.join(INDEX_DIRECTORY, "*.json")):
        with open(file, "r", encoding="utf8") as fin:
            content = fin.read()
            if content:
                json_data = json.loads(content)
                books.extend(json_data)
    return books


def main(*args):
    """
    Main function of the program.
    """
    parser = argparse.ArgumentParser(
        description="Download books from https://m.egwwritings.org"
    )
    parser.add_argument(
        "--n_threads",
        type=int,
        default=os.cpu_count(),
        help="The number of threads to be used for the download"
    )
    parser.add_argument(
        "--index", help="The index JSON file with a list of books"
    )

    # Parsing input arguments
    arguments = parser.parse_args(*args)

    if arguments.index:
        create_corpus_threaded(
            arguments.index, n_threads=os.cpu_count()
        )
    else:
        books = load_combined_indexes()
        create_corpus_threaded(
            books, n_threads=os.cpu_count()
        )


if __name__ == "__main__":
    main(sys.argv[1:])
