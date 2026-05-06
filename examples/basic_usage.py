"""Minimal Room Check use — call evaluate(), print the result."""
from roomcheck import evaluate, alert_for

readings = {
    "co2_ppm": 1280,
    "pm25_ugm3": 8,
    "temperature_f": 73,
    "humidity_pct": 45,
    "voc_index": 110,
}

result = evaluate(readings)
print(f"Overall: {result.overall}")
print(f"Per-parameter: {result.parameters}")
print(f"Alert: {alert_for(result, readings)}")
