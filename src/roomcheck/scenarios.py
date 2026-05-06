"""Built-in test scenarios — useful for demos, judging, training, and CI."""
from __future__ import annotations

SCENARIOS: dict[str, dict] = {
    "normal": {
        "description": "Baseline: occupied building, all systems nominal.",
        "readings": {"co2_ppm": 620, "pm25_ugm3": 8.2, "temperature_f": 72.4, "humidity_pct": 44, "voc_index": 95},
    },
    "stuffy_room": {
        "description": "Crowded meeting room, ventilation can't keep up.",
        "readings": {"co2_ppm": 1050, "pm25_ugm3": 10.1, "temperature_f": 76.8, "humidity_pct": 52, "voc_index": 130},
    },
    "ventilation_failure": {
        "description": "HVAC stopped working — CO2 climbing, temp drifting up.",
        "readings": {"co2_ppm": 1480, "pm25_ugm3": 14.3, "temperature_f": 79.2, "humidity_pct": 58, "voc_index": 180},
    },
    "heat_wave": {
        "description": "Outdoor 105°F. Cooling failing.",
        "readings": {"co2_ppm": 720, "pm25_ugm3": 9.0, "temperature_f": 87.3, "humidity_pct": 72, "voc_index": 110},
    },
    "smoke_event": {
        "description": "Wildfire smoke. CRITICAL: do not open windows.",
        "readings": {"co2_ppm": 690, "pm25_ugm3": 89.4, "temperature_f": 73.1, "humidity_pct": 38, "voc_index": 280},
    },
    "power_outage": {
        "description": "No generator. CO2 building, temp climbing.",
        "readings": {"co2_ppm": 1320, "pm25_ugm3": 18.5, "temperature_f": 84.1, "humidity_pct": 63, "voc_index": 210},
    },
    "combined_emergency": {
        "description": "Heat wave + wildfire smoke + HVAC failure. Worst case.",
        "readings": {"co2_ppm": 1850, "pm25_ugm3": 156.2, "temperature_f": 96.4, "humidity_pct": 78, "voc_index": 420},
    },
}
