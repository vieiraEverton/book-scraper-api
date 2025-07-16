import time
from urllib.parse import urljoin

from sqlmodel import Session

from api.db import engine, init_db
from api.services.book_service import BookService
from scripts.scrape_books import parse_book_info, get_soup

BASE_URL = "https://books.toscrape.com/"

def scrape_and_store():
    print("🔄 Iniciando job de scraping…")
    init_db()
    with Session(engine) as session:
        service = BookService(session)
        home = get_soup(BASE_URL)
        if home is None:
            print("⛔ Não foi possível acessar a homepage. Abortando job.")
            return

        categories = home.select("div.side_categories ul li ul li a")
        for cat in categories:
            cat_name = cat.text.strip()
            page_url = urljoin(BASE_URL, cat["href"])
            print(f"📂 Categoria: {cat_name}")

            while True:
                soup = get_soup(page_url)
                if not soup:
                    break

                for tag in soup.select("article.product_pod"):
                    info = parse_book_info(tag, cat_name, page_url)
                    if not info:
                        continue
                    book = service.create_book(**info)
                    # se já existia, create_book retorna o existente
                    print(f"{'🔄 Atualizado' if book.id else '✔ Salvo'}: {info['title']}")

                # paginação usando urljoin
                next_btn = soup.select_one("li.next a")
                if not next_btn:
                    break
                page_url = urljoin(page_url, next_btn["href"])
                time.sleep(1)

    print("✅ Job de scraping concluído.")
