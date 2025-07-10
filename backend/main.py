from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import json

from models.pallet_model import PalletMovementModel
from models.predictive_model import PredictiveModel
from utils.data_generator import generate_sample_data
from utils.analytics import calculate_delays, calculate_efficiency

app = FastAPI(
    title="Smart Factory Pallet Diagnostics API",
    description="Predictive diagnostics for pallet movement in smart factory",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models
pallet_model = PalletMovementModel()
predictive_model = PredictiveModel()

@app.get("/")
async def root():
    return {"message": "Smart Factory Pallet Diagnostics API", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/shifts")
async def get_shifts():
    """Get shift information"""
    shifts = {
        "night": {"start": "22:00", "end": "06:00", "name": "Night Shift"},
        "morning": {"start": "06:00", "end": "14:00", "name": "Morning Shift"},
        "afternoon": {"start": "14:00", "end": "22:00", "name": "Afternoon Shift"}
    }
    return shifts

@app.get("/api/stations")
async def get_stations():
    """Get station information"""
    stations = {
        "loading_dock": {"name": "Loading Dock", "type": "source"},
        "tube_stations": [
            {"id": 1, "name": "Station Tube 1", "type": "tube"},
            {"id": 2, "name": "Station Tube 2", "type": "tube"},
            {"id": 3, "name": "Station Tube 3", "type": "tube"},
            {"id": 4, "name": "Station Tube 4", "type": "tube"}
        ],
        "non_tube_stations": [
            {"id": 5, "name": "Station Non-Tube 5", "type": "non_tube"},
            {"id": 6, "name": "Station Non-Tube 6", "type": "non_tube"}
        ],
        "rms_stations": [
            {"id": "A", "name": "RMS A", "type": "rms", "serves": "tube"},
            {"id": "C", "name": "RMS C", "type": "rms", "serves": "non_tube"}
        ]
    }
    return stations

@app.post("/api/predict")
async def predict_movement(pallet_count: int, shift: str, date: str):
    """Predict pallet movement and potential delays"""
    try:
        # Generate prediction data
        prediction_data = pallet_model.predict_movement(
            pallet_count=pallet_count,
            shift=shift,
            date=date
        )
        
        # Calculate delays and efficiency
        delays = calculate_delays(prediction_data)
        efficiency = calculate_efficiency(prediction_data)
        
        return {
            "prediction": prediction_data,
            "delays": delays,
            "efficiency": efficiency,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/{shift}")
async def get_analytics(shift: str):
    """Get analytics for specific shift"""
    try:
        # Generate sample data for analytics
        sample_data = generate_sample_data(shift)
        
        # Calculate analytics
        analytics = {
            "shift": shift,
            "total_pallets": len(sample_data),
            "average_processing_time": np.mean([d["processing_time"] for d in sample_data]),
            "delays": calculate_delays(sample_data),
            "efficiency": calculate_efficiency(sample_data),
            "station_breakdown": pallet_model.get_station_breakdown(sample_data)
        }
        
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/3d-data")
async def get_3d_data():
    """Get 3D visualization data"""
    try:
        # Generate 3D coordinates for stations
        stations_3d = {
            "loading_dock": {"x": 0, "y": 0, "z": 0, "name": "Loading Dock"},
            "tube_1": {"x": 10, "y": 5, "z": 2, "name": "Station Tube 1"},
            "tube_2": {"x": 15, "y": 5, "z": 2, "name": "Station Tube 2"},
            "tube_3": {"x": 20, "y": 5, "z": 2, "name": "Station Tube 3"},
            "tube_4": {"x": 25, "y": 5, "z": 2, "name": "Station Tube 4"},
            "non_tube_5": {"x": 10, "y": -5, "z": 2, "name": "Station Non-Tube 5"},
            "non_tube_6": {"x": 15, "y": -5, "z": 2, "name": "Station Non-Tube 6"},
            "rms_a": {"x": 30, "y": 5, "z": 3, "name": "RMS A"},
            "rms_c": {"x": 30, "y": -5, "z": 3, "name": "RMS C"}
        }
        
        return {"stations": stations_3d}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/realtime")
async def get_realtime_data():
    """Get real-time pallet movement data"""
    try:
        current_time = datetime.now()
        realtime_data = pallet_model.get_realtime_data(current_time)
        
        return {
            "timestamp": current_time.isoformat(),
            "data": realtime_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 