# Contributing to Room Check

Thanks for considering it. Room Check stays useful because real librarians, teachers, and building managers rely on it. Keep that in mind when you ship.

## Before you write code

1. Open an issue describing the problem you want to solve. Even a one-liner is fine.
2. If you're adding a sensor adapter, check [`docs/adding_sensors.md`](docs/adding_sensors.md) — the API is small on purpose.
3. If you're proposing new thresholds, **bring a citation** (ASHRAE / EPA / WHO / OSHA / a peer-reviewed paper). We reject unsourced numbers.

## Local setup

```bash
git clone https://github.com/MWare-7938/Room-Check.git
cd room-check
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

## Style

- **Lint:** `ruff check src tests`
- **Format:** we use ruff's autofix; no separate formatter.
- **Tests:** any new logic gets at least one test. PRs without tests don't merge.
- **Docstrings:** module-level docstrings explaining what + why. Inline comments only where the *why* isn't obvious.
- **Plain English alerts:** no jargon. A librarian or teacher should understand every alert without Googling.

## What we reject

- Adding a dependency for something you could do in 20 lines of stdlib.
- Adding a parameter (e.g., NO₂, HCHO) without a published threshold + citation.
- "Smart" features that try to predict alerts. Room Check is deliberately rule-based — it's auditable, you can tell a librarian *why* it said RED, and the rules don't drift over time.
- Vendor-locked sensors. Adapters must work with documented APIs / protocols.

## What we love

- New sensor adapters for cheap, common monitors.
- Translations of the alert messages (Spanish first, then any language).
- Real-world deployment stories. If Room Check is running in your building, open a discussion thread or PR a case study.
- Better thresholds for special contexts (hospitals, daycares, server rooms).

## Tests

```bash
pytest                         # all tests
pytest tests/test_core.py      # just core
pytest -k smoke                # by keyword
pytest --cov=roomcheck         # with coverage
```

CI runs the full matrix (Linux/macOS/Windows × Python 3.10/3.11/3.12) on every push. If CI fails on a platform you don't have, ping a maintainer and we'll help.

## Releasing (maintainers only)

1. Bump `__version__` in `src/roomcheck/__init__.py` and the version in `pyproject.toml`.
2. Update CHANGELOG.md.
3. Tag: `git tag v1.x.y && git push --tags`.
4. GitHub Actions builds and publishes to PyPI.

## Code of Conduct

We follow the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Be kind. The whole point of this project is helping people — be kind to the contributors too.
