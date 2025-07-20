from concurrent.futures import ThreadPoolExecutor, as_completed

from sqlmodel import Session

from api.db import engine
from api.services.book_service import BookService
from api.services.category_service import CategoryService
from scripts.scrape_books import list_categories, list_books_urls_by_category, fetch_book

BASE_URL = "https://books.toscrape.com/"

def perform_initial_scrape():
    print(f"🚀 Performing Initial Scrapping...")
    with Session(engine) as session:
        category_service = CategoryService(session)
        if len(category_service.list_categories()) > 0:
            print("Skipped Initial Scrapping Since the data already exists!")
            return
    perform_scrape()

def perform_scrape():
    categories = list_categories()

    with Session(engine) as session:
        book_service = BookService(session)
        category_service = CategoryService(session)
        for category in categories:
            print(f"📂 Categoria: {category['name']}")

            # Save the category
            category_service.create_category(**{
                'name': category['name']
            })

            # Retrieve the books in parallel
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = {executor.submit(fetch_book, url): url for url in list_books_urls_by_category(category['link'])}
                for future in as_completed(futures):
                    result = future.result()

                    book = book_service.create_book(**result)
                    print(f"{'🔄 Atualizado' if book.id else '✔ Salvo'}: {result['title']}")

    print("✅ Job de scraping concluído.")
