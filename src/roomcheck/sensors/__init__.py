"""
Sensor adapters — pluggable sources of readings.

Every sensor adapter inherits from `Sensor` and returns the same dict shape:

    {
      "co2_ppm":       float | None,
      "pm25_ugm3":     float | None,
      "temperature_f": float | None,
      "humidity_pct":  float | None,
      "voc_index":     float | None,
    }

Built-in adapters:
    InteractiveManual — prompt a human at the terminal
    InkbirdManual     — guided prompts for Inkbird IAM-O2 (CO2 + temp + humidity)
    DysonCloud        — live pull from a Dyson Pure Cool / Hot+Cool via libdyson-neon
    CSVFile           — read the last row of a CSV file
    JSONHttp          — GET an HTTP endpoint, parse JSON, map fields

Adding your own:
    from roomcheck.sensors import Sensor

    class MySensor(Sensor):
        name = "my-sensor"
        def read(self) -> dict:
            ...
"""
from .base import Sensor, SensorError
from .manual import InteractiveManual
from .inkbird_manual import InkbirdManual
from .csv_file import CSVFile

__all__ = ["Sensor", "SensorError", "InteractiveManual", "InkbirdManual", "CSVFile"]

# Optional adapters — only available if their extra is installed.
try:
    from .dyson_cloud import DysonCloud
    __all__.append("DysonCloud")
except ImportError:
    pass

try:
    from .json_http import JSONHttp
    __all__.append("JSONHttp")
except ImportError:
    pass
