import numpy as np

from services.delay import queue_series

HOLDOUT_HOURS = 24


def error_metrics(actual, predicted):
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    valid = np.isfinite(actual) & np.isfinite(predicted)
    if not valid.any():
        return {"mae": None, "rmse": None, "samples": 0}
    error = actual[valid] - predicted[valid]
    return {
        "mae": float(np.mean(np.abs(error))),
        "rmse": float(np.sqrt(np.mean(error ** 2))),
        "samples": int(valid.sum()),
    }


def evaluate_route(actual, predicted, measured_delays, capacity, thresholds, delay_limit):
    predicted_delays = np.array([
        row["delay_minutes"] for row in queue_series(predicted, capacity)
    ])
    measured_delays = np.asarray(measured_delays, dtype=float)
    if np.isfinite(measured_delays).any():
        delay_reference = measured_delays
        label_source = "measured"
    else:
        # This is a queue-model comparison, not measured factory performance.
        delay_reference = np.array([
            row["delay_minutes"] for row in queue_series(actual.ffill(), capacity)
        ])
        label_source = "queue_simulation"

    actual_values = actual.to_numpy()
    # Repeat the configured horizon as a policy over the 24-hour holdout.
    limits = np.resize(thresholds, len(actual_values))
    positives = (actual_values > limits) & np.isfinite(actual_values)
    detection_rate = None
    if positives.any():
        detection_rate = float(np.mean(predicted[positives] > limits[positives]))

    valid_delays = np.isfinite(delay_reference)
    predicted_bottlenecks = predicted_delays[valid_delays] > delay_limit
    actual_bottlenecks = delay_reference[valid_delays] > delay_limit
    return {
        "forecast": error_metrics(actual_values, predicted),
        "delay": error_metrics(delay_reference, predicted_delays),
        "delay_label_source": label_source,
        "threshold_breach_detection_rate": detection_rate,
        "threshold_positive_samples": int(positives.sum()),
        "bottleneck_accuracy": float(np.mean(predicted_bottlenecks == actual_bottlenecks)),
        "bottleneck_samples": int(valid_delays.sum()),
    }
