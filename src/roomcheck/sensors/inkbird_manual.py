"""Guided manual entry tuned for Inkbird IAM-O2 / IAM-T1 / IAM-T2.

Inkbird's BLE protocol is proprietary and the companion app pairing is
flaky. Most reliable workflow: read the values off the screen, type them
in. This adapter shows hints + typical ranges so non-technical users can
do it confidently.
"""
from __future__ import annotations
from typing import Optional
from .base import Sensor, empty_reading


_FIELDS = [
    {"key": "co2_ppm",       "label": "CO2",         "unit": "ppm",
     "hint": "Largest number on display. Outdoor ~420; occupied 600-1000; stuffy >1200.",
     "typical": "650"},
    {"key": "temperature_f", "label": "Temperature", "unit": "°F",
     "hint": "If the Inkbird shows °C, type e.g. '22c' and we convert.",
     "typical": "72"},
    {"key": "humidity_pct",  "label": "Humidity",    "unit": "%RH",
     "hint": "Shown with a water-drop icon. Comfortable 30-60%.",
     "typical": "45"},
]


def _prompt(field: dict) -> Optional[float]:
    prompt = f"  {field['label']} ({field['unit']}) [{field['typical']}]: "
    hinted = False
    while True:
        raw = input(prompt).strip()
        if not raw and not hinted:
            print(f"    hint: {field['hint']}")
            hinted = True
            continue
        if not raw:
            return None
        raw_lower = raw.lower()
        if field["key"] == "temperature_f" and raw_lower.endswith(("c", "°c")):
            try:
                c = float(raw_lower.rstrip("c").rstrip("°").strip())
                f = round(c * 9 / 5 + 32, 2)
                print(f"    converted {c}°C → {f}°F")
                return f
            except ValueError:
                pass
        try:
            return float(raw)
        except ValueError:
            print(f"    couldn't parse {raw!r}; try again or press Enter to skip.")


class InkbirdManual(Sensor):
    """Walk a user through entering Inkbird IAM-* values. PM2.5 + VOC stay None."""
    name = "inkbird-manual"

    def read(self) -> dict:
        print()
        print("=" * 60)
        print(" INKBIRD — Manual Entry")
        print("=" * 60)
        print(" Read three numbers off your Inkbird and type each one.")
        print(" Inkbird IAM-O2 / IAM-T1 don't measure PM2.5 or VOC —")
        print(" those will show as UNKNOWN. That's accurate.")
        print("-" * 60)
        out = empty_reading()
        for field in _FIELDS:
            out[field["key"]] = _prompt(field)
        return out
