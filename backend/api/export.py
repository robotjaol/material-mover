import csv
import io

from fastapi import APIRouter, Response

from api.prediction import create_prediction
from models.schemas import PredictionRequest

router = APIRouter()


@router.post("/export")
def export_csv(request: PredictionRequest):
    prediction = create_prediction(request)
    output = io.StringIO(newline="")
    columns = list(prediction.forecast_table[0].model_fields)
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    for row in prediction.forecast_table:
        writer.writerow(row.model_dump())
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=pallet_forecast.csv"},
    )
