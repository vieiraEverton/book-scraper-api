import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

BASE_URL = "https://books.toscrape.com/"

def get_soup(url: str) -> BeautifulSoup:
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        resp.encoding = 'utf-8'
        return BeautifulSoup(resp.text, "html.parser")
    except RequestException as e:
        print(f"Falha ao buscar {url}: {e}")
        return None

def list_categories():
    categories = []
    home = get_soup(BASE_URL)
    if home is None:
        print("⛔ Não foi possível acessar a homepage. Abortando job.")
        return

    categories_scrape = home.select("div.side_categories ul li ul li a")
    for cat in categories_scrape:
        cat_name = cat.text.strip()
        cat_link = urljoin(BASE_URL, cat["href"])
        categories.append({ 'name': cat_name, 'link': cat_link })
    return categories

def list_books_urls_by_category(category_link: str):
    books_urls = []
    page_url = category_link
    while True:
        soup = get_soup(page_url)
        if not soup:
            break

        for tag in soup.select("article.product_pod"):
            book_url = urljoin(page_url, tag.h3.a["href"])
            books_urls.append(book_url)

        # Find the "Next" button, if it is unavailable it is the last page
        next_btn = soup.select_one("li.next a")
        if not next_btn:
            break

        # Get the next page URL
        page_url = urljoin(page_url, next_btn["href"])
        time.sleep(0.05)
    return books_urls

def fetch_book(book_url: str):
    soup = get_soup(book_url)

    if not soup:
        return None

    title = soup.select_one("div.product_main h1").text.strip()
    price = soup.select_one("p.price_color").text.strip()
    rating = [c for c in soup.select_one("p.star-rating")["class"] if c != "star-rating"][0]
    availability = soup.select_one("p.availability").text.strip()
    category = soup.select_one("ul.breadcrumb").find_all("li")[2].a.get_text(strip=True)
    img_rel = soup.select_one("div.carousel-inner img")["src"]
    image_url = urljoin(book_url, img_rel)

    title = title.encode('utf-8', errors='replace').decode()

    return {
        "title": title,
        "price": price,
        "rating": rating,
        "availability": availability,
        "category": category,
        "image_url": image_url,
        "detail_page": book_url
    }
