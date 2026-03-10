# Altenar Base Class Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an Altenar base class that provides shared scraping logic for Nairabet and Betking via the Altenar sportsbook API, with optional proxy support.

**Architecture:** `AltenarBaseClass` inherits from `BookmakerBaseClass`, overrides `__init__`, `get_league`, `get_all`, `get_team`, and implements `normalizer`. It handles the relational join (events → markets → odds) that the Altenar API requires. Thin subclasses `NairabetAltenar` and `BetkingAltenar` only set `_integration` and `_site`. The `Betid` enum gets a 5th ID field (`altenar_id`).

**Tech Stack:** Python, requests, existing project patterns

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `NaijaBet_Api/id.py` | Modify | Add `altenar_id` to `Betid` enum, add Altenar endpoints, add `altenar` branch in `to_endpoint` |
| `NaijaBet_Api/bookmakers/altenar_base.py` | Create | `AltenarBaseClass` — Altenar API fetching, relational data joining, normalization |
| `NaijaBet_Api/bookmakers/nairabet_altenar.py` | Create | `NairabetAltenar` — sets `_integration="nairabet"` |
| `NaijaBet_Api/bookmakers/betking_altenar.py` | Create | `BetkingAltenar` — sets `_integration="betking"` |
| `NaijaBet_Api/bookmakers/__init__.py` | Modify | Export new classes |
| `tests/test_altenar_e2e.py` | Create | E2E tests for both Altenar subclasses |

---

## Chunk 1: Betid Enum and Altenar Base Class

### Task 1: Add altenar_id to Betid enum

**Files:**
- Modify: `NaijaBet_Api/id.py:6-73`
- Test: `tests/test_altenar_e2e.py`

- [ ] **Step 1: Write failing test for altenar_id**

```python
# tests/test_altenar_e2e.py
import pytest
from NaijaBet_Api.id import Betid

class TestAltenarIds:
    def test_betid_has_altenar_id(self):
        assert hasattr(Betid.PREMIERLEAGUE, 'altenar_id')
        assert Betid.PREMIERLEAGUE.altenar_id == 2936

    def test_all_leagues_have_altenar_id(self):
        for league in Betid:
            assert isinstance(league.altenar_id, int), f"{league.name} missing altenar_id"

    def test_to_endpoint_altenar(self):
        url = Betid.PREMIERLEAGUE.to_endpoint('altenar')
        assert 'sb2frontend-altenar2.biahosted.com' in url
        assert 'champIds=2936' in url
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/Scripts/python -m pytest tests/test_altenar_e2e.py::TestAltenarIds -v`
Expected: FAIL — `AttributeError: altenar_id`

- [ ] **Step 3: Update Betid enum**

In `NaijaBet_Api/id.py`, add `"altenar"` to endpoints dict:

```python
"altenar": {
    "leagues": "https://sb2frontend-altenar2.biahosted.com/api/widget/GetEventsByChamp?culture=en-GB&timezoneOffset=-60&integration={integration}&deviceType=1&numFormat=en-GB&countryCode=NG&champId=0&champIds={leagueid}"
}
```

Update `Betid` enum values to 5-tuples (add altenar_id as 5th):

```python
class Betid(Enum):
    PREMIERLEAGUE = 170880, 841, "EN_PR", 17, 2936
    CHAMPIONSHIP = 170881, 863, "EN_CH", 18, 2937
    LEAGUE_ONE = 995354, 909, "EN_L1", 24, 2947
    LEAGUE_TWO = 995355, 939, "EN_L2", 25, 2946
    BUNDESLIGA = 180923, 1007, "DE_BL", 35, 2950
    BUNDESLIGA_2 = 180924, 1025, "DE_B2", 44, 2954
    LALIGA = 180928, 1108, "ES_PL", 8, 2941
    LIGUE_1 = 950503, 1104, "FR_L1", 34, 2943
    LIGUE_2 = 958691, 1179, "FR_L2", 182, 2939
    SERIEA = 167856, 3775, "IT_SA", 23, 2942
```

Update `__init__` to accept 5th param:

```python
def __init__(self, bet9ja_id, betking_id, nairabet_id, sportybet_id, altenar_id):
    self.bet9ja_id = bet9ja_id
    self.betking_id = betking_id
    self.nairabet_id = nairabet_id
    self.sportybet_id = sportybet_id
    self.altenar_id = altenar_id
```

Add `altenar` branch to `to_endpoint`. Note: the `integration` placeholder is NOT resolved here — callers pass the integration name separately. So `to_endpoint('altenar')` returns the URL with `{integration}` still in it:

```python
elif betting_site == 'altenar':
    endpoint_url = endpoints["altenar"]["leagues"].format(
        leagueid=self.altenar_id,
        integration="{integration}"  # left as placeholder for subclass to fill
    )
```

