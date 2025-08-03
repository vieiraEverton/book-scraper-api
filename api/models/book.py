from typing import Optional
from sqlmodel import SQLModel, Field

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    price: float
    rating: int
    availability: str
    category: str
    image_url: str
    detail_page: str
