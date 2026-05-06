"""
roomcheck — command-line interface.

    roomcheck                              # interactive prompt
    roomcheck --inkbird                    # guided Inkbird IAM-* entry
    roomcheck --csv path/to/log.csv        # read latest row from CSV
    roomcheck --scenario smoke_event       # canned scenario
    roomcheck --watch --interval 30        # continuous loop
    roomcheck --json                       # machine-readable output

Exit codes encode the safety status:
    0 GREEN, 1 YELLOW, 2 RED, 3 UNKNOWN

That makes Room Check easy to chain with other tools — alerting,
dashboards, CI, cron, etc.
"""
from __future__ import annotations
import argparse
import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from . import evaluate, alert_for, resilience_index, DEFAULT_THRESHOLDS
from .render import render_panel
from .scenarios import SCENARIOS
from .sensors import InteractiveManual, InkbirdManual, CSVFile

EXIT_BY_STATUS = {"GREEN": 0, "YELLOW": 1, "RED": 2, "UNKNOWN": 3}


def _gather(args) -> tuple[dict, str]:
    if args.scenario:
        scn = SCENARIOS.get(args.scenario)
        if scn is None:
            sys.exit(f"Unknown scenario: {args.scenario}\nAvailable: {', '.join(SCENARIOS)}")
        return dict(scn["readings"]), f"scenario:{args.scenario}"
    if args.csv:
        return CSVFile(args.csv).read(), f"csv:{args.csv}"
    if args.inkbird:
        return InkbirdManual().read(), "inkbird-manual"
    return InteractiveManual().read(), "manual"


def _append_alerts(path: Path, payload: dict) -> None:
    new = not path.exists()
    cols = [
        "timestamp", "source", "overall_status", "alert_full",
        "co2_ppm", "pm25_ugm3", "temperature_f", "humidity_pct", "voc_index",
        "resilience_score", "resilience_band",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(cols)
        r = payload["resilience"] or {"score": "", "band": ""}
        w.writerow([
            payload["timestamp"], payload["source"],
            payload["status"]["overall"], payload["alert"],
            payload["readings"].get("co2_ppm"),
            payload["readings"].get("pm25_ugm3"),
            payload["readings"].get("temperature_f"),
            payload["readings"].get("humidity_pct"),
            payload["readings"].get("voc_index"),
            r["score"], r["band"],
        ])


def main():
    p = argparse.ArgumentParser(
        prog="roomcheck",
        description="Translate indoor air-quality readings into GREEN/YELLOW/RED.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  roomcheck                              prompt at the terminal\n"
            "  roomcheck --inkbird                    guided Inkbird entry\n"
            "  roomcheck --csv readings.csv           read last row of CSV\n"
            "  roomcheck --scenario smoke_event       run a canned scenario\n"
            "  roomcheck --scenario smoke_event --json | jq .alert\n"
            "  roomcheck --watch --interval 60        keep polling\n\n"
            f"Scenarios: {', '.join(SCENARIOS)}"
        ),
    )
    src = p.add_mutually_exclusive_group()
    src.add_argument("--inkbird", action="store_true", help="guided Inkbird IAM-* manual entry")
    src.add_argument("--csv", metavar="PATH", help="read latest row from a CSV file")
    src.add_argument("--scenario", metavar="NAME", help=f"use a canned scenario ({', '.join(SCENARIOS)})")

    p.add_argument("--watch", action="store_true", help="continuous loop")
    p.add_argument("--interval", type=int, default=30, help="seconds between polls in --watch")
    p.add_argument("--json", action="store_true", help="emit machine-readable JSON only")
    p.add_argument("--alerts-csv", default="alerts.csv", help="append each result to this CSV")
    p.add_argument("--no-alerts-csv", action="store_true", help="don't write alerts.csv")
    args = p.parse_args()

    def one() -> dict:
        readings, source = _gather(args)
        result = evaluate(readings, DEFAULT_THRESHOLDS)
        msg = alert_for(result, readings)
        resilience = resilience_index(result)
        ts = datetime.now().isoformat(timespec="seconds")
        payload = {
            "timestamp": ts,
            "source": source,
            "readings": result.readings,
            "status": {
                "overall": result.overall,
                "parameters": result.parameters,
            },
            "alert": msg,
            "resilience": resilience,
        }
        if args.json:
            print(json.dumps(payload, default=str))
        else:
            print(render_panel(result, alert=msg, timestamp=ts, source=source))
            print(f"  Resilience: {resilience['score']}/100 ({resilience['band']})")
        if not args.no_alerts_csv:
            _append_alerts(Path(args.alerts_csv), payload)
        return payload

    if not args.watch:
        payload = one()
        sys.exit(EXIT_BY_STATUS.get(payload["status"]["overall"], 3))

    print(f"Watching every {args.interval}s. Ctrl-C to stop.")
    while True:
        try:
            one()
            time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nStopped.")
            return


if __name__ == "__main__":
    main()
