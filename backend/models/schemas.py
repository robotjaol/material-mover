from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

ROUTES = {'tube_station_1': 150, 'tube_station_2': 200, 'tube_station_3': 250,
          'tube_station_4': 300, 'non_tube_station_5': 180,
          'non_tube_station_6': 220, 'rms_a': 400, 'rms_c': 350}
Material = Literal['tube', 'non_tube']


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)


class TruckConfig(StrictModel):
    truck_id: int = Field(ge=1)
    pallet_volume: int = Field(ge=0, le=10000)
    arrival_time: str = Field(pattern=r'^([01]\d|2[0-3]):[0-5]\d$')
    material: Material = 'tube'


class Fleet(StrictModel):
    tube: int = Field(default=4, ge=1, le=100)
    non_tube: int = Field(default=3, ge=1, le=100)


class AGVConfig(StrictModel):
    mode: Literal['single', 'dual', 'specialized'] = 'single'
    # Legacy field name: these values are fleet counts, not throughput.
    per_hour: Fleet = Field(default_factory=Fleet)


class ThresholdConfig(StrictModel):
    station: str
    per_hour: list[float] = Field(min_length=1, max_length=48)


class Observation(StrictModel):
    timestamp: datetime
    route: str
    pallet_volume: float = Field(ge=0, le=100000)
    delay_minutes: float | None = Field(default=None, ge=0)


class PredictionRequest(StrictModel):
    trucks: list[TruckConfig] = Field(default_factory=list, max_length=100)
    agv_config: AGVConfig = Field(default_factory=AGVConfig)
    thresholds: list[ThresholdConfig] = Field(default_factory=list, max_length=8)
    material_assignments: dict[str, Material] = Field(default_factory=lambda: {'tube': 'tube', 'non_tube': 'non_tube'})
    history: list[Observation] = Field(default_factory=list, max_length=20000)
    horizon: int = Field(default=12, ge=1, le=48)
    forecast_start: datetime | None = None
    delay_threshold_minutes: float = Field(default=30, ge=0)

    @model_validator(mode='after')
    def validate_inputs(self):
        if len({t.truck_id for t in self.trucks}) != len(self.trucks):
            raise ValueError('Truck IDs must be unique')
        if set(self.material_assignments) != {'tube', 'non_tube'}:
            raise ValueError('Material assignments require tube and non_tube keys')
        if len({t.station for t in self.thresholds}) != len(self.thresholds):
            raise ValueError('Threshold stations must be unique')
        for t in self.thresholds:
            if t.station not in ROUTES or len(t.per_hour) != self.horizon or any(v < 0 for v in t.per_hour):
                raise ValueError('Thresholds require a known route and one nonnegative value per forecast hour')
        if any(o.route not in ROUTES for o in self.history):
            raise ValueError('History contains an unknown route')
        if self.forecast_start:
            self.forecast_start = self.forecast_start.replace(tzinfo=self.forecast_start.tzinfo or timezone.utc).astimezone(timezone.utc)
            if self.forecast_start.minute or self.forecast_start.second or self.forecast_start.microsecond:
                raise ValueError('forecast_start must align to an hour')
        return self


class ForecastEntry(StrictModel):
    hour: int
    timestamp: str
    route: str
    pallet_volume: float
    baseline_pallets: float
    scheduled_pallets: float
    threshold: float
    alert: bool
    capacity_per_hour: float
    backlog_pallets: float
    delay_minutes: float
    bottleneck: bool


class DelayEntry(StrictModel):
    hour: int
    timestamp: str
    route: str
    delay_minutes: float
    backlog_pallets: float
    bottleneck: bool


class ErrorMetrics(StrictModel):
    mae: float | None
    rmse: float | None
    samples: int


class RouteMetrics(StrictModel):
    forecast: ErrorMetrics
    delay: ErrorMetrics
    delay_label_source: Literal['measured', 'queue_simulation']
    threshold_breach_detection_rate: float | None
    threshold_positive_samples: int
    bottleneck_accuracy: float
    bottleneck_samples: int


class PredictionResponse(StrictModel):
    forecast_table: list[ForecastEntry]
    delay_summary: list[DelayEntry]
    alerts: list[str]
    evaluation: dict[str, RouteMetrics]
    model_status: dict[str, dict[str, dict[str, str]]]
    metadata: dict[str, str | int]
