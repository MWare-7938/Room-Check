# Adding a new sensor adapter

Every sensor in Room Check is a class that inherits from `Sensor` and implements `read()`. That's it.

## Minimum example

```python
# src/roomcheck/sensors/my_sensor.py
from .base import Sensor, empty_reading

class MySensor(Sensor):
    name = "my-sensor"

    def __init__(self, host: str):
        self.host = host

    def read(self) -> dict:
        out = empty_reading()
        out["co2_ppm"] = self._fetch_co2()
        out["temperature_f"] = self._fetch_temp()
        # ...etc.
        return out

    def _fetch_co2(self):
        # whatever your sensor needs — HTTP, serial, MQTT, modbus
        ...
```

## Schema your `read()` must return

```python
{
  "co2_ppm":       float | None,
  "pm25_ugm3":     float | None,
  "temperature_f": float | None,
  "humidity_pct":  float | None,
  "voc_index":     float | None,
}
```

You may include extra keys like `timestamp`, `device`, `location`, `battery_pct` — they're preserved through the pipeline but not used in evaluation.

If your sensor doesn't measure something, **return `None`** for that key. Room Check will mark it `UNKNOWN`. Don't fake it with a zero — that would silently turn missing data into "GREEN."

## Unit conversions to know

If your sensor reports in different units than Room Check expects, convert in `read()`:

| Native | Convert to | Code |
|---|---|---|
| Celsius | Fahrenheit | `c * 9 / 5 + 32` |
| Kelvin | Fahrenheit | `(k - 273.15) * 9 / 5 + 32` |
| PM2.5 in mg/m³ | µg/m³ | `mg * 1000` |
| Decimal humidity (0.0-1.0) | percent (0-100) | `dec * 100` |

## Add it to `__init__.py`

```python
# src/roomcheck/sensors/__init__.py
from .my_sensor import MySensor
__all__.append("MySensor")
```

If your sensor needs an optional dependency (like `requests` for HTTP), wrap the import in a try/except:

```python
try:
    from .my_sensor import MySensor
    __all__.append("MySensor")
except ImportError:
    pass
```

And declare it in `pyproject.toml`:

```toml
[project.optional-dependencies]
my-sensor = ["mylib>=1.0"]
```

Then users install with `pip install 'room-check[my-sensor]'`.

## Test it

```python
# tests/test_my_sensor.py
def test_my_sensor_returns_schema(monkeypatch):
    sensor = MySensor("dummy-host")
    monkeypatch.setattr(sensor, "_fetch_co2", lambda: 650)
    out = sensor.read()
    assert out["co2_ppm"] == 650
    assert "pm25_ugm3" in out  # schema completeness
```

## Submit the PR

- Give it a single-purpose commit message: `Add MySensor adapter (PurpleAir local API)`.
- Update the sensor list in the README.
- Make sure tests pass: `pytest`.

That's the whole process. We've kept the surface area tiny on purpose — no plugin registry, no metaclass magic, no config schemas. Just `read() -> dict`.
