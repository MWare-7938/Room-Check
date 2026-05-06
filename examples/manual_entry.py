"""Guided manual entry for an Inkbird-style monitor."""
from roomcheck import evaluate, alert_for, resilience_index
from roomcheck.sensors import InkbirdManual

with InkbirdManual() as sensor:
    readings = sensor.read()

result = evaluate(readings)
print(f"\nOverall: {result.overall}")
print(f"Alert:   {alert_for(result, readings)}")

res = resilience_index(result)
print(f"Resilience: {res['score']}/100 ({res['band']})")
