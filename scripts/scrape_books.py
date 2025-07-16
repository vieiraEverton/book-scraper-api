import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from requests.exceptions import RequestException

BASE_URL = "https://books.toscrape.com/"

def get_soup(url: str) -> BeautifulSoup:
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except RequestException as e:
        print(f"Falha ao buscar {url}: {e}")
        return None

def parse_book_info(book_tag, category: str, page_url: str):
    href = book_tag.h3.a["href"]
    book_url = urljoin(page_url, href)

    soup = get_soup(book_url)

    if not soup:
        return None

    title = soup.select_one("div.product_main h1").text.strip()
    price = soup.select_one("p.price_color").text.strip()
    rating = [c for c in soup.select_one("p.star-rating")["class"] if c != "star-rating"][0]
    availability = soup.select_one("p.availability").text.strip()
    img_rel = soup.select_one("div.carousel-inner img")["src"]
    image_url = urljoin(page_url, img_rel)

    return {
        "title": title,
        "price": price,
        "rating": rating,
        "availability": availability,
        "category": category,
        "image_url": image_url,
        "detail_page": book_url
    }
