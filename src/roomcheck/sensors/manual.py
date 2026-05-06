"""Generic interactive prompt — accepts any of the five parameters."""
from __future__ import annotations
from typing import Optional
from .base import Sensor, empty_reading


def _prompt_float(label: str) -> Optional[float]:
    raw = input(f"  {label} (blank = skip): ").strip()
    if not raw:
        return None
    raw_lower = raw.lower()
    # Allow "22c" → convert °C to °F
    if "(°f)" in label.lower() and raw_lower.endswith(("c", "°c")):
        try:
            c = float(raw_lower.rstrip("c").rstrip("°").strip())
            return round(c * 9 / 5 + 32, 2)
        except ValueError:
            pass
    try:
        return float(raw)
    except ValueError:
        print(f"    couldn't parse {raw!r} — skipping.")
        return None


class InteractiveManual(Sensor):
    """Prompt the user for each parameter in order. Press Enter to skip any."""
    name = "manual"

    def read(self) -> dict:
        print("\nEnter sensor readings (press Enter to skip a value):")
        out = empty_reading()
        out["co2_ppm"]       = _prompt_float("CO2 (ppm)")
        out["pm25_ugm3"]     = _prompt_float("PM2.5 (µg/m³)")
        out["temperature_f"] = _prompt_float("Temperature (°F)")
        out["humidity_pct"]  = _prompt_float("Humidity (%RH)")
        out["voc_index"]     = _prompt_float("VOC index")
        return out
