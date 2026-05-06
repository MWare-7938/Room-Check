"""Run on a schedule (cron, systemd timer, Task Scheduler).

If RED, send a text. If YELLOW, log it. If GREEN, do nothing.

Suggested cron line (every 5 minutes):
    */5 * * * * /usr/bin/python /path/to/scheduled_alerts.py
"""
import os
import sys
from roomcheck import evaluate, alert_for
from roomcheck.sensors import CSVFile

# Adjust this path to wherever your sensor logs land.
LOG = os.environ.get("ROOMCHECK_LOG", "/var/log/sensor.csv")

try:
    readings = CSVFile(LOG).read()
except Exception as exc:
    sys.exit(f"Could not read sensor log: {exc}")

result = evaluate(readings)
msg = alert_for(result, readings)

if result.overall == "RED":
    # Hook up your alerting here. Examples:
    #
    # Twilio SMS:
    #     from twilio.rest import Client
    #     Client(SID, TOKEN).messages.create(to=PHONE, from_=FROM, body=msg)
    #
    # Slack:
    #     import requests
    #     requests.post(SLACK_WEBHOOK, json={"text": msg})
    #
    # Email via SMTP:
    #     smtp.send_message(...)
    print(f"[ALERT] {msg}")
elif result.overall == "YELLOW":
    print(f"[CAUTION] {msg}")

sys.exit({"GREEN": 0, "YELLOW": 1, "RED": 2, "UNKNOWN": 3}.get(result.overall, 3))
