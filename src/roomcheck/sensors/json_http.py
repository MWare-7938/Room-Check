"""Generic HTTP/JSON adapter — works with any sensor that exposes a JSON endpoint.

Examples this can talk to with a small `field_map`:
    - PurpleAir local API:    http://<sensor-ip>/json
    - Awair Element local:    http://<sensor-ip>:80/air-data/latest
    - Home Assistant entity:  http://<ha-ip>:8123/api/states/sensor.<id>
    - Custom IoT endpoints
"""
from __future__ import annotations
from typing import Optional
from .base import Sensor, SensorError, empty_reading


class JSONHttp(Sensor):
    """GET an HTTP endpoint, parse JSON, map fields → standard Room Check schema.

    Args:
        url: GET endpoint that returns JSON.
        field_map: dict mapping Room Check keys to JSON paths in the response.
            Use dot-notation for nested fields. Values can be Python expressions
            evaluated on the looked-up value (e.g., "x * 9/5 + 32" for °C → °F).
        headers: optional auth headers (e.g., bearer token).
        timeout: HTTP timeout in seconds.

    Example with an Awair Element local API:

        sensor = JSONHttp(
            url="http://192.168.1.50/air-data/latest",
            field_map={
                "co2_ppm":       "co2",
                "pm25_ugm3":     "pm25",
                "voc_index":     "voc",
                "temperature_f": "temp * 9/5 + 32",   # Awair reports °C
                "humidity_pct":  "humid",
            },
        )
    """
    name = "http"

    def __init__(
        self,
        url: str,
        field_map: dict[str, str],
        headers: Optional[dict] = None,
        timeout: float = 10.0,
    ):
        try:
            import requests
        except ImportError as exc:
            raise SensorError(
                "requests not installed. Run: pip install 'room-check[http]'"
            ) from exc
        self._requests = requests
        self.url = url
        self.field_map = field_map
        self.headers = headers or {}
        self.timeout = timeout

    def _lookup(self, payload, path: str):
        """Resolve a possibly-nested path or simple expression."""
        path = path.strip()
        # Simple arithmetic on a single field — eval in a tiny sandbox
        if any(op in path for op in (" * ", " / ", " + ", " - ", " ** ")):
            tokens = path.replace("(", " ( ").replace(")", " ) ").split()
            keys = [t for t in tokens if t.replace(".", "").replace("_", "").isalnum() and not t.isdigit()]
            ctx = {}
            for k in keys:
                ctx[k] = self._dotwalk(payload, k)
            try:
                return float(eval(path, {"__builtins__": {}}, ctx))  # noqa: S307
            except Exception:
                return None
        return self._dotwalk(payload, path)

    def _dotwalk(self, payload, path: str):
        cur = payload
        for part in path.split("."):
            if cur is None:
                return None
            if isinstance(cur, dict):
                cur = cur.get(part)
            else:
                return None
        try:
            return float(cur) if cur is not None else None
        except (TypeError, ValueError):
            return None

    def read(self) -> dict:
        try:
            resp = self._requests.get(self.url, headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            payload = resp.json()
        except Exception as exc:
            raise SensorError(f"HTTP read failed: {exc}") from exc

        out = empty_reading()
        for std, path in self.field_map.items():
            if std in out:
                out[std] = self._lookup(payload, path)
        return out
