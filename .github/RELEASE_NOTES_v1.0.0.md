# Room Check v1.0.0 — First Public Release

> **Tell a librarian, teacher, or building manager what to *do* about air quality — not just what's wrong.**

A $25 sensor reports "CO₂ 1280 ppm." Room Check translates that into:

```
[ UNSAFE ]
URGENT: Carbon dioxide levels are very high — poor ventilation.
Open windows and doors if outdoor air is clean.
This may indicate HVAC failure.
```

That's the whole product. No dashboard, no machine learning, no vendor lock-in. Numbers in → action out.

---

## What's in 1.0.0

### Core

- **`evaluate()`** — translates sensor readings into GREEN / YELLOW / RED / UNKNOWN per parameter, with a worst-of overall status.
- **5 parameters** with default thresholds backed by real published standards: CO₂ (ASHRAE 62.1), PM2.5 (EPA AQI), temperature (OSHA + ASHRAE 55), humidity (ASHRAE 55), VOC (Sensirion VOC Index).
- **Plain-language alerts** with smart special-cases for smoke events, heat danger, and high CO₂. The smoke-event alert ("do NOT open windows") is the one that matters most — and it's the one most simple thresholding tools get backwards.
- **Optional Community Resilience Index** (0–100) for buildings with known structural vulnerabilities like no backup generator or aging HVAC.
- **Configurable thresholds** — override defaults in 4 lines of code (see `examples/custom_thresholds.py`). Useful for schools, hospitals, daycares, server rooms.

### Sensor adapters

Plug-and-play, all returning the same standard schema:

- **`InteractiveManual`** — type values at the terminal
- **`InkbirdManual`** — guided prompts for Inkbird IAM-O2 / IAM-T1 / IAM-T2
- **`CSVFile`** — last row of any CSV, with optional column-name remap
- **`DysonCloud`** — live pull from Dyson Pure Cool / Hot+Cool via mDNS (`pip install 'room-check[dyson]'`)
- **`JSONHttp`** — any HTTP/JSON endpoint: PurpleAir, Awair, Home Assistant, custom IoT (`pip install 'room-check[http]'`)

Adding a new sensor takes ~30 lines of code. See `docs/adding_sensors.md`.

### Command line

```bash
roomcheck --scenario smoke_event       # canned scenario
roomcheck --inkbird                    # guided manual entry
roomcheck --csv readings.csv           # from a CSV log
roomcheck --watch --interval 60        # continuous loop
roomcheck --json | jq .alert           # pipe to anything
```

Exit code encodes status (`0` GREEN, `1` YELLOW, `2` RED, `3` UNKNOWN), so it chains cleanly with cron, alerting tools, CI pipelines.

### Quality bar

- 23 tests covering core evaluation, alert messages, resilience index, and adapter behavior.
- CI matrix on Linux, macOS, and Windows × Python 3.10 / 3.11 / 3.12.
- All thresholds cite published standards. No "we think this is right" numbers.
- All alerts are plain English. No jargon. No stack traces.

---

## Install

```bash
pip install room-check
roomcheck --scenario smoke_event
```

For Dyson live pulls: `pip install 'room-check[dyson]'`
For HTTP-based sensors: `pip install 'room-check[http]'`

---

## Origin

Originally built at GridHack 2026 (April 24, 2026, bwtech@UMBC) for **Montgomery County Library** — a 104,634 sq ft resilience hub serving 436 daily visitors, with no backup generator, R-22 chillers that can't be recharged, and air handlers from 1994. The library can't afford a $50,000 building-management system; they can run this on a laptop.

Built by five student teams over six hours. Each team owned one file (inputs, thresholds, evaluation, alerts, documentation), and the whole system integrated end-to-end.

---

## What's NOT in 1.0.0 (and that's intentional)

- **No sensors.** You bring the hardware (or a CSV).
- **No dashboard.** You bring the UI (or use the CLI).
- **No machine learning.** It's deliberately rule-based — auditable, deterministic, doesn't drift.
- **No medical advice.** A nurse, HVAC tech, or building engineer makes the final call. We're the boring middle layer.

---

## Roadmap

- More sensor adapters: Awair Element, Atmotube Pro, Airthings View, AirGradient, Sensirion SCD30 (USB), Modbus
- Localization (Spanish first — most impactful for Maryland libraries)
- Built-in alert delivery (Twilio SMS, Slack, Discord, email)
- Multi-room aggregation
- Web dashboard adapter (Grafana plugin, Home Assistant integration)
- BAS / building automation system integration

PRs welcome. See `CONTRIBUTING.md`.

---

## Thanks

To the Montgomery County Library team for letting us benchmark against their actual building data, to bwtech@UMBC for hosting GridHack, and to every student who showed up on April 24 and shipped.

If you deploy Room Check in a real building, open an issue and tell us about it. We'd love to know what it's protecting.

— Orivia Tech, GridHack 2026
