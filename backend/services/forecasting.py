import warnings

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from xgboost import XGBRegressor


def lag_features(values, timestamp):
    return [
        values[-1],
        values[-2],
        values[-24],
        np.mean(values[-6:]),
        np.sin(2 * np.pi * timestamp.hour / 24),
        np.cos(2 * np.pi * timestamp.hour / 24),
        timestamp.dayofweek,
    ]


def forecast_xgboost(values, timestamps, horizon):
    training_features = []
    for index in range(24, len(values)):
        training_features.append(lag_features(values[:index], timestamps[index]))

    model = XGBRegressor(
        n_estimators=80, max_depth=3, learning_rate=0.06, n_jobs=1, random_state=42
    )
    model.fit(np.array(training_features), values[24:])

    history = list(values)
    predictions = []
    for step in range(horizon):
        timestamp = timestamps[-1] + pd.Timedelta(hours=step + 1)
        features = np.array([lag_features(history, timestamp)])
        prediction = float(model.predict(features)[0])
        history.append(prediction)
        predictions.append(prediction)
    return np.array(predictions)


def forecast_ensemble(series: pd.Series, horizon: int):
    # Fit preprocessing on this training window only; never fill from the future.
    smoothed = series.ffill().rolling(3, min_periods=1).mean()
    scaler = StandardScaler().fit(smoothed.to_numpy().reshape(-1, 1))
    values = scaler.transform(smoothed.to_numpy().reshape(-1, 1)).ravel()

    models = {
        "holt_winters": ExponentialSmoothing(
            values, trend="add", seasonal="add", seasonal_periods=24
        ),
        "arima": ARIMA(values, order=(2, 1, 1)),
        "sarima": SARIMAX(
            values, order=(1, 0, 0), seasonal_order=(1, 0, 0, 24), trend="c"
        ),
    }
    predictions = {}
    model_status = {}
    for name, model in models.items():
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                fitted = model.fit(disp=False, maxiter=60) if name == "sarima" else model.fit()
                forecast = np.asarray(fitted.forecast(horizon))
            if not np.isfinite(forecast).all():
                raise ValueError("Non-finite model output")
            predictions[name] = forecast
            model_status[name] = "fit_with_warning" if caught else "fit"
        except (ValueError, np.linalg.LinAlgError) as error:
            model_status[name] = "unavailable: " + type(error).__name__

    predictions["xgboost"] = forecast_xgboost(values, smoothed.index, horizon)
    model_status["xgboost"] = "fit"

    restored_predictions = []
    for forecast in predictions.values():
        original_scale = scaler.inverse_transform(forecast.reshape(-1, 1)).ravel()
        restored_predictions.append(np.maximum(0, original_scale))

    return np.mean(restored_predictions, axis=0), model_status