Actually, simpler: just return the URL with `leagueid` resolved. The `AltenarBaseClass` will handle inserting its `_integration` value.

```python
elif betting_site == 'altenar':
    endpoint_url = endpoints["altenar"]["leagues"].format(
        leagueid=self.altenar_id,
        integration="{integration}"
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/Scripts/python -m pytest tests/test_altenar_e2e.py::TestAltenarIds -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add NaijaBet_Api/id.py tests/test_altenar_e2e.py
git commit -m "feat: add altenar_id to Betid enum and altenar endpoint"
```

---

### Task 2: Create AltenarBaseClass

**Files:**
- Create: `NaijaBet_Api/bookmakers/altenar_base.py`
- Test: `tests/test_altenar_e2e.py`

- [ ] **Step 1: Write failing test for AltenarBaseClass**

Append to `tests/test_altenar_e2e.py`:

```python
from NaijaBet_Api.bookmakers.altenar_base import AltenarBaseClass
from NaijaBet_Api.id import Betid
import requests

class TestAltenarBaseClass:
    def test_cannot_instantiate_directly(self):
        """AltenarBaseClass requires _integration to be set by subclass"""
        with pytest.raises(NotImplementedError):
            class BareAltenar(AltenarBaseClass):
                _site = 'test'
                _url = 'http://test.com'
            BareAltenar()

    def test_proxy_support(self):
        """Should accept proxies dict and apply to session"""
        class FakeAltenar(AltenarBaseClass):
            _site = 'fakealtenar'
            _url = 'https://example.com'
            _integration = 'fake'
        fa = FakeAltenar(proxies={"https": "http://proxy:8080"})
        assert fa.session.proxies == {"https": "http://proxy:8080"}

    def test_normalizer_empty_input(self):
        """normalizer should return [] for empty/None input"""
        class FakeAltenar(AltenarBaseClass):
            _site = 'fakealtenar'
            _url = 'https://example.com'
            _integration = 'fake'
        fa = FakeAltenar()
        assert fa.normalizer(None) == []
        assert fa.normalizer({"events": [], "odds": [], "markets": []}) == []

    def test_normalizer_joins_data(self):
        """normalizer should join events, markets, odds into standardized format"""
        class FakeAltenar(AltenarBaseClass):
            _site = 'fakealtenar'
            _url = 'https://example.com'
            _integration = 'fake'
        fa = FakeAltenar()

        mock_response = {
            "events": [{
                "id": 100,
                "name": "Team A vs. Team B",
                "startDate": "2026-03-14T15:00:00Z",
                "champId": 2936,
                "marketIds": [1, 2],
            }],
            "markets": [
                {"id": 1, "name": "1x2", "oddIds": [10, 11, 12], "typeId": 1},
                {"id": 2, "name": "Double chance", "oddIds": [20, 21, 22], "typeId": 10},
            ],
            "odds": [
                {"id": 10, "typeId": 1, "price": 2.5, "name": "Team A"},
                {"id": 11, "typeId": 2, "price": 3.0, "name": "X"},
                {"id": 12, "typeId": 3, "price": 2.8, "name": "Team B"},
                {"id": 20, "typeId": 9, "price": 1.5, "name": "Team A or draw"},
                {"id": 21, "typeId": 10, "price": 1.3, "name": "Team A or Team B"},
                {"id": 22, "typeId": 11, "price": 1.4, "name": "Draw or Team B"},
            ],
            "champs": [{"id": 2936, "name": "Premier League"}],
        }

        result = fa.normalizer(mock_response)
        assert len(result) == 1
        match = result[0]
        assert match["match"] == "Team A - Team B"
        assert match["match_id"] == 100
        assert match["league"] == "Premier League"
        assert match["league_id"] == 2936
        assert match["home"] == 2.5
        assert match["draw"] == 3.0
        assert match["away"] == 2.8
        assert match["home_or_draw"] == 1.5
        assert match["home_or_away"] == 1.3
        assert match["draw_or_away"] == 1.4
        assert isinstance(match["time"], int)  # unix timestamp
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/Scripts/python -m pytest tests/test_altenar_e2e.py::TestAltenarBaseClass -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement AltenarBaseClass**

Create `NaijaBet_Api/bookmakers/altenar_base.py`:

```python
import requests
import arrow
from NaijaBet_Api.bookmakers.BaseClass import BookmakerBaseClass
from NaijaBet_Api.id import Betid
from typing import List, Dict, Any, Optional


# Altenar odds typeId → standardized field name
ODDS_TYPE_MAP = {
    1: "home",
    2: "draw",
    3: "away",
    9: "home_or_draw",
    10: "home_or_away",
    11: "draw_or_away",
}


