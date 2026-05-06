"""Core engine tests — the GREEN/YELLOW/RED translator."""
import pytest
from roomcheck import evaluate, DEFAULT_THRESHOLDS


def test_all_green():
    r = evaluate({"co2_ppm": 500, "pm25_ugm3": 5, "temperature_f": 72,
                  "humidity_pct": 45, "voc_index": 80})
    assert r.overall == "GREEN"
    assert all(v == "GREEN" for v in r.parameters.values())
    assert r.is_safe


def test_smoke_is_red():
    r = evaluate({"co2_ppm": 500, "pm25_ugm3": 89, "temperature_f": 72,
                  "humidity_pct": 45, "voc_index": 80})
    assert r.overall == "RED"
    assert r.parameters["pm25_ugm3"] == "RED"
    assert r.needs_action


def test_worst_wins():
    r = evaluate({"co2_ppm": 700, "pm25_ugm3": 5, "temperature_f": 95,
                  "humidity_pct": 45, "voc_index": 80})
    assert r.overall == "RED"  # one bad parameter forces RED


def test_unknown_when_missing():
    r = evaluate({"pm25_ugm3": 5, "temperature_f": 72,
                  "humidity_pct": 45, "voc_index": 80})  # no CO2
    assert r.parameters["co2_ppm"] == "UNKNOWN"
    # Single UNKNOWN with everything else GREEN bubbles up to UNKNOWN
    assert r.overall == "UNKNOWN"


def test_yellow_co2():
    r = evaluate({"co2_ppm": 1000, "pm25_ugm3": 5, "temperature_f": 72,
                  "humidity_pct": 45, "voc_index": 80})
    assert r.parameters["co2_ppm"] == "YELLOW"
    assert r.overall == "YELLOW"


def test_temperature_range_low():
    r = evaluate({"co2_ppm": 500, "pm25_ugm3": 5, "temperature_f": 50,
                  "humidity_pct": 45, "voc_index": 80})
    assert r.parameters["temperature_f"] == "RED"


def test_humidity_mold_risk():
    r = evaluate({"co2_ppm": 500, "pm25_ugm3": 5, "temperature_f": 72,
                  "humidity_pct": 75, "voc_index": 80})
    assert r.parameters["humidity_pct"] == "RED"


def test_extra_keys_ignored():
    r = evaluate({"co2_ppm": 500, "pm25_ugm3": 5, "temperature_f": 72,
                  "humidity_pct": 45, "voc_index": 80,
                  "co_ppm": 999, "noise_db": 60})
    assert r.overall == "GREEN"


def test_readings_preserved():
    r = evaluate({"co2_ppm": 500, "pm25_ugm3": 5, "temperature_f": 72,
                  "humidity_pct": 45, "voc_index": 80})
    assert r.readings["co2_ppm"] == 500.0
    assert r.readings["pm25_ugm3"] == 5.0


def test_count_measured_unknown():
    r = evaluate({"co2_ppm": 500, "pm25_ugm3": None, "temperature_f": 72,
                  "humidity_pct": 45, "voc_index": None})
    assert r.measured_count == 3
    assert r.unknown_count == 2
