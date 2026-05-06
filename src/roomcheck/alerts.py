"""
Plain-language alerts a person can act on.

The whole point of Room Check: a librarian, a teacher, a parent should be
able to read the alert and know what to *do*, not just what's "wrong."

We special-case three scenarios because the right action varies dramatically:
    - Smoke event (high PM2.5)  → DON'T open windows.
    - Heat danger (high temp)   → Move vulnerable occupants, hydrate.
    - High CO2 (poor venting)   → Open windows IF outdoor air is clean.

Plus an optional Community Resilience Index for buildings whose vulnerabilities
(no backup generator, aging HVAC, no purifiers) compound the risk.
"""
from __future__ import annotations
from typing import Optional, Mapping
from .core import RoomStatus, Status

SMOKE_PM25  = 35.4   # EPA AQI "Unhealthy" line for 24h
HEAT_TEMP_F = 88
HIGH_CO2    = 1200


def _params_at(status: Status, parameters: dict[str, Status]) -> list[str]:
    return [k for k, v in parameters.items() if v == status]


def alert_for(
    result: RoomStatus,
    readings: Optional[Mapping[str, Optional[float]]] = None,
) -> str:
    """Human-readable alert for a RoomStatus.

    Always returns a non-empty string. Tone scales with severity.
    """
    if readings is None:
        readings = result.readings

    pm25 = readings.get("pm25_ugm3")
    temp = readings.get("temperature_f")
    co2  = readings.get("co2_ppm")
    smoke  = pm25 is not None and pm25 > SMOKE_PM25
    heat   = temp is not None and temp > HEAT_TEMP_F
    stuffy = co2  is not None and co2  > HIGH_CO2

    overall = result.overall

    if overall == "GREEN":
        return "Air quality is good. The room is safe for all occupants. No action needed."

    if overall == "UNKNOWN":
        return "Some sensor readings are unavailable. Cannot fully assess room safety. Check sensor connections."

    if overall == "RED":
        if smoke and heat:
            return ("URGENT: Dangerous air quality AND extreme heat. "
                    "Do NOT open windows — outdoor air may contain smoke. "
                    "Move occupants to an interior room with filtered air. "
                    "Contact building management immediately.")
        if smoke:
            return ("URGENT: Air particulate levels are dangerous. "
                    "Do NOT open windows — this may be a smoke event. "
                    "Keep doors closed. Run any available air purifiers. "
                    "Contact building management now.")
        if heat:
            return ("URGENT: Temperature is dangerously high. "
                    "Move vulnerable occupants (elderly, children) to the coolest area. "
                    "Provide water. Contact building management.")
        if stuffy:
            return ("URGENT: Carbon dioxide levels are very high — poor ventilation. "
                    "Open windows and doors if outdoor air is clean. "
                    "This may indicate HVAC failure.")
        red = ", ".join(_params_at("RED", result.parameters))
        return f"URGENT: Unsafe conditions detected ({red}). Take action immediately and contact building management."

    yellow = " and ".join(_params_at("YELLOW", result.parameters)) or "some readings"
    return (f"Caution: {yellow} are outside the ideal range. "
            "Monitor closely and consider improving ventilation. "
            "Alert staff if conditions worsen.")


def resilience_index(
    result: RoomStatus,
    vulnerabilities: Optional[dict[str, dict]] = None,
) -> dict:
    """Compute a 0-100 'Community Resilience Index'.

    Starts at 100, deducts for:
      - Building vulnerabilities you provide (no_backup_generator, etc.)
      - Current YELLOW (-4 each) and RED (-10 each) parameter statuses

    Returns:
        {
          "score": 72.0,
          "band": "FRAGILE",  # or RESILIENT / AT_RISK / CRITICAL
          "breakdown": [{"cause": str, "note": str, "points": int}, ...]
        }

    Example vulnerabilities (callers define their own — these are real for
    older Maryland resilience hubs):

        {
          "no_backup_generator": {"points_deducted": 20, "note": "Building goes dark in outage."},
          "r22_chillers":        {"points_deducted": 15, "note": "Refrigerant phased out."},
        }
    """
    score = 100.0
    breakdown = []

    if vulnerabilities:
        for vuln_id, spec in vulnerabilities.items():
            d = spec.get("points_deducted", 0)
            score -= d
            breakdown.append({"cause": vuln_id, "note": spec.get("note",""), "points": -d})

    for key, value in result.parameters.items():
        if value == "RED":
            score -= 10
            breakdown.append({"cause": f"{key}=RED", "note": "Current unsafe reading", "points": -10})
        elif value == "YELLOW":
            score -= 4
            breakdown.append({"cause": f"{key}=YELLOW", "note": "Current caution reading", "points": -4})

    score = max(0.0, min(100.0, score))
    if score >= 80:
        band = "RESILIENT"
    elif score >= 60:
        band = "FRAGILE"
    elif score >= 40:
        band = "AT_RISK"
    else:
        band = "CRITICAL"

    return {"score": round(score, 1), "band": band, "breakdown": breakdown}
