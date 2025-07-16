from sqlmodel import Session, select
from api.models.book import Book

class BookService:
    def __init__(self, session: Session):
        self.session = session

    def get_by_detail_page(self, detail_page: str) -> Book | None:
        stmt = select(Book).where(Book.detail_page == detail_page)
        return self.session.exec(stmt).first()

    def create_book(self, **data) -> Book:
        existing = self.get_by_detail_page(data["detail_page"])
        if existing:
            return existing

        book = Book(**data)
        self.session.add(book)
        self.session.commit()
        self.session.refresh(book)
        return book

    def get_book(self, book_id: int) -> Book | None:
        return self.session.get(Book, book_id)

    def list_books(self) -> list[Book]:
        statement = select(Book)
        return self.session.exec(statement).all()
