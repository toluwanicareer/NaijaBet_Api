# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NaijaBet_Api is a Python library that wraps the APIs of Nigerian betting sites (Bet9ja, Betking, Nairabet) to extract and normalize football match odds. Published to PyPI as `NaijaBet_Api`. No web framework, no database — pure data extraction library.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Install package locally (editable)
pip install -e .

# Run all tests (these are live E2E tests hitting real APIs)
pytest tests/ -v

# Run tests for a single bookmaker
pytest tests/test_bet9ja_e2e.py -v
pytest tests/test_betking_e2e.py -v
pytest tests/test_nairabet_e2e.py -v
pytest tests/test_betking_playwright.py -v

# Run a single test
pytest tests/test_bet9ja_e2e.py::TestBet9jaE2E::test_get_league_returns_list -v

# Lint
flake8 NaijaBet_Api/ --max-line-length=120

# Build for PyPI
python -m build
```

## Architecture

### Data Flow

```
Betid enum (league IDs per site) → BookmakerBaseClass.get_league()
  → HTTP request (requests sync / aiohttp async)
    → JMESPath extraction (utils/jsonpaths.py)
      → Name normalization (utils/normalizer.py + JSON lookup tables)
        → List[Dict] with standardized match/odds fields
```

### Key Abstractions

- **`BookmakerBaseClass`** (`NaijaBet_Api/bookmakers/BaseClass.py`): Abstract base using Template Method pattern. Handles HTTP sessions, sync/async operations, iteration over leagues. Subclasses must implement `normalizer()`.
- **`Betid` enum** (`NaijaBet_Api/id.py`): Maps league names to site-specific IDs (4-tuple: bet9ja_id, betking_id, nairabet_id, sportybet_id). Has `to_endpoint(site)` method that builds the full API URL.
- **Bookmaker classes** (`NaijaBet_Api/bookmakers/`): `Bet9ja`, `Betking`, `Nairabet` each inherit from `BookmakerBaseClass` and implement `normalizer()` to transform site-specific JSON into the standardized format.
- **`BetkingPlaywright`** (`NaijaBet_Api/bookmakers/betking_playwright.py`): Separate Playwright-based implementation for Betking that bypasses Cloudflare protection. Used as async context manager.

### Normalization Pipeline

- `utils/jsonpaths.py`: JMESPath expressions that extract fields from each bookmaker's nested JSON response structure.
- `utils/normalizer.py`: Converts extracted data — maps team names via JSON lookup files (`*_normalizer.json`), converts odds strings to floats, converts timestamps via `arrow`.
- `utils/*.json`: Team name mapping files for each bookmaker (canonical name resolution).

### Standardized Output Format

All bookmaker classes return `List[Dict]` with these fields:
- `match` (str): `"Team A - Team B"`
- `league` (str), `time` (int, unix timestamp), `league_id` (int), `match_id` (int)
- `home`, `draw`, `away` (float): 1X2 odds
- `home_or_draw`, `home_or_away`, `draw_or_away` (float, optional): double-chance odds

## Testing Notes

- All tests are **live E2E tests** — they make real HTTP calls to betting site APIs. No mocks.
- Tests may fail if a betting site is down or changes its API.
- Betking standard tests expect empty results (Cloudflare blocks non-browser requests). The Playwright tests require `playwright` installed with browsers.
- `asyncio_mode = auto` in pytest.ini — async tests run automatically without markers.

## Publishing

CI publishes to PyPI on push to the `release` branch (via `.github/workflows/py-build.yml`). Version is in `setup.cfg`.
