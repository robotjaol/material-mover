from fastapi import APIRouter, HTTPException

from models.schemas import PredictionRequest, PredictionResponse
from services.prediction import predict

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
def create_prediction(request: PredictionRequest):
    try:
        return predict(request)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
