# Room Check

> **Turn raw indoor air-quality numbers into a clear GREEN, YELLOW, or RED safety call** — backed by published standards (ASHRAE, EPA, OSHA, Sensirion), with plain-language alerts a librarian, parent, or building manager can act on.

[![Tests](https://github.com/YOUR-ORG/room-check/actions/workflows/test.yml/badge.svg)](https://github.com/YOUR-ORG/room-check/actions)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Sensors](https://img.shields.io/badge/sensors-Dyson%20%7C%20Inkbird%20%7C%20CSV%20%7C%20HTTP-orange)

---

## Why this exists

A $25 sensor can tell you "1280 ppm CO₂." It cannot tell you what to *do* about it.

Room Check is the translation layer. You hand it readings; it hands back:

```
============================================================
 ROOM CHECK  [ UNSAFE ]
============================================================
  co2_ppm           1280     [RED]
  pm25_ugm3            8.0   [GREEN]
  temperature_f       73.0   [GREEN]
  humidity_pct        45.0   [GREEN]
  voc_index          110.0   [GREEN]
------------------------------------------------------------
  ALERT: URGENT: Carbon dioxide levels are very high — poor
         ventilation. Open windows and doors if outdoor air
         is clean. This may indicate HVAC failure.
============================================================
```

That's the whole product. No dashboards to log into. No machine-learning. No vendor lock-in. Just **numbers in → action out.**

Built originally for **Montgomery County Library** as part of GridHack 2026 — a 104,634 sq ft resilience hub with 436 daily visitors, no backup generator, and 1994-vintage HVAC. The library can't afford a $50,000 building-management system. They can run this on a laptop.

---

## 60-second install + demo

```bash
pip install room-check
roomcheck --scenario smoke_event
```

That's it. You'll see Room Check render a RED panel with the alert *"Do NOT open windows — this may be a smoke event."*

For real readings:

```bash
# Type values from any monitor's display
roomcheck

# Or for an Inkbird IAM-O2 / IAM-T1 / IAM-T2 (guided prompts)
roomcheck --inkbird

# Or for a Dyson (live)
pip install 'room-check[dyson]'
# (one-time setup writes ~/.dyson-auth.json)
roomcheck --csv dyson_live.csv --watch --interval 30
```

---

## What it measures (and what it doesn't)

Room Check evaluates **5 parameters** that cover ~90% of indoor air-quality concerns:

| Parameter | Standard | GREEN | YELLOW | RED |
|---|---|---|---|---|
| **CO₂** (ppm) | ASHRAE 62.1 | ≤ 800 | ≤ 1200 | > 1200 |
| **PM2.5** (µg/m³) | EPA AQI | ≤ 12 | ≤ 35.4 | > 35.4 |
| **Temperature** (°F) | OSHA / ASHRAE 55 | 65–80 | 60–88 | outside |
| **Humidity** (%RH) | ASHRAE 55 | 30–60 | 20–70 | outside |
| **VOC index** (0-500) | Sensirion | ≤ 150 | ≤ 350 | > 350 |

The overall status is the **worst** of any parameter — one RED parameter forces a RED room. Missing measurements come back as `UNKNOWN`, never silently treated as safe.

Need different thresholds for your building? Override them in 4 lines of code (see [Custom thresholds](#custom-thresholds)).

---

## Why the alerts matter more than the numbers

Most air-quality tools tell you what's wrong. Room Check tells you what to **do**:

| Situation | What Room Check says |
|---|---|
| Wildfire smoke | *"Do NOT open windows. Run air purifiers. Contact building management."* |
| Extreme heat | *"Move vulnerable occupants (elderly, children) to the coolest area. Provide water."* |
| High CO₂ | *"Open windows IF outdoor air is clean. May indicate HVAC failure."* |
| Smoke + heat together | *"Do NOT open windows. Move to interior room with filtered air."* (the trickiest case) |

Every alert is actionable. Every alert is in plain English. No stack trace, no AQI math, no "consult an expert."

---

## Sensors supported out of the box

Room Check is **sensor-agnostic** — adapters live in `roomcheck.sensors`:

| Adapter | Source | Install |
|---|---|---|
| `InteractiveManual` | Type values at the terminal | built-in |
| `InkbirdManual` | Guided prompts for Inkbird IAM-* (CO₂ + temp + humidity) | built-in |
| `CSVFile` | Last row of any CSV (with optional column-name remap) | built-in |
| `DysonCloud` | Live pull from Dyson Pure Cool / Hot+Cool via mDNS | `pip install 'room-check[dyson]'` |
| `JSONHttp` | Any HTTP/JSON endpoint (PurpleAir, Awair, Home Assistant, custom IoT) | `pip install 'room-check[http]'` |

**Adding a new sensor takes ~30 lines of code.** Subclass `Sensor`, implement `read()`, return a dict in the standard schema. See [docs/adding_sensors.md](docs/adding_sensors.md).

---

## Use it as a Python library

```python
from roomcheck import evaluate, alert_for, resilience_index

readings = {
    "co2_ppm": 1280,
    "pm25_ugm3": 8,
    "temperature_f": 73,
    "humidity_pct": 45,
    "voc_index": 110,
}

result = evaluate(readings)
print(result.overall)              # 'RED'
print(result.parameters)           # {'co2_ppm': 'RED', ...}
print(alert_for(result, readings)) # 'URGENT: Carbon dioxide levels...'

if result.needs_action:
    # Send a Slack alert, a text message, an email, whatever
    notify_team(alert_for(result, readings))
```

---

## Use it from the command line

```bash
# One-shot
roomcheck --scenario heat_wave           # canned scenario
roomcheck --csv my_log.csv               # from a CSV
roomcheck --inkbird                      # guided manual entry

# Continuous
roomcheck --scenario smoke_event --watch --interval 30

# Machine-readable for scripts / dashboards
roomcheck --scenario heat_wave --json | jq .alert
```

**Exit code encodes the status:** `0` GREEN, `1` YELLOW, `2` RED, `3` UNKNOWN. So you can chain Room Check into cron, CI, alerting pipelines, anywhere a 0/non-zero exit matters:

```bash
# Cron: run every 5 minutes; if RED, send a text
*/5 * * * * roomcheck --csv /var/log/sensor.csv --json > /tmp/rc.json || sms-alert "$(jq -r .alert /tmp/rc.json)"
```

---

## Custom thresholds

Override any parameter:

```python
from roomcheck import evaluate, DEFAULT_THRESHOLDS
from roomcheck.thresholds import Thresholds, CeilingThreshold
from dataclasses import replace

# Stricter CO2 limits for a school
strict = replace(DEFAULT_THRESHOLDS, co2_ppm=CeilingThreshold(
    green_max=600, yellow_max=900, unit="ppm",
    source="WHO indoor air quality guidelines (school)",
    green_meaning="Good ventilation",
    yellow_meaning="Increase ventilation now",
    red_meaning="Evacuate to outdoor space if possible",
))

evaluate(readings, thresholds=strict)
```

---

## Resilience Index (optional)

For buildings with known vulnerabilities, Room Check can compute a 0-100 *Community Resilience Index* that combines current air quality with structural risk:

```python
from roomcheck import evaluate, resilience_index

result = evaluate(readings)
score = resilience_index(result, vulnerabilities={
    "no_backup_generator":  {"points_deducted": 20, "note": "Building goes dark in outage."},
    "r22_chillers":         {"points_deducted": 15, "note": "Refrigerant phased out."},
    "no_air_purifiers":     {"points_deducted": 10, "note": "Nothing to scrub smoke."},
})
# {'score': 65.0, 'band': 'FRAGILE', 'breakdown': [...]}
```

Useful for grant narratives, capital-planning conversations, and anyone who needs to argue "this building deserves a generator before the next heat wave."

---

## Examples

See [`examples/`](examples/):

- [`basic_usage.py`](examples/basic_usage.py) — minimal Python use
- [`live_dyson.py`](examples/live_dyson.py) — pull from a Dyson every 30 seconds
- [`manual_entry.py`](examples/manual_entry.py) — guided manual entry
- [`custom_thresholds.py`](examples/custom_thresholds.py) — schools / hospitals / homes
- [`scheduled_alerts.py`](examples/scheduled_alerts.py) — cron-style monitoring with email + SMS

---

## Testing

```bash
pip install -e ".[dev]"
pytest
```

23 tests covering core evaluation logic, alert messages, resilience index, and sensor adapters. CI runs on Linux, macOS, and Windows × Python 3.10/3.11/3.12 on every push.

---

## Roadmap

- [ ] Web dashboard adapter (Grafana plugin, Home Assistant integration)
- [ ] More sensor adapters: Awair, Atmotube, Airthings, AirGradient, Sensirion SCD30 (USB)
- [ ] Localization (Spanish first — most impactful for Maryland libraries)
- [ ] Alerts via Twilio, Slack, Discord, email out of the box
- [ ] Multi-room aggregation
- [ ] BAS / Modbus integration for commercial buildings

PRs welcome on any of these.

---

## Contributing

This started as a hackathon project. It works because real librarians and building managers use it. Keep that spirit:

1. Fork → branch → PR.
2. Add a test for any new logic.
3. Cite a real published standard for any new threshold.
4. Plain-language alerts only — no jargon.

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup details.

---

## License

[MIT](LICENSE). Use it in your library, your school, your home, your commercial product. Modify it, fork it, sell it.

If you ship Room Check in production, we'd love to hear about it — open an issue with `[Used in production]` in the title and tell us what building it's protecting.

---

## Citation

If you use Room Check in research, civic publications, or grant applications:

```
Room Check: Open-source indoor air-quality safety translator.
https://github.com/YOUR-ORG/room-check
Originally developed for Montgomery County Library, GridHack 2026.
```

---

## A note on what this is NOT

- **Not a sensor.** You bring the hardware (or a CSV).
- **Not a dashboard.** You bring the UI (or use the CLI).
- **Not medical advice.** It's a translator. A nurse, a doctor, an HVAC tech, or a building engineer makes the final call.
- **Not certified.** No FCC, no CE, no FDA. It's MIT-licensed software that reads numbers.

Room Check is meant to be the boring, reliable middle layer between "I have a sensor reading" and "what should I do." Everything else — the hardware, the dashboards, the medical judgment — is someone else's job.

That's the point.
