import numpy as np
import pandas as pd

from models.schemas import ROUTES, PredictionRequest

MIN_HISTORY_HOURS = 120
MAX_HISTORY_HOURS = 24 * 90


def simulate_history(start: pd.Timestamp) -> pd.DataFrame:
    random = np.random.default_rng(42)
    timestamps = pd.date_range(end=start - pd.Timedelta(hours=1), periods=336, freq="h")
    daily_pattern = 1 + 0.35 * np.sin(2 * np.pi * timestamps.hour.to_numpy() / 24)
    volumes = {}
    for index, route in enumerate(ROUTES):
        hourly_mean = (8 + index * 2) * daily_pattern
        volumes[route] = random.poisson(hourly_mean)
    return pd.DataFrame(volumes, index=timestamps, dtype=float)


def load_history(request: PredictionRequest):
    if not request.history:
        start = pd.Timestamp(request.forecast_start)
        return simulate_history(start), None, "simulated"

    records = pd.DataFrame([row.model_dump() for row in request.history])
    records["timestamp"] = pd.to_datetime(records["timestamp"], utc=True).dt.floor("h")
    if set(records["route"]) != set(ROUTES):
        raise ValueError("Historical input must include all eight routes")

    start = pd.Timestamp(request.forecast_start)
    if records["timestamp"].max() >= start:
        raise ValueError("Historical observations must precede forecast_start")

    timestamps = pd.date_range(records["timestamp"].min(), start - pd.Timedelta(hours=1), freq="h")
    if not MIN_HISTORY_HOURS <= len(timestamps) <= MAX_HISTORY_HOURS:
        raise ValueError("Provide between 120 and 2160 hours of historical data")

    volumes = records.pivot_table(
        index="timestamp", columns="route", values="pallet_volume", aggfunc="sum"
    ).reindex(index=timestamps, columns=list(ROUTES))

    if volumes.iloc[0].isna().any() or volumes.isna().mean().max() > 0.2:
        raise ValueError("Each route needs a complete first hour and at least 80% hourly coverage")

    delays = records.pivot_table(
        index="timestamp", columns="route", values="delay_minutes", aggfunc="mean"
    ).reindex(index=timestamps, columns=list(ROUTES))
    return volumes, delays, "historical"
