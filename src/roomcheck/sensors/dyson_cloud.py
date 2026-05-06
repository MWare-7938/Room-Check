"""Dyson Pure Cool / Hot+Cool live adapter.

Uses libdyson-neon (`pip install room-check[dyson]`) to talk to the Dyson
on the local network. Auto-discovers via mDNS or you can pass a host IP.

One-time setup outside this adapter:
    1. pip install libdyson-neon
    2. Run a `--login` CLI flow to get device serial + credential
       (see `room-check login` or examples/dyson_login.py)
    3. Save serial + credential + product_type somewhere

Then:
    from roomcheck.sensors import DysonCloud
    sensor = DysonCloud(serial="...", credential="...", product_type="438")
    print(sensor.read())

Notes:
  * Dyson Pure Cool / Hot+Cool does NOT measure CO2.
  * Temperature comes in mixed formats (Kelvin, K×10, or °C). Auto-detected.
  * VOC is on Dyson's 0-9 scale; we floor + scale ×50 → Sensirion 0-500.
"""
from __future__ import annotations
import asyncio
import time
from typing import Optional
from .base import Sensor, SensorError, empty_reading


def _libdyson():
    try:
        import libdyson  # noqa: F401
        from libdyson import get_device
    except ImportError as exc:
        raise SensorError(
            "libdyson-neon not installed. Run: pip install 'room-check[dyson]'"
        ) from exc

    DysonAccount = None
    for path in ("libdyson.cloud.account", "libdyson.cloud", "libdyson"):
        try:
            mod = __import__(path, fromlist=["DysonAccount"])
            DysonAccount = getattr(mod, "DysonAccount", None)
            if DysonAccount:
                break
        except ImportError:
            continue
    return DysonAccount, get_device


def _temp_to_f(raw) -> Optional[float]:
    """Auto-detect Dyson's temperature format by magnitude."""
    try:
        raw = float(raw)
    except (TypeError, ValueError):
        return None
    if raw > 1000:
        k = raw / 10.0
    elif raw > 100:
        k = raw
    else:
        k = raw + 273.15
    return round((k - 273.15) * 9 / 5 + 32, 2)


def _num(val) -> Optional[float]:
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


class DysonCloud(Sensor):
    """Dyson Pure Cool / Hot+Cool adapter (local LAN, mDNS-discovered)."""
    name = "dyson"

    def __init__(self, serial: str, credential: str, product_type: str,
                 host: Optional[str] = None, discover_timeout: float = 10.0):
        self.serial = serial
        self.credential = credential
        self.product_type = product_type
        self.host = host
        self.discover_timeout = discover_timeout
        self._device = None

    def _connect(self) -> None:
        _, get_device = _libdyson()
        device = get_device(self.serial, self.credential, self.product_type)
        host = self.host
        if not host:
            host = self._discover_host(device)
            if not host:
                raise SensorError(
                    "Could not discover Dyson on local network. "
                    "Pass host=... or ensure laptop is on the same WiFi as the Dyson."
                )
        device.connect(host)
        self._device = device

    def _discover_host(self, device) -> Optional[str]:
        try:
            from libdyson.discovery import DysonDiscovery
        except ImportError:
            return None
        found = {}
        def _cb(address):
            if address and "host" not in found:
                found["host"] = address
        discovery = DysonDiscovery()
        discovery.start_discovery()
        try:
            discovery.register_device(device, _cb)
            start = time.time()
            while time.time() - start < self.discover_timeout:
                if "host" in found:
                    break
                time.sleep(0.2)
        finally:
            try: discovery.stop_discovery()
            except Exception: pass
        return found.get("host")

    def _env(self) -> dict:
        if self._device is None:
            self._connect()
        env = getattr(self._device, "environmental_data", None)
        if env:
            return env
        # Fall back to attribute scraping for older lib versions
        out = {}
        for std, attrs in {
            "particulate_matter_2_5": ("particulate_matter_2_5", "pm2_5", "pm25"),
            "volatile_organic_compounds": ("volatile_organic_compounds", "voc", "va10"),
            "humidity": ("humidity", "hact"),
            "temperature": ("temperature", "tact"),
        }.items():
            for a in attrs:
                v = getattr(self._device, a, None)
                if v is not None:
                    out[std] = v
                    break
        return out

    def read(self) -> dict:
        env = self._env()
        voc_raw = _num(env.get("volatile_organic_compounds"))
        voc_floor = max(0, int(voc_raw)) if voc_raw is not None else 0

        out = empty_reading()
        out["co2_ppm"]       = None  # not measured by Pure Cool family
        out["pm25_ugm3"]     = _num(env.get("particulate_matter_2_5"))
        out["temperature_f"] = _temp_to_f(env.get("temperature"))
        out["humidity_pct"]  = _num(env.get("humidity"))
        out["voc_index"]     = voc_floor * 50  # 0-9 → 0-450 (Sensirion-aligned)
        out["device"] = f"dyson:{self.serial}"
        return out

    def close(self) -> None:
        if self._device is not None:
            for attr in ("disconnect", "close"):
                if hasattr(self._device, attr):
                    try: getattr(self._device, attr)()
                    except Exception: pass
                    break
            self._device = None
