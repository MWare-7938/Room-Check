"""Override default thresholds — schools, hospitals, and homes need different limits."""
from dataclasses import replace
from roomcheck import evaluate, alert_for, DEFAULT_THRESHOLDS
from roomcheck.thresholds import CeilingThreshold

# A school is stricter than an office because kids are still developing
# respiratory systems and 30 of them in one room produce CO2 fast.
SCHOOL_THRESHOLDS = replace(DEFAULT_THRESHOLDS, co2_ppm=CeilingThreshold(
    green_max=600, yellow_max=900, unit="ppm",
    source="WHO indoor air quality guidelines for schools",
    green_meaning="Good ventilation for student learning",
    yellow_meaning="Increase ventilation; consider opening doors/windows",
    red_meaning="Take students outside or to better-ventilated room",
))

readings = {"co2_ppm": 750, "pm25_ugm3": 8, "temperature_f": 72,
            "humidity_pct": 45, "voc_index": 100}

# Same readings, two thresholds:
office  = evaluate(readings, thresholds=DEFAULT_THRESHOLDS)
school  = evaluate(readings, thresholds=SCHOOL_THRESHOLDS)

print(f"Office context: CO2 {readings['co2_ppm']} ppm → {office.parameters['co2_ppm']}")
print(f"School context: CO2 {readings['co2_ppm']} ppm → {school.parameters['co2_ppm']}")
print()
print(f"Office alert: {alert_for(office, readings)}")
print(f"School alert: {alert_for(school, readings)}")
