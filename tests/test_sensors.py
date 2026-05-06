"""Sensor adapter tests."""
import csv
from pathlib import Path
import pytest

from roomcheck.sensors import CSVFile
from roomcheck.sensors.base import empty_reading


def test_csv_reads_last_row(tmp_path: Path):
    p = tmp_path / "log.csv"
    p.write_text(
        "timestamp,co2_ppm,pm25_ugm3,temperature_f,humidity_pct,voc_index\n"
        "2026-04-24T10:00:00,500,5.0,70,40,80\n"
        "2026-04-24T10:05:00,1234,12.3,74.5,48,150\n"
    )
    out = CSVFile(p).read()
    assert out["co2_ppm"] == 1234.0
    assert out["temperature_f"] == 74.5
    assert out["timestamp"] == "2026-04-24T10:05:00"


def test_csv_handles_missing_columns(tmp_path: Path):
    p = tmp_path / "partial.csv"
    p.write_text("timestamp,co2_ppm\n2026-04-24T10:00:00,650\n")
    out = CSVFile(p).read()
    assert out["co2_ppm"] == 650.0
    assert out["pm25_ugm3"] is None


def test_csv_with_column_map(tmp_path: Path):
    p = tmp_path / "weird.csv"
    p.write_text("Time,CO2 (ppm),Temp °F\n2026-04-24T10:00:00,725,71.2\n")
    out = CSVFile(p, column_map={
        "timestamp": "Time",
        "co2_ppm": "CO2 (ppm)",
        "temperature_f": "Temp °F",
    }).read()
    assert out["co2_ppm"] == 725.0
    assert out["temperature_f"] == 71.2


def test_csv_missing_file_raises(tmp_path: Path):
    from roomcheck.sensors import SensorError
    with pytest.raises(SensorError):
        CSVFile(tmp_path / "does-not-exist.csv").read()


def test_empty_reading_shape():
    e = empty_reading()
    expected = {"co2_ppm", "pm25_ugm3", "temperature_f", "humidity_pct", "voc_index"}
    assert set(e.keys()) == expected
    assert all(v is None for v in e.values())
