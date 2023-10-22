"""
This script is used to enumerate all documents at the website
https://egwwritings.org/ .

Usage:

$ python -u -m crawlers.egwwritings.enumerate
"""
import os
import json

from bs4 import BeautifulSoup

import requests

from .settings import BASE_URL, DOWNLOAD_DIRECTORY, INDEX_FILE


def book_url(book, lang="en"):
    return f"{BASE_URL}/{lang}/book/{book}"


def get_book_info(book, lang="en"):
    url = book_url(book, lang)
    page = requests.get(f"{url}/info", timeout=120)

    if page.status_code != 200:
        return None

    soup = BeautifulSoup(page.content.decode(), "html.parser")

    return _parse_book_details(book, url, soup)


def create_index(max_book_id=30000):

    with open(INDEX_FILE, "w", encoding="utf8") as fout:
        
        for book in range(1, max_book_id + 1):

            details = get_book_info(book, "en")
            
            if not details:
                continue

            # Fix breadcrumb for other languages
            if details["Language"] != "en":
                details = get_book_info(book, details["Language"])

            # Set the download path
            details["Path"] = os.path.join(DOWNLOAD_DIRECTORY, details["Language"],  "%05d.txt" % book)
            
            print(f"{book}\t{details['Language']}\t{details['Title']}")
            fout.write(json.dumps(details) + os.linesep)
            fout.flush()


def _parse_book_details(pk, url, soup):
    book_title = soup.find("h1").text
    details = soup.find(attrs={"class": "book-details"})
    
    # Parsing breadcrumb
    breadcrumbs = []
    for li in soup.find("ul", attrs={"class": "breadcrumb"}).find_all("li"):
        if "class" in li.attrs and "dropdown" in li.attrs["class"]:
            breadcrumbs.append(li.find("a").text)
            break
        breadcrumbs.append(li.text)
            
    titles = [element.text for element in details.find_all("dt")]
    descriptions = [element.text for element in details.find_all("dd")]
    
    book_details = {detail: description for  detail, description in zip(titles, descriptions)}
    book_details["Title"] = book_title
    book_details["Url"] = url
    book_details["Category"] = " > ".join(breadcrumbs[1:-1])  # remove "home" and book name
    book_details["Id"] = pk

    return book_details


if __name__ == "__main__":
    create_index()