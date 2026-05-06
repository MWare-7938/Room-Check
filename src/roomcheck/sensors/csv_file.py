"""CSV-file adapter — reads the LAST row of a CSV.

Expected columns (any subset is fine; missing columns become None):
    timestamp, co2_ppm, pm25_ugm3, temperature_f, humidity_pct, voc_index

If your CSV uses different column names, pass `column_map` to translate:

    CSVFile("mydata.csv", column_map={
        "co2_ppm": "CO2 (ppm)",
        "temperature_f": "Temp °F",
    })
"""
from __future__ import annotations
import csv
from pathlib import Path
from typing import Optional
from .base import Sensor, SensorError, empty_reading


class CSVFile(Sensor):
    """Adapter: pull readings from a CSV file."""
    name = "csv"

    def __init__(self, path: str | Path, column_map: Optional[dict[str, str]] = None):
        self.path = Path(path)
        self.column_map = column_map or {}

    def _resolve(self, std_key: str) -> str:
        return self.column_map.get(std_key, std_key)

    def read(self) -> dict:
        if not self.path.exists():
            raise SensorError(f"CSV file not found: {self.path}")
        with open(self.path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            raise SensorError(f"CSV is empty: {self.path}")
        last = rows[-1]
        out = empty_reading()
        for std in out:
            col = self._resolve(std)
            v = last.get(col)
            if v in (None, ""):
                continue
            try:
                out[std] = float(v)
            except ValueError:
                out[std] = None
        # Preserve a timestamp if present
        for ts_col in (self._resolve("timestamp"), "timestamp", "time", "Date Time"):
            if ts_col in last:
                out["timestamp"] = last[ts_col]
                break
        return out