class AltenarBaseClass(BookmakerBaseClass):
    """
    Base class for bookmakers powered by the Altenar sportsbook platform.

    Subclasses must set:
        _integration: str — Altenar integration name (e.g. "nairabet", "betking")
        _site: str — site identifier
        _url: str — base site URL
    """

    _headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, '_integration'):
            raise NotImplementedError("Altenar subclasses must define _integration")

    def __init__(self, proxies: Optional[Dict[str, str]] = None):
        """
        Args:
            proxies: Optional dict for requests, e.g. {"https": "http://user:pass@host:port"}
        """
        self.site = 'altenar'
        self.session = requests.Session()
        self.session.headers.update(self._headers)
        if proxies:
            self.session.proxies = proxies

    def _build_url(self, league: Betid) -> str:
        """Build the Altenar API URL for a league."""
        return league.to_endpoint('altenar').format(integration=self._integration)

    def normalizer(self, data: Any) -> List[Dict[str, Any]]:
        """
        Join the relational Altenar response into standardized match dicts.
        """
        if not data or not isinstance(data, dict):
            return []

        events = data.get("events", [])
        if not events:
            return []

        odds_list = data.get("odds", [])
        markets_list = data.get("markets", [])
        champs_list = data.get("champs", [])

        odds_by_id = {o["id"]: o for o in odds_list}
        markets_by_id = {m["id"]: m for m in markets_list}
        champs_by_id = {c["id"]: c for c in champs_list}

        results = []
        for event in events:
            champ = champs_by_id.get(event.get("champId"), {})

            # Collect odds from 1x2 and double chance markets
            match_odds = {}
            for mid in event.get("marketIds", []):
                market = markets_by_id.get(mid, {})
                for oid in market.get("oddIds", []):
                    odd = odds_by_id.get(oid, {})
                    type_id = odd.get("typeId")
                    field = ODDS_TYPE_MAP.get(type_id)
                    if field:
                        match_odds[field] = odd.get("price")

            # Convert "Team A vs. Team B" to "Team A - Team B"
            name = event.get("name", "")
            match_name = name.replace(" vs. ", " - ")

            # Convert ISO timestamp to unix int
            start_date = event.get("startDate", "")
            try:
                time_val = arrow.get(start_date).int_timestamp
            except Exception:
                time_val = 0

            match_dict = {
                "match": match_name,
                "league": champ.get("name", ""),
                "time": time_val,
                "league_id": event.get("champId", 0),
                "match_id": event.get("id", 0),
            }
            match_dict.update(match_odds)
            results.append(match_dict)

        return results

    def get_league(self, league: Betid = Betid.PREMIERLEAGUE) -> List[Dict[str, Any]]:
        """Fetch odds for a league via the Altenar API."""
        try:
            url = self._build_url(league)
            res = self.session.get(url)
            if res.status_code != 200:
                print(f"Warning: HTTP {res.status_code} for {self._integration}")
                return []
            data = res.json()
            if data is None:
                return []
            return self.normalizer(data)
        except Exception as e:
            print(f"Error fetching league for {self._integration}: {e}")
            return []

    def get_all(self) -> List[Dict[str, Any]]:
        """Fetch odds for all implemented leagues."""
        self.data = []
        for league in Betid:
            self.data += self.get_league(league)
        return self.data

    def get_team(self, team: str) -> List[Dict[str, Any]]:
        """Fetch odds for matches involving a specific team."""
        self.get_all()

        def filter_func(data):
            match: str = data["match"]
            return match.lower().find(team.lower()) != -1

        return list(filter(filter_func, self.data))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/Scripts/python -m pytest tests/test_altenar_e2e.py::TestAltenarBaseClass -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add NaijaBet_Api/bookmakers/altenar_base.py tests/test_altenar_e2e.py
git commit -m "feat: add AltenarBaseClass with relational data joining and proxy support"
```

---

## Chunk 2: Subclasses, Exports, and E2E Tests

### Task 3: Create NairabetAltenar and BetkingAltenar subclasses

**Files:**
- Create: `NaijaBet_Api/bookmakers/nairabet_altenar.py`
- Create: `NaijaBet_Api/bookmakers/betking_altenar.py`
- Test: `tests/test_altenar_e2e.py`

- [ ] **Step 1: Write failing E2E tests**

Append to `tests/test_altenar_e2e.py`:

```python
from NaijaBet_Api.bookmakers.nairabet_altenar import NairabetAltenar
from NaijaBet_Api.bookmakers.betking_altenar import BetkingAltenar


