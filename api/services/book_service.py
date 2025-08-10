from typing import Optional

from fastapi import Depends
from sqlmodel import Session, select, and_, func
from sqlalchemy import func

from api.db import get_session
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

    def search_books(self,
                     title: Optional[str] = None,
                     category: Optional[str] = None,
                     limit: int = 10,
                     offset: int = 0) -> list[Book]:
        stmt = select(Book)

        filters = []
        if title:
            filters.append(func.lower(Book.title).like(f"%{title.lower()}%"))
        if category:
            filters.append(func.lower(Book.category).like(f"%{category.lower()}%"))

        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.offset(offset).limit(limit)

        return self.session.exec(stmt).all()

    def get_overview_stats(self) -> dict:
        total_books = self.session.exec(select(func.count()).select_from(Book)).one()

        avg_price = self.session.exec(select(func.avg(Book.price))).one()

        rating_distribution = self.session.exec(
            select(Book.rating, func.count())
            .group_by(Book.rating)
            .order_by(Book.rating)
        ).all()

        return {
            "total_books": total_books,
            "average_price": round(avg_price, 2) if avg_price else 0.0,
            "rating_distribution": [
                {"rating": rating, "count": count} for rating, count in rating_distribution
            ]
        }

    def get_category_stats(self) -> list[dict]:
        results = self.session.exec(
            select(
                Book.category,
                func.count().label("count"),
                func.avg(Book.price).label("average_price")
            ).group_by(Book.category)
            .order_by(Book.category)
        ).all()

        return [
            {
                "category": category,
                "book_count": count,
                "average_price": round(avg_price, 2) if avg_price is not None else 0.0
            }
            for category, count, avg_price in results
        ]

    def get_top_books(self, limit: int = 10, offset: int = 0) -> list[Book]:
        stmt = (
            select(Book)
            .order_by(Book.rating.desc())
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(stmt).all()

    def filter_by_price_range(
            self,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            limit: int = 10, offset: int = 0
    ) -> list[Book]:
        stmt = select(Book)

        filters = []
        if min_price is not None:
            filters.append(Book.price >= min_price)
        if max_price is not None:
            filters.append(Book.price <= max_price)

        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.offset(offset).limit(limit)

        return self.session.exec(stmt).all()

def get_book_service(session: Session = Depends(get_session)) -> BookService:
    return BookService(session)