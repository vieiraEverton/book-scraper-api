from pydantic import BaseModel
from typing import List

class FeatureSchema(BaseModel):
    detail_page: str
    price: float
    rating: int
    availability_numeric: int
    category_encoded: int

class TrainingSchema(FeatureSchema):
    target: str

class PredictionRequest(FeatureSchema):
    pass

class PredictionResponse(BaseModel):
    prediction: str

class BatchRequest(BaseModel):
    batch: List[List[float]]