class TestNairabetAltenarE2E:
    """Live E2E tests for NairabetAltenar"""

    def test_initialization(self):
        nb = NairabetAltenar()
        assert nb._integration == "nairabet"
        assert nb.session is not None

    def test_initialization_with_proxy(self):
        nb = NairabetAltenar(proxies={"https": "http://proxy:8080"})
        assert nb.session.proxies == {"https": "http://proxy:8080"}

    @pytest.mark.timeout(30)
    def test_get_league_premier_league(self):
        nb = NairabetAltenar()
        data = nb.get_league(Betid.PREMIERLEAGUE)
        assert isinstance(data, list)
        if len(data) > 0:
            match = data[0]
            assert "match" in match
            assert "home" in match
            assert "draw" in match
            assert "away" in match
            assert "time" in match
            assert "league" in match
            assert isinstance(match["home"], float)
            assert isinstance(match["time"], int)

    @pytest.mark.timeout(30)
    def test_get_league_la_liga(self):
        nb = NairabetAltenar()
        data = nb.get_league(Betid.LALIGA)
        assert isinstance(data, list)

    @pytest.mark.timeout(60)
    def test_get_all(self):
        nb = NairabetAltenar()
        data = nb.get_all()
        assert isinstance(data, list)


class TestBetkingAltenarE2E:
    """Live E2E tests for BetkingAltenar"""

    def test_initialization(self):
        bk = BetkingAltenar()
        assert bk._integration == "betking"

    @pytest.mark.timeout(30)
    def test_get_league_premier_league(self):
        bk = BetkingAltenar()
        data = bk.get_league(Betid.PREMIERLEAGUE)
        assert isinstance(data, list)
        if len(data) > 0:
            match = data[0]
            assert "match" in match
            assert "home" in match
            assert "draw" in match
            assert "away" in match
            assert isinstance(match["home"], float)

    @pytest.mark.timeout(30)
    def test_get_league_bundesliga(self):
        bk = BetkingAltenar()
        data = bk.get_league(Betid.BUNDESLIGA)
        assert isinstance(data, list)

    @pytest.mark.timeout(60)
    def test_get_all(self):
        bk = BetkingAltenar()
        data = bk.get_all()
        assert isinstance(data, list)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/Scripts/python -m pytest tests/test_altenar_e2e.py::TestNairabetAltenarE2E::test_initialization -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement NairabetAltenar**

Create `NaijaBet_Api/bookmakers/nairabet_altenar.py`:

```python
from NaijaBet_Api.bookmakers.altenar_base import AltenarBaseClass


class NairabetAltenar(AltenarBaseClass):
    _site = 'nairabet_altenar'
    _url = 'https://nairabet.com'
    _integration = 'nairabet'
```

- [ ] **Step 4: Implement BetkingAltenar**

Create `NaijaBet_Api/bookmakers/betking_altenar.py`:

```python
from NaijaBet_Api.bookmakers.altenar_base import AltenarBaseClass


class BetkingAltenar(AltenarBaseClass):
    _site = 'betking_altenar'
    _url = 'https://betking.com'
    _integration = 'betking'
```

- [ ] **Step 5: Run E2E tests**

Run: `.venv/Scripts/python -m pytest tests/test_altenar_e2e.py -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add NaijaBet_Api/bookmakers/nairabet_altenar.py NaijaBet_Api/bookmakers/betking_altenar.py tests/test_altenar_e2e.py
git commit -m "feat: add NairabetAltenar and BetkingAltenar subclasses"
```

---

### Task 4: Update bookmakers __init__.py exports

**Files:**
- Modify: `NaijaBet_Api/bookmakers/__init__.py`

- [ ] **Step 1: Update exports**

```python
"""Bookmakers module

Available bookmakers:
- Bet9ja: Full support, no browser automation needed
- Betking: Standard version (Cloudflare blocked), Playwright version available
- BetkingAltenar: Betking via Altenar API, no browser needed
- Nairabet: Legacy (API dead)
- NairabetAltenar: Nairabet via Altenar API
"""

from .bet9ja import Bet9ja
from .betking import Betking
from .nairabet import Nairabet
from .nairabet_altenar import NairabetAltenar
from .betking_altenar import BetkingAltenar

# Playwright version (optional - only if playwright installed)
try:
    from .betking_playwright import BetkingPlaywright
    __all__ = ['Bet9ja', 'Betking', 'Nairabet', 'BetkingPlaywright',
               'NairabetAltenar', 'BetkingAltenar']
except ImportError:
    __all__ = ['Bet9ja', 'Betking', 'Nairabet',
               'NairabetAltenar', 'BetkingAltenar']
```

- [ ] **Step 2: Verify imports work**

Run: `.venv/Scripts/python -c "from NaijaBet_Api.bookmakers import NairabetAltenar, BetkingAltenar; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Run full test suite to ensure nothing is broken**

Run: `.venv/Scripts/python -m pytest tests/ -v`
Expected: All existing tests still pass, new tests pass

- [ ] **Step 4: Commit**

```bash
git add NaijaBet_Api/bookmakers/__init__.py
git commit -m "feat: export NairabetAltenar and BetkingAltenar from bookmakers module"
```
