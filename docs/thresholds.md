# Default thresholds and their sources

Every default threshold cites a real published standard. Don't change one without updating the citation.

## Why these specific numbers

### CO₂ — ASHRAE Standard 62.1-2022, Appendix D

Outdoor baseline ~420 ppm + a 700 ppm differential = ~1100 ppm as a per-occupant ceiling. We round down to 800 ppm GREEN / 1200 ppm YELLOW because:

- Cognitive performance starts measurably degrading above 1000 ppm.
- A librarian or teacher can intervene by simply opening windows, which is cheap.
- False positives are recoverable; missed exposures are not.

### PM2.5 — EPA AQI breakpoints, 40 CFR Part 58 Appendix G

12 µg/m³ is the EPA "Good" ceiling. 35.4 µg/m³ is the "Moderate / Unhealthy for Sensitive Groups" line. Above that the alert switches to "do NOT open windows" — which is the most counterintuitive guidance in indoor air quality.

These are 24-hour averages. If your sensor reports a 1-second reading and you're seeing 89 µg/m³, that's a smoke event and you should treat it as one.

### Temperature — OSHA Technical Manual III.2 + ASHRAE 55

OSHA recommends 68–76°F for offices. ASHRAE 55 widens that slightly for clothing variation. We extend to 65–80°F GREEN / 60–88°F YELLOW because:

- Resilience hubs may not be able to hold tight setpoints during outages.
- Outside 60°F there's risk of hypothermia in elderly visitors.
- Above 88°F there's risk of heat exhaustion, especially for kids.

### Humidity — ASHRAE Standard 55-2020

30–60% RH is the textbook comfort zone. Below 20% you get respiratory irritation and static damage to electronics. Above 70% mold grows in walls within days. Our YELLOW band (20–70%) captures everything still livable; outside it is a real problem.

### VOC — Sensirion VOC Index whitepaper

The Sensirion VOC Index uses 100 as a baseline (= air composition of the last 24 hours). 150 GREEN / 350 YELLOW corresponds to "fresh" / "noticeably elevated" / "investigate now."

If you're using a different VOC sensor (e.g., raw ppb measurements), you'll need to scale. As a rough mapping: divide your sensor's typical baseline reading by 100 to get a multiplier, or write a custom threshold in your initialization.

## Why "worst wins"

Room Check's overall status is the **worst** parameter — one RED forces the room to RED. This is conservative on purpose:

- Air quality risks compound in unpredictable ways.
- A librarian opening windows during a smoke event because "everything else is GREEN" would be worse than the original problem.
- It's better to occasionally over-warn than to miss a real risk.

## Why "UNKNOWN" doesn't equal "GREEN"

Missing data is the most common failure mode in indoor sensors. A disconnected CO₂ sensor returns nothing. A PM2.5 sensor with a clogged inlet shows zero forever.

If we treated missing data as "GREEN" we'd quietly fail. So:

- A single UNKNOWN parameter forces the overall status to UNKNOWN at minimum.
- Multiple UNKNOWNs trigger an explicit alert: "Some sensor readings are unavailable."
- A librarian will want to investigate why before relying on the dashboard.

## Customizing thresholds

See [`examples/custom_thresholds.py`](../examples/custom_thresholds.py) for a school example. Common reasons to override:

| Building type | What to change | Why |
|---|---|---|
| School | Tighter CO₂ (600/900) | Children's developing respiratory systems + dense classrooms |
| Hospital | Tighter PM2.5 + stricter humidity | Immunocompromised patients + sterile-environment standards |
| Home | Looser everything | Comfort > strict standards |
| Greenhouse | Wider temp + humidity | Plants tolerate more than people do |
| Server room | Tighter humidity (30–50) | Static damage + condensation |

Whenever you change a threshold, **update the `source` field** with where the new value came from. Future-you (and anyone auditing your code) will need to know.
