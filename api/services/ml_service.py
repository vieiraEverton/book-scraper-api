import os
from typing import List, Dict

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.utils import Bunch
from sqlmodel import Session, select

from api.db import engine
from api.models.book import Book
from api.services.ml_helpers import parse_price, parse_rating, parse_availability, encode_category

MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "logistic_model.joblib")

def load_book_dataset() -> Bunch:
    with Session(engine) as session:
        books = session.exec(select(Book)).all()
        cat_map = get_category_mapping(session)

        data, target, detail_pages = [], [], []
        for b in books:
            try:
                price = parse_price(b.price)
                rating = parse_rating(b.rating)
                availability = parse_availability(b.availability)
                category_encoded = cat_map.get(b.category, -1)
                data.append([price, rating, availability, category_encoded])
                target.append(1 if rating >= 4 else 0)
                detail_pages.append(b.detail_page)
            except Exception as e:
                print(f"Erro ao converter livro: {b.title} → {e}")
                continue

    feature_names = ["price","rating","availability","category_encoded"]
    return Bunch(
        data=data,
        target=target,
        feature_names=feature_names,
        detail_pages=detail_pages
    )


def train_logistic_model(test_size=0.2, random_state=42, save_path=MODEL_PATH):
    # 1. Carregar dados
    with Session(engine) as session:
        books = session.exec(select(Book)).all()

    # 2. Pré-processar
    data = []
    labels = []
    for book in books:
        try:
            price = parse_price(book.price)
            rating = parse_rating(book.rating)
            availability = parse_availability(book.availability)
            category = encode_category(book.category)
            label = 1 if price > 30 else 0

            data.append([price, rating, availability, category])
            labels.append(label)
        except Exception as e:
            print(f"Erro ao processar livro '{book.title}': {e}")
            continue

    if len(data) < 10:
        raise ValueError(f"Poucos dados disponíveis para treino: {len(data)} exemplos")

    X = np.array(data)
    y = np.array(labels)

    # 3. Split e treino
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    # 4. Avaliação
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)

    # 5. Validação cruzada opcional
    cv_scores = cross_val_score(model, X, y, cv=5)
    print("Cross-val accuracy:", cv_scores.mean())

    # 6. Salvar modelo
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    joblib.dump(model, save_path)

    return {
        "accuracy": round(acc, 4),
        "report": report,
        "model_path": save_path
    }


def predict_logistic(batch: List[List[float]]) -> List[int]:
    """
    Recebe uma lista de listas com features numéricas.
    Exemplo: [[price, rating, availability, category_encoded], ...]
    Retorna: [0, 1, 0, ...]
    """
    # 1. Carregar modelo
    try:
        model = joblib.load(MODEL_PATH)
    except FileNotFoundError:
        raise ValueError(f"Modelo não encontrado em: {MODEL_PATH}")

    # 2. Validar entrada
    if not isinstance(batch, list) or not all(isinstance(row, list) for row in batch):
        raise ValueError("Formato inválido. Esperado: List[List[float]]")

    # 3. Validar número de features
    expected_features = 4
    for row in batch:
        if len(row) != expected_features:
            raise ValueError(f"Cada entrada deve conter {expected_features} valores. Recebido: {len(row)}")

    # 4. Converter para numpy array
    X = np.array(batch)

    # 5. Fazer predição
    predictions = model.predict(X)


def get_category_mapping(session: Session) -> dict[str, int]:
    stmt = select(Book.category).distinct()
    results = session.exec(stmt).all()
    categories = sorted(set(results))
    return {cat: idx for idx, cat in enumerate(categories)}

def get_feature_data() -> List[List[float]]:
    dataset = load_book_dataset()
    return dataset.data

def get_training_data() -> Dict[str, List]:
    dataset = load_book_dataset()
    return {
        "features": dataset.data,
        "labels": dataset.target
    }
