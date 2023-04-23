import os 

from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException

from bs4 import BeautifulSoup

chrome_options = Options()
# chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)


def download_article(url):
    driver.get(url)

    content = ""

    # Title, subtitle and author
    for elm in driver.find_elements(By.CLASS_NAME, "ct-headline"):
        if elm.text == "RELATED STORIES":
            break
        content += elm.text + 2 * os.linesep
    
    # Main content
    content_elm = driver.find_element(By.CLASS_NAME, "ct-inner-content")
    soup = BeautifulSoup(content_elm.get_attribute("innerHTML"), 'html.parser')

    # Removing captial first letter
    span = soup.find('span', {'class': 'cap'})

    if span:
        try:
            text = span.string
            span.replace_with(text)
        except ValueError:
            pass

    for p in soup.find_all("p"):
        content += p.text + 2 * os.linesep
    
    return content


def save_content(content, url):
    path = "corpus" / Path( url.replace("https://adventistreview.org/", "")[0:-1] + ".txt")
    parent = path.parent

    if not parent.exists():
        parent.mkdir(parents=True)

    with open(path, "w", encoding="utf8") as fout:
        fout.write(content)


def download_url(url):
    print(f'{url}: ', end='')
    try:
        content = download_article(url)
        save_content(content, url)
        print('\t[ok]')
    except (NoSuchElementException, WebDriverException):
        with open('error.txt', 'a', encoding="utf8") as fout:
            fout.write(url + os.linesep)
        print('\t[fail]')

def download_all(skip=0):
    with open('urls.txt') as fin:
        urls = fin.readlines()
    
    for i, url in enumerate(urls):
        if i < skip:
            continue
        download_url(url.strip())


if __name__ == "__main__":
    download_all(skip=2868)
    # download_url("https://adventistreview.org/magazine-article/this-hallowed-ground/")
