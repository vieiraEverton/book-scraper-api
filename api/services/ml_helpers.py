import re

from api.db import engine
from sqlmodel import Session


def parse_price(value) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if value is None:
        raise ValueError("price is None")
    s = str(value).strip()
    s = s.replace("Â£", "").replace("£", "").replace(",", "")
    return float(s)

def parse_rating(value) -> int:
    if isinstance(value, (int, float)):
        v = int(value)
        return max(1, min(5, v))
    if value is None:
        return 0
    s = str(value).strip().title()
    mapping = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    if s.isdigit():
        v = int(s)
        return max(1, min(5, v))
    return mapping.get(s, 0)

def parse_availability(value) -> int:
    if isinstance(value, (int, float)):
        return int(value)
    if value is None:
        return 0
    s = str(value)
    m = re.search(r"(\d+)", s)
    return int(m.group(1)) if m else 0


def encode_category(cat: str) -> int:
    from api.services.ml_service import get_category_mapping

    with Session(engine) as session:
        mapping = get_category_mapping(session)
        return mapping.get(cat, -1)