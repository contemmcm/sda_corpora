import os 

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)


def find_all_urls(url, prefix):
    driver.get(url)
    urls = []
    for a in driver.find_elements(By.TAG_NAME, 'a'):
        href = a.get_attribute("href")
        if href.startswith(prefix) and href.strip() != prefix:
            print(href)
            urls.append(href)
    return urls

def list_issues():
    return find_all_urls(
        url="https://adventistreview.org/issues/", 
        prefix="https://adventistreview.org/issue/"
    )


def list_articles(url):
    return find_all_urls(
        url, 
        prefix="https://adventistreview.org/magazine-article/"
    )

def create_index_articles():
    with open("articles.txt", "w", encoding="utf8") as fout:
        for issue in list_issues():
            for article in list_articles(issue):
                fout.write(article + os.linesep)

def create_index_news():
    with open("news.txt", "w", encoding="utf8") as fout:
        for page in range(1, 600):
            print(page)
            url = f"https://adventistreview.org/category/category/news/page/{page}/"
            for news in find_all_urls(url, prefix="https://adventistreview.org/news/"):
                fout.write(news + os.linesep)


def create_index_profiles():
    with open("profiles.txt", "w", encoding="utf8") as fout:
        for page in range(1, 20):
            print(page)
            url = f"https://adventistreview.org/category/category/profile/page/{page}/"
            for profiles in find_all_urls(url, prefix="https://adventistreview.org/profile/"):
                fout.write(profiles + os.linesep)


def main():
    create_index_articles()
    create_index_news()
    create_index_profiles()

if __name__ == '__main__':
    main()
