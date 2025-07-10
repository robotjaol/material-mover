from pydantic import BaseModel
from typing import List, Dict, Any

class TruckConfig(BaseModel):
    truck_id: int
    pallet_volume: int
    arrival_time: str  # ISO format

class AGVConfig(BaseModel):
    mode: str
    per_hour: Dict[str, Any]

class ThresholdConfig(BaseModel):
    station: str
    per_hour: List[int]

class PredictionRequest(BaseModel):
    trucks: List[TruckConfig]
    agv_config: AGVConfig
    thresholds: List[ThresholdConfig]
    material_assignments: Dict[str, str]

class ForecastEntry(BaseModel):
    hour: int
    route: str
    pallet_volume: int
    threshold: int
    alert: bool

class DelayEntry(BaseModel):
    truck_id: int
    route: str
    delay_minutes: float

class PredictionResponse(BaseModel):
    forecast_table: List[ForecastEntry]
    delay_summary: List[DelayEntry]
    alerts: List[str] 