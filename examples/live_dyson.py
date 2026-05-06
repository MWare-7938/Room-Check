"""Pull live readings from a Dyson Pure Cool / Hot+Cool every 30 seconds.

One-time setup:
    pip install 'room-check[dyson]'
    python -c "from libdyson.cloud.account import DysonAccount; print('ok')"
    # then run an OTP login flow that gives you serial + credential + product_type

Save those three values somewhere (env vars are nice).
"""
import os
import time
from roomcheck import evaluate, alert_for
from roomcheck.sensors import DysonCloud

dyson = DysonCloud(
    serial=os.environ["DYSON_SERIAL"],
    credential=os.environ["DYSON_CREDENTIAL"],
    product_type=os.environ.get("DYSON_PRODUCT_TYPE", "438"),
)

with dyson:
    while True:
        try:
            readings = dyson.read()
            result = evaluate(readings)
            print(f"[{readings.get('timestamp','?')}] {result.overall:7s}  {alert_for(result)}")
        except Exception as exc:
            print(f"  read failed: {exc}")
        time.sleep(30)
