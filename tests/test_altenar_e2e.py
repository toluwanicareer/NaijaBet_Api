"""
E2E tests for Altenar-based bookmakers (NairabetAltenar, BetkingAltenar).
One real API call each, validates all odds fields including multiple O/U lines.
"""
import pytest
from NaijaBet_Api.id import Betid
from NaijaBet_Api.bookmakers.altenar_base import AltenarBaseClass
from NaijaBet_Api.bookmakers.nairabet_altenar import NairabetAltenar
from NaijaBet_Api.bookmakers.betking_altenar import BetkingAltenar

REQUIRED_FIELDS = ['match', 'league', 'time', 'league_id', 'match_id']
ODDS_1X2 = ['home', 'draw', 'away']
ODDS_DC = ['home_or_draw', 'home_or_away', 'draw_or_away']
ODDS_OU = ['over_2_5', 'under_2_5']
ODDS_BTTS = ['btts_yes', 'btts_no']


# --- Unit tests (no network) ---

class TestAltenarNormalizer:

    def test_normalizer_empty_input(self):
        class FakeAltenar(AltenarBaseClass):
            _site = 'fake'
            _url = 'https://example.com'
            _integration = 'fake'
        fa = FakeAltenar()
        assert fa.normalizer(None) == []
        assert fa.normalizer({"events": [], "odds": [], "markets": []}) == []

    def test_normalizer_joins_data(self):
        class FakeAltenar(AltenarBaseClass):
            _site = 'fake'
            _url = 'https://example.com'
            _integration = 'fake'
        fa = FakeAltenar()

        mock_response = {
            "events": [{
                "id": 100, "name": "Team A vs. Team B",
                "startDate": "2026-03-14T15:00:00Z",
                "champId": 2936, "marketIds": [1, 2, 3, 4],
            }],
            "markets": [
                {"id": 1, "oddIds": [10, 11, 12], "typeId": 1},
                {"id": 2, "oddIds": [20, 21, 22], "typeId": 10},
                {"id": 3, "oddIds": [30, 31], "typeId": 18, "sv": "2.5"},
                {"id": 4, "oddIds": [40, 41], "typeId": 29},
            ],
            "odds": [
                {"id": 10, "typeId": 1, "price": 2.5},
                {"id": 11, "typeId": 2, "price": 3.0},
                {"id": 12, "typeId": 3, "price": 2.8},
                {"id": 20, "typeId": 9, "price": 1.5},
                {"id": 21, "typeId": 10, "price": 1.3},
                {"id": 22, "typeId": 11, "price": 1.4},
                {"id": 30, "typeId": 12, "price": 1.72},
                {"id": 31, "typeId": 13, "price": 2.13},
                {"id": 40, "typeId": 74, "price": 1.65},
                {"id": 41, "typeId": 76, "price": 2.20},
            ],
            "champs": [{"id": 2936, "name": "Premier League"}],
        }

        result = fa.normalizer(mock_response)
        assert len(result) == 1
        m = result[0]
        assert m["match"] == "Team A - Team B"
        assert m["home"] == 2.5
        assert m["draw"] == 3.0
        assert m["away"] == 2.8
        assert m["home_or_draw"] == 1.5
        assert m["home_or_away"] == 1.3
        assert m["draw_or_away"] == 1.4
        assert m["over_2_5"] == 1.72
        assert m["under_2_5"] == 2.13
        assert m["btts_yes"] == 1.65
        assert m["btts_no"] == 2.20


# --- E2E: NairabetAltenar ---

