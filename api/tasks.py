from concurrent.futures import ThreadPoolExecutor, as_completed

from sqlmodel import Session

from api.db import engine
from api.services.book_service import BookService
from scripts.scrape_books import list_categories, list_books_urls_by_category, fetch_book

BASE_URL = "https://books.toscrape.com/"

def perform_scrape():
    categories = list_categories()

    with Session(engine) as session:
        book_service = BookService(session)
        for category in categories:
            print(f"📂 Categoria: {category['name']}")

            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = {executor.submit(fetch_book, url): url for url in list_books_urls_by_category(category['link'])}
                for future in as_completed(futures):
                    result = future.result()

                    book = book_service.create_book(**result)
                    print(f"{'🔄 Atualizado' if book.id else '✔ Salvo'}: {result['title']}")

    print("✅ Job de scraping concluído.")
