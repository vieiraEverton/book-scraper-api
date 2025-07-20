from sqlmodel import Session, select
from api.models.category import Category

class CategoryService:
    def __init__(self, session: Session):
        self.session = session

    def get_by_name(self, name: str) -> Category | None:
        stmt = select(Category).where(Category.name == name)
        return self.session.exec(stmt).first()

    def create_category(self, **data) -> Category:
        existing = self.get_by_name(data["name"])
        if existing:
            return existing

        category = Category(**data)
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def get_book(self, category_id: int) -> Category | None:
        return self.session.get(Category, category_id)

    def list_categories(self) -> list[Category]:
        statement = select(Category)
        return self.session.exec(statement).all()