class TestNairabetAltenarE2E:

    @pytest.fixture(scope="class")
    def league_data(self):
        return NairabetAltenar().get_league(Betid.PREMIERLEAGUE)

    def test_returns_list_with_matches(self, league_data):
        assert isinstance(league_data, list)
        assert len(league_data) > 0, "Expected at least one match"

    def test_match_structure(self, league_data):
        match = league_data[0]
        for field in REQUIRED_FIELDS:
            assert field in match, f"Missing '{field}'"
        assert ' - ' in match['match']
        assert isinstance(match['time'], int)

    def test_1x2_odds(self, league_data):
        match = league_data[0]
        for field in ODDS_1X2:
            assert field in match, f"Missing '{field}'"
            assert isinstance(match[field], float)
            assert match[field] > 1.0

    def test_double_chance_odds(self, league_data):
        match = league_data[0]
        for field in ODDS_DC:
            assert field in match, f"Missing '{field}'"
            assert isinstance(match[field], float)
            assert match[field] > 1.0

    def test_over_under_multiple_lines(self, league_data):
        match = league_data[0]
        for field in ODDS_OU:
            assert field in match, f"Missing '{field}'"
            assert isinstance(match[field], float)
            assert match[field] > 1.0
        ou_keys = [k for k in match if k.startswith("over_") or k.startswith("under_")]
        assert len(ou_keys) > 4, f"Expected multiple O/U lines, got {ou_keys}"

    def test_btts_odds(self, league_data):
        match = league_data[0]
        for field in ODDS_BTTS:
            assert field in match, f"Missing '{field}'"
            assert isinstance(match[field], float)
            assert match[field] > 1.0

    def test_all_odds_summary(self, league_data):
        match = league_data[0]
        all_odds = ODDS_1X2 + ODDS_DC + ODDS_OU + ODDS_BTTS
        missing = [f for f in all_odds if f not in match]
        ou_keys = sorted([k for k in match if k.startswith("over_") or k.startswith("under_")])
        print(f"\n  Match: {match['match']}")
        print(f"  O/U lines ({len(ou_keys)}): {ou_keys}")
        assert len(missing) == 0, f"Missing odds fields: {missing}"


# --- E2E: BetkingAltenar ---

class TestBetkingAltenarE2E:

    @pytest.fixture(scope="class")
    def league_data(self):
        return BetkingAltenar().get_league(Betid.PREMIERLEAGUE)

    def test_returns_list_with_matches(self, league_data):
        assert isinstance(league_data, list)
        assert len(league_data) > 0, "Expected at least one match"

    def test_match_structure(self, league_data):
        match = league_data[0]
        for field in REQUIRED_FIELDS:
            assert field in match, f"Missing '{field}'"
        assert ' - ' in match['match']
        assert isinstance(match['time'], int)

    def test_1x2_odds(self, league_data):
        match = league_data[0]
        for field in ODDS_1X2:
            assert field in match, f"Missing '{field}'"
            assert isinstance(match[field], float)
            assert match[field] > 1.0

    def test_double_chance_odds(self, league_data):
        match = league_data[0]
        for field in ODDS_DC:
            assert field in match, f"Missing '{field}'"
            assert isinstance(match[field], float)
            assert match[field] > 1.0

    def test_over_under_multiple_lines(self, league_data):
        match = league_data[0]
        for field in ODDS_OU:
            assert field in match, f"Missing '{field}'"
            assert isinstance(match[field], float)
            assert match[field] > 1.0
        ou_keys = [k for k in match if k.startswith("over_") or k.startswith("under_")]
        assert len(ou_keys) > 4, f"Expected multiple O/U lines, got {ou_keys}"

    def test_btts_odds(self, league_data):
        match = league_data[0]
        for field in ODDS_BTTS:
            assert field in match, f"Missing '{field}'"
            assert isinstance(match[field], float)
            assert match[field] > 1.0

    def test_all_odds_summary(self, league_data):
        match = league_data[0]
        all_odds = ODDS_1X2 + ODDS_DC + ODDS_OU + ODDS_BTTS
        missing = [f for f in all_odds if f not in match]
        ou_keys = sorted([k for k in match if k.startswith("over_") or k.startswith("under_")])
        print(f"\n  Match: {match['match']}")
        print(f"  O/U lines ({len(ou_keys)}): {ou_keys}")
        assert len(missing) == 0, f"Missing odds fields: {missing}"
