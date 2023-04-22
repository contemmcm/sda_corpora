"""
This script is used to enumerate all index pages for book at the website
https://m.egwwritings.org/ .

Usage:

$ python3 -u -m crawlers.egwwritings.enumerate

You need to create a .env file and include there a variable called
EGWWRITINGS_PHPSESSION with the authenticated cookie. To retrieve the cookie,
proceed as follow (Google Chrome):

- Login and authenticate to https://m.egwwritings.org/
- Press F12
- Go to Application (tab) > Cookies (sidebar)
- Copy the value of the "phpsession" cookie

Then, put it on the .env file:

$ echo "EGWWRITINGS_PHPSESSION=1n8o599td5tpv4v7jred2v7vd5" >> .env
"""
import os
import json
import requests

from bs4 import BeautifulSoup
from slugify import slugify

from .settings import BASE_URL, COOKIES, INDEX_DIRECTORY


def parse_index(base_url):
    """
    Parse the book list from the given base_url
    """
    response = requests.get(base_url, timeout=60, cookies=COOKIES)

    if response.status_code == 404:
        return response.status_code

    soup = BeautifulSoup(response.content, "html.parser")
    index = []

    # title
    breadcrumb = []
    for item in soup.find("ul", {"class": "breadcrumb"}).find_all("li"):
        breadcrumb.append(item.text)

    basepath = "__".join([slugify(w) for w in breadcrumb])
    fname = basepath + ".json"

    for item in soup.find_all("div", {"class": ["media", "book-entry"]}):
        title = item.find("h4", {"class": "book-title"}).text
        url = item.find("a", {"class": ["button", "primary"]}).attrs["href"]

        index.append({
            "book": title,
            "url": url,
            "path": basepath,
        })

    fout_name = os.path.join(INDEX_DIRECTORY, fname)
    with open(fout_name, "w", encoding="utf8") as fout:
        fout.write(json.dumps(index, indent=2))

    return response.status_code


def brute_force_indexes():
    """
    Enumarate all folders by brute-force
    """
    for i in range(0, 1500):
        url = f"{BASE_URL}{i}"
        status_code = parse_index(url)

        if status_code == 200:
            print(f"{url}:\t[ok]")


if __name__ == "__main__":
    brute_force_indexes()
