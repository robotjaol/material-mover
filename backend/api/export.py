from fastapi import APIRouter, Response
from models.schemas import PredictionRequest
from services.prediction import run_prediction
from services.delay import estimate_delays
import io
import csv

router = APIRouter()

@router.post("/export")
def export_csv(request: PredictionRequest):
    """Export forecast and delay data as CSV"""
    # Get prediction data
    forecast_entries = run_prediction(request)
    delay_entries = estimate_delays(request)
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write forecast data
    writer.writerow(['Forecast Data'])
    writer.writerow(['Hour', 'Route', 'Pallet Volume', 'Threshold', 'Alert'])
    for entry in forecast_entries:
        writer.writerow([
            entry.hour,
            entry.route,
            entry.pallet_volume,
            entry.threshold,
            'Yes' if entry.alert else 'No'
        ])
    
    writer.writerow([])  # Empty row
    
    # Write delay data
    writer.writerow(['Delay Data'])
    writer.writerow(['Truck ID', 'Route', 'Delay (minutes)'])
    for entry in delay_entries:
        writer.writerow([
            entry.truck_id,
            entry.route,
            entry.delay_minutes
        ])
    
    # Get CSV content
    csv_content = output.getvalue()
    output.close()
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=pallet_forecast.csv"}
    ) 