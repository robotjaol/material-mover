from fastapi import APIRouter
from models.schemas import PredictionRequest, PredictionResponse
from services.prediction import run_prediction
from services.delay import estimate_delays
from typing import List

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """Main prediction endpoint"""
    # Run prediction engine
    forecast_entries = run_prediction(request)
    
    # Run delay estimation
    delay_entries = estimate_delays(request)
    
    # Generate alerts
    alerts = generate_alerts(forecast_entries, delay_entries, request)
    
    return PredictionResponse(
        forecast_table=forecast_entries,
        delay_summary=delay_entries,
        alerts=alerts
    )

def generate_alerts(forecast_entries, delay_entries, request):
    """Generate alerts based on forecasts and delays"""
    alerts = []
    
    # Check for threshold breaches
    threshold_alerts = []
    for entry in forecast_entries:
        if entry.alert:
            threshold_alerts.append(f"Route {entry.route} at hour {entry.hour}: {entry.pallet_volume} pallets (threshold: {entry.threshold})")
    
    if threshold_alerts:
        alerts.append(f"⚠️ Threshold breaches detected: {', '.join(threshold_alerts[:3])}")
    
    # Check for high delays
    high_delays = []
    for entry in delay_entries:
        if entry.delay_minutes > 30:  # Alert if delay > 30 minutes
            high_delays.append(f"Truck {entry.truck_id} on {entry.route}: {entry.delay_minutes} min delay")
    
    if high_delays:
        alerts.append(f"🚨 High delays detected: {', '.join(high_delays[:3])}")
    
    # Check for capacity issues
    total_pallets = sum(truck.pallet_volume for truck in request.trucks)
    if total_pallets > 100:
        alerts.append("📊 High pallet volume detected - consider adjusting AGV configuration")
    
    # Check AGV mode efficiency
    agv_mode = request.agv_config.mode
    if agv_mode == 'specialized' and total_pallets > 50:
        alerts.append("⚙️ Specialized AGV mode may cause bottlenecks with high volume")
    
    return alerts 