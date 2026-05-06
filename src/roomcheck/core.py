"""
The core: evaluate sensor readings → GREEN / YELLOW / RED / UNKNOWN.

This is the part that translates numbers into something a human (a librarian,
a building manager, a parent) can act on. It's intentionally tiny — five
parameters, two threshold types, four possible statuses.

    from roomcheck import evaluate
    result = evaluate({"co2_ppm": 1280, "pm25_ugm3": 5, ...})
    result.overall          # "RED"
    result.parameters       # {"co2_ppm": "RED", "pm25_ugm3": "GREEN", ...}
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Mapping, Literal

from .thresholds import (
    Thresholds, DEFAULT_THRESHOLDS,
    CeilingThreshold, RangeThreshold,
)


Status = Literal["GREEN", "YELLOW", "RED", "UNKNOWN"]
ParameterStatus = dict[str, Status]

_ORDER: dict[Status, int] = {"GREEN": 0, "UNKNOWN": 1, "YELLOW": 2, "RED": 3}

# All parameters this engine knows about. Adding one means adding it to
# Thresholds and to PARAM_KINDS below.
PARAM_KINDS: dict[str, type] = {
    "co2_ppm":       CeilingThreshold,
    "pm25_ugm3":     CeilingThreshold,
    "voc_index":     CeilingThreshold,
    "temperature_f": RangeThreshold,
    "humidity_pct":  RangeThreshold,
}


@dataclass(frozen=True)
class RoomStatus:
    """The result of one evaluation."""
    overall: Status
    parameters: ParameterStatus
    readings: dict[str, Optional[float]]
    measured_count: int = 0
    unknown_count: int = 0

    @property
    def is_safe(self) -> bool:
        return self.overall == "GREEN"

    @property
    def needs_action(self) -> bool:
        return self.overall == "RED"

    def __str__(self) -> str:
        return f"<RoomStatus overall={self.overall} parameters={self.parameters}>"


def _eval_ceiling(value: Optional[float], spec: CeilingThreshold) -> Status:
    if value is None:
        return "UNKNOWN"
    if value <= spec.green_max:
        return "GREEN"
    if value <= spec.yellow_max:
        return "YELLOW"
    return "RED"


def _eval_range(value: Optional[float], spec: RangeThreshold) -> Status:
    if value is None:
        return "UNKNOWN"
    if spec.green_min <= value <= spec.green_max:
        return "GREEN"
    if spec.yellow_min <= value <= spec.yellow_max:
        return "YELLOW"
    return "RED"


def evaluate(
    readings: Mapping[str, Optional[float]],
    thresholds: Thresholds = DEFAULT_THRESHOLDS,
) -> RoomStatus:
    """Translate raw sensor values into GREEN/YELLOW/RED.

    Args:
        readings: dict of parameter → numeric value (or None if not measured).
            Recognized keys: co2_ppm, pm25_ugm3, voc_index, temperature_f, humidity_pct.
            Extra keys are ignored. Missing keys are treated as UNKNOWN.
        thresholds: a Thresholds dataclass; defaults to DEFAULT_THRESHOLDS
            (ASHRAE / EPA / OSHA / Sensirion).

    Returns:
        RoomStatus with per-parameter statuses + an overall worst-of status.

    The overall status is the WORST individual status (RED > YELLOW > UNKNOWN > GREEN).
    UNKNOWN dominates GREEN because "we don't know" is not "safe."
    """
    parameters: ParameterStatus = {}
    measured = 0
    unknown = 0

    for key in PARAM_KINDS:
        spec = getattr(thresholds, key, None)
        if spec is None:
            parameters[key] = "UNKNOWN"
            unknown += 1
            continue

        value = readings.get(key)
        if isinstance(spec, CeilingThreshold):
            status = _eval_ceiling(value, spec)
        elif isinstance(spec, RangeThreshold):
            status = _eval_range(value, spec)
        else:
            status = "UNKNOWN"

        parameters[key] = status
        if status == "UNKNOWN":
            unknown += 1
        else:
            measured += 1

    # Worst wins — including UNKNOWN > GREEN.
    overall: Status = "GREEN"
    for s in parameters.values():
        if _ORDER[s] > _ORDER[overall]:
            overall = s

    # Filter readings to known keys + preserve types.
    filtered_readings: dict[str, Optional[float]] = {
        k: (float(readings[k]) if readings.get(k) is not None else None)
        for k in PARAM_KINDS
    }

    return RoomStatus(
        overall=overall,
        parameters=parameters,
        readings=filtered_readings,
        measured_count=measured,
        unknown_count=unknown,
    )
