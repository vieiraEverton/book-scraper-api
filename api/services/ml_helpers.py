from api.db import engine
from sqlmodel import Session


def parse_price(price: str) -> float:
    return float(price.replace('Â£', '').replace('£', '').strip())

def parse_rating(rating: str) -> int:
    mapping = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
    return mapping.get(rating, 0)

def parse_availability(availability: str) -> int:
    import re
    match = re.search(r'\((\d+)\s+available\)', availability)
    return int(match.group(1)) if match else 0


def encode_category(cat: str) -> int:
    from api.services.ml_service import get_category_mapping

    with Session(engine) as session:
        mapping = get_category_mapping(session)
        return mapping.get(cat, -1)