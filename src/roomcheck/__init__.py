"""
Room Check — turn raw indoor air-quality numbers into easy GREEN/YELLOW/RED calls.

Quickstart:

    from roomcheck import evaluate, alert_for, DEFAULT_THRESHOLDS

    readings = {
        "co2_ppm": 1280,
        "pm25_ugm3": 18,
        "temperature_f": 79,
        "humidity_pct": 55,
        "voc_index": 200,
    }
    result = evaluate(readings)
    print(result.overall)              # "RED"
    print(alert_for(result, readings)) # "URGENT: Carbon dioxide levels are very high..."
"""

from .core import evaluate, Status, ParameterStatus, RoomStatus
from .thresholds import DEFAULT_THRESHOLDS, Thresholds
from .alerts import alert_for, resilience_index

__all__ = [
    "evaluate",
    "Status",
    "ParameterStatus",
    "RoomStatus",
    "DEFAULT_THRESHOLDS",
    "Thresholds",
    "alert_for",
    "resilience_index",
]

__version__ = "1.0.0"
