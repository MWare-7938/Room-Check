"""Alert message tests — the part a librarian actually reads."""
from roomcheck import evaluate, alert_for, resilience_index


def test_green_message_is_calm():
    r = evaluate({"co2_ppm": 500, "pm25_ugm3": 5, "temperature_f": 72,
                  "humidity_pct": 45, "voc_index": 80})
    msg = alert_for(r)
    assert "safe" in msg.lower() or "good" in msg.lower()
    assert "no action" in msg.lower()


def test_smoke_says_no_windows():
    """The single most important alert: smoke event → don't open windows."""
    r = evaluate({"co2_ppm": 500, "pm25_ugm3": 89, "temperature_f": 73,
                  "humidity_pct": 40, "voc_index": 100})
    msg = alert_for(r)
    assert "do not open" in msg.lower() or "not open windows" in msg.lower()
    assert "window" in msg.lower()


def test_heat_calls_out_vulnerable():
    r = evaluate({"co2_ppm": 500, "pm25_ugm3": 5, "temperature_f": 95,
                  "humidity_pct": 45, "voc_index": 80})
    msg = alert_for(r)
    assert any(w in msg.lower() for w in ("elder", "vulnerable", "children"))


def test_high_co2_says_open_windows_if_clean():
    r = evaluate({"co2_ppm": 1500, "pm25_ugm3": 5, "temperature_f": 72,
                  "humidity_pct": 45, "voc_index": 80})
    msg = alert_for(r)
    assert "ventilation" in msg.lower() or "window" in msg.lower()


def test_unknown_says_check_sensors():
    r = evaluate({"co2_ppm": None, "pm25_ugm3": 5, "temperature_f": 72,
                  "humidity_pct": 45, "voc_index": 80})
    msg = alert_for(r)
    assert "sensor" in msg.lower() or "unavailable" in msg.lower()


def test_resilience_max_when_safe():
    r = evaluate({"co2_ppm": 500, "pm25_ugm3": 5, "temperature_f": 72,
                  "humidity_pct": 45, "voc_index": 80})
    res = resilience_index(r)
    assert res["score"] == 100
    assert res["band"] == "RESILIENT"


def test_resilience_drops_with_red():
    r = evaluate({"co2_ppm": 500, "pm25_ugm3": 89, "temperature_f": 72,
                  "humidity_pct": 45, "voc_index": 80})
    res = resilience_index(r)
    assert res["score"] < 100


def test_resilience_with_vulnerabilities():
    r = evaluate({"co2_ppm": 500, "pm25_ugm3": 5, "temperature_f": 72,
                  "humidity_pct": 45, "voc_index": 80})
    res = resilience_index(r, vulnerabilities={
        "no_backup_generator": {"points_deducted": 20, "note": "outage risk"},
    })
    assert res["score"] == 80
    assert res["band"] == "RESILIENT"  # 80 is the floor of RESILIENT
