"""Sensor adapter base class. Every adapter implements `read()`."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional


class SensorError(Exception):
    """Raised when a sensor cannot produce a reading."""


class Sensor(ABC):
    """Plug-in interface for a reading source.

    Subclasses must:
      - set `name` (short slug, e.g., 'dyson')
      - implement `read()` returning a dict with the standard keys

    Optional:
      - implement `close()` to release resources
    """
    name: str = "unknown"

    @abstractmethod
    def read(self) -> dict:
        """Return one fresh reading.

        Schema (all keys present; missing values are None):
            {
              "co2_ppm":       float | None,
              "pm25_ugm3":     float | None,
              "temperature_f": float | None,
              "humidity_pct":  float | None,
              "voc_index":     float | None,
            }

        Adapters MAY include additional keys (timestamp, device, location, etc.)
        — they're preserved by Room Check but not used in evaluation.
        """
        ...

    def close(self) -> None:
        """Release any resources. Default: no-op."""
        return None

    def __enter__(self) -> "Sensor":
        return self

    def __exit__(self, *args) -> None:
        self.close()


def empty_reading() -> dict:
    """A blank reading dict. Useful as a starting point for adapters."""
    return {
        "co2_ppm":       None,
        "pm25_ugm3":     None,
        "temperature_f": None,
        "humidity_pct":  None,
        "voc_index":     None,
    }
