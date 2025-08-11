from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from api.db import get_session
from api.schemas.ml import BatchRequest
from api.security import get_current_user
from api.services.ml_service import (
    get_category_mapping,
    train_logistic_model,
    predict_logistic,
    get_feature_data,
    get_training_data,
)

router = APIRouter()

@router.get(
    "/features",
    summary="Obter somente as features numéricas",
    responses={200: {"description": "OK"}},
)
def get_features(
    current_user: dict = Depends(get_current_user),
):
    """
    Retorna **apenas a matriz de features** dos livros, já convertidas para valores numéricos.

    - **Ordem das features**: `[price, rating, availability, category_encoded]`
      - `price`: preço numérico (ex.: "£45.17" → `45.17`)
      - `rating`: nota mapeada para inteiro (`One`→1, ..., `Five`→5)
      - `availability`: número disponível (ex.: "In stock (19 available)" → `19`)
      - `category_encoded`: índice inteiro da categoria

    Use este endpoint quando você só precisa das entradas **X** (sem labels).
    """
    return get_feature_data()

@router.get(
    "/training-data",
    summary="Obter features + labels para treino",
    responses={200: {"description": "OK"}},
)
def get_training(
    current_user: dict = Depends(get_current_user),
):
    """
    Retorna **features** e **labels** (0/1) para treinar/validar modelos.

    - **Label (y)**: por padrão é `1` quando `rating >= 4` e `0` caso contrário.
    - Útil para análises rápidas, validação e para clientes que queiram treinar modelos externamente.
    """
    return get_training_data()

@router.post(
    "/predictions",
    summary="Obter predições do modelo treinado",
    responses={
        200: {"description": "Lista de predições (0/1) na mesma ordem do batch"},
        500: {"description": "Erro interno ao executar a predição"},
    },
)
def post_predictions(
    payload: BatchRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Recebe um **batch** de features e retorna as **predições (0/1)** do modelo de Regressão Logística
    previamente treinado.

    ### Formato do batch
    `[[price, rating, availability, category_encoded], ...]`

    ### Exemplo de request body
    ```json
    {
      "batch": [
        [45.17, 2, 19, 47],
        [49.43, 4, 15, 47]
      ]
    }
    ```
    """
    try:
        return predict_logistic(payload.batch)
    except Exception as e:
        raise HTTPException(500, f"Erro na predição: {e}")

@router.post(
    "/train-logistic",
    summary="Treinar modelo de Regressão Logística",
    responses={200: {"description": "Métricas e caminho do arquivo serializado do modelo"}},
)
def train_logistic(
    test_size: float = Query(
        0.2, ge=0.1, le=0.5,
        description="Proporção do dataset usada para teste (entre 0.1 e 0.5)."
    ),
    seed: int = Query(42, description="Seed para reprodutibilidade do split."),
    current_user: dict = Depends(get_current_user),
):
    """
    Treina o modelo de **Regressão Logística** sobre os livros do banco.

    **Retorna**:
    - `accuracy`: acurácia no conjunto de teste
    - `report`: classification report (precision/recall/f1/support)
    - `model_path`: caminho do arquivo `.joblib` salvo em `models/`
    """
    return train_logistic_model(test_size=test_size, random_state=seed)


@router.get(
    "/category-encodings",
    summary="Mapeamento de categorias para índices"
)
def get_category_encodings(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Retorna um **dicionário** `{categoria: inteiro}` usado para codificar `category_encoded`
    nas features. Ex.:

    ```json
    {
      "Travel": 47,
      "Mystery": 26,
      "Historical Fiction": 21
    }
    ```
    """
    return get_category_mapping(session)
