# Changelog

All notable changes to Room Check are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-04-24

First public release. Originally built at GridHack 2026 for Montgomery County Library.

### Added
- Core `evaluate()` engine — reads a dict of sensor values, returns GREEN/YELLOW/RED per parameter + worst-of overall.
- 5 supported parameters: CO₂ (ppm), PM2.5 (µg/m³), Temperature (°F), Humidity (%RH), VOC index (Sensirion 0–500).
- Default thresholds citing ASHRAE 62.1, EPA AQI, OSHA, ASHRAE 55, Sensirion VOC Index whitepaper.
- Plain-language alerts with smoke/heat/CO₂ special cases.
- Optional Community Resilience Index (0–100) for buildings with known structural vulnerabilities.
- Sensor adapters: `InteractiveManual`, `InkbirdManual`, `CSVFile`, `DysonCloud`, `JSONHttp`.
- `roomcheck` CLI with `--scenario`, `--inkbird`, `--csv`, `--watch`, `--json`, `--alerts-csv`.
- 7 built-in scenarios (normal, stuffy_room, ventilation_failure, heat_wave, smoke_event, power_outage, combined_emergency).
- 23-test pytest suite covering core logic, alerts, and adapters.
- GitHub Actions CI matrix: Linux/macOS/Windows × Python 3.10/3.11/3.12.

### Notes
- Dyson Pure Cool / Hot+Cool does not measure CO₂ — that parameter will return UNKNOWN.
- Inkbird IAM-* devices have flaky BLE pairing; the recommended adapter is `InkbirdManual` (guided manual entry).
