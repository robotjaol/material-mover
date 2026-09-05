from datetime import datetime, timezone
from functools import lru_cache

import numpy as np
import pandas as pd

from models.schemas import ROUTES, PredictionRequest, PredictionResponse
from services.data import load_history
from services.delay import capacities, queue_series, route_material
from services.evaluation import HOLDOUT_HOURS, evaluate_route
from services.forecasting import forecast_ensemble


def scheduled_demand(request, route, start):
    demand = np.zeros(request.horizon)
    matching_routes = [name for name in ROUTES if route_material(name) == route_material(route)]
    for truck in request.trucks:
        if truck.material != route_material(route):
            continue
        hour, minute = map(int, truck.arrival_time.split(":"))
        arrival = start.normalize() + pd.Timedelta(hours=hour, minutes=minute)
        if arrival < start:
            arrival += pd.Timedelta(days=1)
        offset = int((arrival - start).total_seconds() // 3600)
        if offset < request.horizon:
            demand[offset] += truck.pallet_volume / len(matching_routes)
    return demand


def run_prediction(request: PredictionRequest) -> PredictionResponse:
    history, measured_delays, source = load_history(request)
    start = history.index[-1] + pd.Timedelta(hours=1)
    route_capacities = capacities(request)
    thresholds = {item.station: item.per_hour for item in request.thresholds}
    forecast_rows = []
    delay_rows = []
    evaluation = {}
    model_status = {}
    alerts = []

    for route in ROUTES:
        series = history[route]
        baseline, status = forecast_ensemble(series, request.horizon)
        validation, validation_status = forecast_ensemble(series.iloc[:-HOLDOUT_HOURS], HOLDOUT_HOURS)
        actual = series.iloc[-HOLDOUT_HOURS:]
        observed = np.full(HOLDOUT_HOURS, np.nan)
        if measured_delays is not None:
            observed = measured_delays[route].iloc[-HOLDOUT_HOURS:].to_numpy()

        limits = thresholds.get(route, [20.0] * request.horizon)
        capacity = route_capacities[route]
        evaluation[route] = evaluate_route(
            actual, validation, observed, capacity, limits, request.delay_threshold_minutes
        )
        model_status[route] = {"forecast": status, "validation": validation_status}

        scheduled = scheduled_demand(request, route, start)
        # Truck manifests add demand beyond the historical baseline.
        demand = np.round(baseline + scheduled, 4)
        queues = queue_series(demand, capacity)
        route_has_breach = False
        route_has_bottleneck = False
        for hour, queue in enumerate(queues):
            breach = bool(demand[hour] > limits[hour])
            bottleneck = queue["delay_minutes"] > request.delay_threshold_minutes
            delay_row = {
                "hour": hour,
                "timestamp": (start + pd.Timedelta(hours=hour)).isoformat(),
                "route": route,
                **queue,
                "bottleneck": bottleneck,
            }
            delay_rows.append(delay_row)
            forecast_rows.append({
                **delay_row,
                "pallet_volume": float(demand[hour]),
                "baseline_pallets": round(float(baseline[hour]), 4),
                "scheduled_pallets": round(float(scheduled[hour]), 4),
                "threshold": limits[hour],
                "alert": breach,
                "capacity_per_hour": round(capacity, 4),
            })
            route_has_breach |= breach
            route_has_bottleneck |= bottleneck

        if route_has_breach:
            alerts.append(f"{route}: demand exceeds the pallet threshold")
        if route_has_bottleneck:
            alerts.append(f"{route}: queue delay exceeds {request.delay_threshold_minutes:g} minutes")

    return PredictionResponse(
        forecast_table=forecast_rows,
        delay_summary=delay_rows,
        alerts=alerts,
        evaluation=evaluation,
        model_status=model_status,
        metadata={
            "data_source": source,
            "history_hours": len(history),
            "holdout_hours": HOLDOUT_HOURS,
            "forecast_start": start.isoformat(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "queue_initial_backlog": 0,
            "ensemble": "equal weight across available models",
            "threshold_evaluation": "configured horizon repeated over holdout",
        },
    )


@lru_cache(maxsize=8)
def cached_prediction(payload: str) -> PredictionResponse:
    return run_prediction(PredictionRequest.model_validate_json(payload))


def predict(request: PredictionRequest) -> PredictionResponse:
    if request.forecast_start is None:
        if request.history:
            latest = max(pd.Timestamp(row.timestamp).tz_localize("UTC") if row.timestamp.tzinfo is None
                         else pd.Timestamp(row.timestamp).tz_convert("UTC") for row in request.history)
            start = latest.floor("h") + pd.Timedelta(hours=1)
        else:
            start = pd.Timestamp.now(tz="UTC").floor("h")
        request = request.model_copy(update={"forecast_start": start.to_pydatetime()})
    return cached_prediction(request.model_dump_json())
