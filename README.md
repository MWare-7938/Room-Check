# Room Check

> **Turn raw indoor air-quality numbers into a clear GREEN, YELLOW, or RED safety call** — backed by published standards (ASHRAE, EPA, OSHA, Sensirion), with plain-language alerts a librarian, parent, or building manager can act on.

[![Tests](https://github.com/MWare-7938/Room-Check/actions/workflows/test.yml/badge.svg)](https://github.com/MWare-7938/Room-Check/actions)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Sensors](https://img.shields.io/badge/sensors-Dyson%20%7C%20Inkbird%20%7C%20CSV%20%7C%20HTTP-orange)

**Who this is for**
Room Check is for the people who already own indoor air quality sensors and need help acting on what they see. In the United States today, that is increasingly:

Households with disabled residents. People with asthma, COPD, autoimmune conditions, mobility limitations, or other chronic conditions who cannot easily relocate during a wildfire smoke event, a heat wave, or a power outage.
Seniors aging in place. Often on fixed incomes, often in older housing, often alone, often facing the highest mortality risk during heat events and air quality crises.
Households with language barriers. First-generation immigrant families, mixed-language households, anyone for whom the EPA AirNow app and AQI maps are not accessible.
Caregivers and family members trying to make safety calls for someone they love.

These households increasingly own indoor sensors. A Dyson Pure Cool was a holiday gift. An Inkbird IAM-O2 was a $90 Amazon order during fire season. A PurpleAir was deployed by a neighbor and the data is publicly available. The hardware exists. What is missing is the translation layer between the number on the screen and the action the person needs to take.
That is what Room Check is.

What it does
A $90 sensor can tell you "1280 ppm CO2." It cannot tell you what to do about it.
Room Check is the translation layer. You hand it readings; it hands back:
============================================================
 ROOM CHECK  [ UNSAFE ]
============================================================
  co2_ppm           1280     [RED]
  pm25_ugm3            8.0   [GREEN]
  temperature_f       73.0   [GREEN]
  humidity_pct        45.0   [GREEN]
  voc_index          110.0   [GREEN]
------------------------------------------------------------
  ALERT: URGENT: Carbon dioxide levels are very high. Poor
         ventilation. Open windows and doors if outdoor air
         is clean. This may indicate HVAC failure.
============================================================
That is the whole product. No dashboards to log into. No machine learning. No vendor lock-in. Just numbers in, action out.

Provenance and program home
Room Check was built by Michelle Ware-Allen at Orivia Institute, originally as part of GridHack 2026 at bwtech@UMBC during DC Climate Week. The reference deployment was a 104,634 square foot Montgomery County library that operates as a community shelter during outages, with no backup generator and aging HVAC plant that significantly predates the building itself.
The tool now anchors Breathe Easy Maryland, a community lending program operated through Citizens for Climate Action (the C Word Foundation, a 501(c)(3) public charity). The program model: Maryland public libraries lend Room Check kits (indoor air sensor plus a USB drive with the software and printed plain-language guides) the same way they already lend hot spots, Kill A Watt meters, and seed packets. A senior worried about wildfire smoke borrows the kit for a week. A family with an asthmatic child borrows it during a heat wave. The library gets it back, lends it again. The same translation layer serves vulnerable households whether they live alone or visit the library on a hot afternoon.
Room Check is also the operational complement to Orivia Institute's Resilience Hub Readiness Index research, which ranks public buildings at portfolio level for resilience hub designation. RHRI identifies which buildings should be doing this work; Room Check is what those buildings hand to the residents they serve.

60-second install and demo
bashpip install room-check
roomcheck --scenario smoke_event
That is it. You will see Room Check render a RED panel with the alert "Do NOT open windows. This may be a smoke event."
For real readings:
bash# Type values from any monitor's display
roomcheck

# Or for an Inkbird IAM-O2 / IAM-T1 / IAM-T2 (guided prompts)
roomcheck --inkbird

# Or for a Dyson (live)
pip install 'room-check[dyson]'
# (one-time setup writes ~/.dyson-auth.json)
roomcheck --csv dyson_live.csv --watch --interval 30

What it measures
Room Check evaluates 5 parameters that cover roughly 90 percent of indoor air quality concerns relevant to vulnerable households:
ParameterStandardGREENYELLOWREDCO2 (ppm)ASHRAE 62.1 (interpreted)<= 800<= 1200> 1200PM2.5 (ug/m3)EPA AQI<= 12<= 35.4> 35.4Temperature (F)ASHRAE 5565-8060-88outsideHumidity (%RH)ASHRAE 5530-6020-70outsideVOC index (0-500)Sensirion (tightened)<= 150<= 350> 350
The overall status is the worst of any parameter. One RED parameter forces a RED room. Missing measurements come back as UNKNOWN, never silently treated as safe.
Need different thresholds for your situation? A household with a chemotherapy patient, an asthmatic child, or a family member on home oxygen may want stricter limits. Override them in 4 lines of code (see Custom thresholds).

Why the alerts matter more than the numbers
Most air quality tools tell you what is wrong. Room Check tells you what to do:
SituationWhat Room Check saysWildfire smoke"Do NOT open windows. Run air purifiers. If you have respiratory conditions, move to your most sealed room."Extreme heat"Move vulnerable occupants (elderly, children, those with chronic conditions) to the coolest area. Provide water. Check on them every 30 minutes."High CO2"Open windows IF outdoor air is clean. May indicate HVAC failure."Smoke and heat together"Do NOT open windows. Move to interior room with filtered air. This is the hardest combination; consider relocating to a public cooling center if you can."
Every alert is actionable. Every alert is in plain English. No stack traces, no AQI math, no "consult an expert." This matters because the people who need this information most often do not have an expert to consult.

Sensors supported out of the box
Room Check is sensor-agnostic. Adapters live in roomcheck.sensors:
AdapterSourceInstallInteractiveManualType values at the terminalbuilt-inInkbirdManualGuided prompts for Inkbird IAM-* (CO2 + temp + humidity)built-inCSVFileLast row of any CSV (with optional column-name remap)built-inDysonCloudLive pull from Dyson Pure Cool / Hot+Cool via mDNSpip install 'room-check[dyson]'JSONHttpAny HTTP/JSON endpoint (PurpleAir, Awair, Home Assistant, custom IoT)pip install 'room-check[http]'
The supported sensors are intentionally accessible. Inkbird IAM-O2 is around $90. PurpleAir is community-deployed and often free to read. A used Dyson Pure Cool can be had for under $200. Awair Element is around $200 new. None of these require commercial procurement, vendor relationships, or specialized training to deploy in a private home.
Adding a new sensor takes about 30 lines of code. Subclass Sensor, implement read(), return a dict in the standard schema. See docs/adding_sensors.md.

Use it as a Python library
pythonfrom roomcheck import evaluate, alert_for, resilience_index

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
    notify_team(alert_for(result, readings))

Use it from the command line
bash# One-shot
roomcheck --scenario heat_wave           # canned scenario
roomcheck --csv my_log.csv               # from a CSV
roomcheck --inkbird                      # guided manual entry

# Continuous
roomcheck --scenario smoke_event --watch --interval 30

# Machine-readable for scripts and dashboards
roomcheck --scenario heat_wave --json | jq .alert
Exit code encodes the status: 0 GREEN, 1 YELLOW, 2 RED, 3 UNKNOWN. So you can chain Room Check into cron, alerting pipelines, anywhere a 0/non-zero exit matters:
bash# Cron: run every 5 minutes; if RED, send a text
*/5 * * * * roomcheck --csv /var/log/sensor.csv --json > /tmp/rc.json || sms-alert "$(jq -r .alert /tmp/rc.json)"

Custom thresholds
Override any parameter:
pythonfrom roomcheck import evaluate, DEFAULT_THRESHOLDS
from roomcheck.thresholds import Thresholds, CeilingThreshold
from dataclasses import replace

# Stricter PM2.5 limits for a household with a chemotherapy patient
strict = replace(DEFAULT_THRESHOLDS, pm25_ugm3=CeilingThreshold(
    green_max=5, yellow_max=12, unit="ug/m3",
    source="WHO 2021 air quality guidelines (sensitive population)",
    green_meaning="Safe for sensitive household members",
    yellow_meaning="Run air purifier; close windows if outdoor air is poor",
    red_meaning="Move sensitive household members to filtered room",
))

evaluate(readings, thresholds=strict)
The override mechanism is intended to be used. Default thresholds are interpreted from EPA AQI breakpoints, ASHRAE 55 thermal comfort guidance, ASHRAE 62.1 ventilation standards, and Sensirion VOC index documentation, calibrated for general indoor environments. A household with someone on home oxygen, a household with a newborn, a household with an autoimmune condition reasonably wants stricter limits. The customization path is documented and works.

Resilience Index
For households or facilities with known structural vulnerabilities, Room Check can compute a 0-100 Community Resilience Index that combines current air quality with documented building risk:
pythonfrom roomcheck import evaluate, resilience_index

result = evaluate(readings)
score = resilience_index(result, vulnerabilities={
    "no_backup_generator":  {"points_deducted": 20, "note": "Building goes dark in outage."},
    "no_air_purifiers":     {"points_deducted": 10, "note": "Nothing to scrub smoke."},
    "older_hvac":           {"points_deducted": 15, "note": "Equipment past expected service life."},
})
# {'score': 65.0, 'band': 'FRAGILE', 'breakdown': [...]}
Useful for advocacy conversations, capital planning, grant narratives, and any time someone needs to argue "this household, this senior center, this library, deserves a generator before the next heat wave." The scoring is documented and auditable; the deductions are evidence-based and traceable to specific structural conditions.

Examples
See examples/:

basic_usage.py - minimal Python use
live_dyson.py - pull from a Dyson every 30 seconds
manual_entry.py - guided manual entry
custom_thresholds.py - sensitive populations, schools, homes
scheduled_alerts.py - cron-style monitoring with email and SMS


Testing
bashpip install -e ".[dev]"
pytest
23 tests covering core evaluation logic, alert messages, resilience index, and sensor adapters. CI runs on Linux, macOS, and Windows with Python 3.10, 3.11, and 3.12 on every push.

Roadmap
The roadmap is prioritized by what reduces friction for vulnerable households first.

 Spanish localization of all alerts and CLI prompts. Highest equity priority for Maryland communities.
 Plain-language printed guides included in Breathe Easy Maryland kits. Walk-through cards for "what to do if the screen says RED."
 Additional accessible sensor adapters: Awair, Atmotube, Airthings, AirGradient.
 Phone alert integrations: Twilio SMS, simple email, voice call (for users without smartphones).
 Web dashboard adapter for caregivers monitoring a parent's home remotely (Home Assistant, Grafana plugin).
 Multi-room aggregation for senior care facilities, family homes with multiple zones.

PRs welcome on any of these. Contributions that improve accessibility for non-technical users are prioritized.

Breathe Easy Maryland
Citizens for Climate Action operates Breathe Easy Maryland, a community lending program that puts Room Check kits in the hands of vulnerable Maryland residents through their public libraries. A kit consists of an indoor air sensor (Inkbird IAM-O2 standard, with Dyson and Awair upgrades for partner libraries), a USB drive with Room Check pre-installed, printed plain-language guides in English and Spanish, and a single-page laminated quick-reference card.
Libraries lend kits in two-week loans, the way they already lend hot spots and seed packets. Borrowers receive a brief training from library staff (15 minutes), take the kit home, monitor their air quality during heat waves, smoke events, or just for general operational awareness, and return the kit. Anonymized aggregate data flows back to Citizens for Climate Action and partner researchers, informing future advocacy for indoor air quality protections.
The program is in pilot with Montgomery County libraries and is seeking partnership with additional Maryland library systems. To inquire about hosting kits at your library, partnering as a disability or aging advocacy organization, or contributing as a researcher, contact Citizens for Climate Action through Orivia Institute.

Companion research
Room Check sits within a larger Orivia Institute research portfolio applying civic data analysis to building energy and resilience hub readiness in Montgomery County, Maryland.
ArtifactDescriptionResilience Hub Readiness Index briefTwo-page methodology and findings document, 1,828 BEPS-covered buildings rankedRockville Memorial Library case studyThe reference building for Room Check's designCharles McGee Library case studyThe lone improving public library trajectory in the County datasetMoCo-BEPS-Bench datasetForthcoming research dataset, summer 2026 release under Creative Commons Attribution
If Room Check is useful to your work, the research portfolio it sits within is likely useful too.

Contributing
This started as a hackathon project. It works because real librarians, real seniors, and real families have used it in their actual homes during actual smoke events. Keep that spirit:

Fork, branch, PR.
Add a test for any new logic.
Cite a real published standard for any new threshold.
Plain-language alerts only. No jargon. No shame in writing for people who do not have engineering degrees.

See CONTRIBUTING.md for setup details.

License
MIT. Use it in your home, your library, your senior center, your school, your commercial product. Modify it, fork it, sell it, give it away.
If you ship Room Check in production, we would love to hear about it. Open an issue with [Used in production] in the title and tell us what household, what library, what facility, is breathing easier because of it.

Citation
If you use Room Check in research, civic publications, advocacy materials, or grant applications:
Ware-Allen, M. (2026). Room Check: Open-source indoor air quality safety
translator for vulnerable households. Orivia Institute LLC and Citizens
for Climate Action. https://github.com/MWare-7938/Room-Check

Originally developed for Montgomery County Library, GridHack 2026 at
bwtech@UMBC. Operated as part of Breathe Easy Maryland community
lending program.

A note on what this is NOT

Not a sensor. You bring the hardware, or borrow a kit from your library.
Not a dashboard. You bring the UI, or use the CLI.
Not medical advice. It is a translator. A nurse, a doctor, a respiratory therapist, or a building engineer makes the final call.
Not certified. No FCC, no CE, no FDA. It is MIT-licensed software that reads numbers and applies published standards.
Not a replacement for professional indoor air quality assessment in commercial buildings. Building engineers use calibrated, NIST-traceable instruments for compliance work. Room Check is for the people who do not have a building engineer to call.

Room Check is meant to be the boring, reliable middle layer between "I have a sensor reading" and "what should I do." Everything else (the hardware, the dashboards, the medical judgment, the professional commissioning, the legal designation) is someone else's job.
That is the point.
