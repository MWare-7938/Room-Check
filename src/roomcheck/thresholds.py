"""
Default safety thresholds for indoor air-quality parameters.

Every value here cites a published standard. If you change one, change the
citation. Default thresholds are conservative — they err on the side of
flagging YELLOW earlier rather than later, because false positives are far
cheaper than missed exposures.

Standards used:
    CO2          — ASHRAE Standard 62.1-2022, Appendix D (ventilation)
    PM2.5        — EPA AQI breakpoints, 40 CFR Part 58 Appendix G (24-hr avg)
    Temperature  — OSHA Technical Manual III.2 + ASHRAE 55 comfort zone
    Humidity     — ASHRAE 55-2020 thermal environmental conditions
    VOC          — Sensirion VOC Index whitepaper (baseline 100)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class CeilingThreshold:
    """A 'lower-is-better' parameter (CO2, PM2.5, VOC)."""
    green_max: float
    yellow_max: float
    unit: str
    source: str
    green_meaning: str
    yellow_meaning: str
    red_meaning: str


@dataclass(frozen=True)
class RangeThreshold:
    """A 'comfort range' parameter (temperature, humidity)."""
    green_min: float
    green_max: float
    yellow_min: float
    yellow_max: float
    unit: str
    source: str
    green_meaning: str
    yellow_meaning: str
    red_meaning: str


@dataclass(frozen=True)
class Thresholds:
    """A complete set of thresholds, one per parameter.

    Use the module-level DEFAULT_THRESHOLDS for ASHRAE/EPA/OSHA defaults,
    or construct your own to override any parameter.
    """
    co2_ppm:       Optional[CeilingThreshold] = None
    pm25_ugm3:     Optional[CeilingThreshold] = None
    voc_index:     Optional[CeilingThreshold] = None
    temperature_f: Optional[RangeThreshold]   = None
    humidity_pct:  Optional[RangeThreshold]   = None


DEFAULT_THRESHOLDS = Thresholds(
    co2_ppm=CeilingThreshold(
        green_max=800, yellow_max=1200, unit="ppm",
        source="ASHRAE Standard 62.1-2022, Appendix D",
        green_meaning="Fresh air, good ventilation. Safe for all occupants.",
        yellow_meaning="Slightly elevated. Increase ventilation; monitor.",
        red_meaning="Poor air quality. Occupants may feel drowsy. Ventilate immediately.",
    ),
    pm25_ugm3=CeilingThreshold(
        green_max=12, yellow_max=35.4, unit="µg/m³",
        source="EPA AQI breakpoints for PM2.5, 40 CFR Part 58 Appendix G",
        green_meaning="Good air quality. No particulate health risk.",
        yellow_meaning="Moderate. Sensitive groups (asthma, heart disease) may be affected.",
        red_meaning="Unhealthy. Keep windows CLOSED during smoke events.",
    ),
    voc_index=CeilingThreshold(
        green_max=150, yellow_max=350, unit="index (0-500)",
        source="Sensirion VOC Index whitepaper (baseline 100)",
        green_meaning="Normal air composition.",
        yellow_meaning="Elevated VOCs. Check for cleaning products or off-gassing.",
        red_meaning="High VOC levels. Ventilate and investigate source.",
    ),
    temperature_f=RangeThreshold(
        green_min=65, green_max=80,
        yellow_min=60, yellow_max=88,
        unit="°F",
        source="OSHA Technical Manual III.2; ASHRAE 55 comfort zone",
        green_meaning="Comfortable temperature for most occupants.",
        yellow_meaning="Outside comfort zone. Monitor elderly and children.",
        red_meaning="Dangerous. Risk of heat stress or hypothermia.",
    ),
    humidity_pct=RangeThreshold(
        green_min=30, green_max=60,
        yellow_min=20, yellow_max=70,
        unit="%RH",
        source="ASHRAE Standard 55-2020 thermal environmental conditions",
        green_meaning="Comfortable humidity.",
        yellow_meaning="Outside ideal range. Dry irritates airways; humid encourages mold.",
        red_meaning="Dangerous. Mold risk above 70%, respiratory irritation below 20%.",
    ),
)
