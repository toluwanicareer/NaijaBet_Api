"""
E2E test for LivescoreBet — real API calls, validates all odds fields.
"""
import pytest
from NaijaBet_Api.bookmakers.livescorebet import LivescoreBet, _parse_events
from NaijaBet_Api.id import Betid

REQUIRED_FIELDS = ['match', 'league', 'time', 'league_id', 'match_id']
ODDS_1X2 = ['home', 'draw', 'away']
ODDS_DC = ['home_or_draw', 'home_or_away', 'draw_or_away']
ODDS_OU = ['over_2_5', 'under_2_5']
ODDS_BTTS = ['btts_yes', 'btts_no']


# --- Unit tests (no network) ---

class TestParseEvents:

    def test_empty_input(self):
        assert _parse_events({}) == []
        assert _parse_events({"events": {}}) == []
        assert _parse_events({"events": {"categories": []}}) == []

    def test_parses_match_with_odds(self):
        data = {
            "events": {"categories": [{
                "name": "England - Premier League",
                "originalId": "1000094985",
                "events": [{
                    "originalId": "1024043969",
                    "state": "NOTSTARTED",
                    "startTime": "2026-03-14 15:00:00",
                    "participants": [
                        {"name": "Arsenal", "venueRole": "Home"},
                        {"name": "Chelsea", "venueRole": "Away"},
                    ],
                    "markets": [
                        {
                            "name": "Full Time",
                            "periodType": "FT",
                            "selections": [
                                {"name": "Arsenal", "odds": 1.5},
                                {"name": "Draw", "odds": 4.0},
                                {"name": "Chelsea", "odds": 6.5},
                            ],
                        },
                        {
                            "name": "Double Chance",
                            "periodType": "FT",
                            "selections": [
                                {"name": "Arsenal or Draw", "odds": 1.1},
                                {"name": "Arsenal or Chelsea", "odds": 1.3},
                                {"name": "Draw or Chelsea", "odds": 2.5},
                            ],
                        },
                        {
                            "name": "Both Teams To Score",
                            "periodType": "FT",
                            "selections": [
                                {"name": "Yes", "odds": 1.6},
                                {"name": "No", "odds": 2.2},
                            ],
                        },
                        {
                            "name": "Total Goals",
                            "periodType": "FT",
                            "selections": [
                                {"name": "Over 2.5", "odds": 1.8},
                                {"name": "Under 2.5", "odds": 2.1},
                            ],
                        },
                    ],
                }],
            }]},
        }
        result = _parse_events(data)
        assert len(result) == 1
        m = result[0]
        assert m["match"] == "Arsenal - Chelsea"
        assert m["league"] == "England - Premier League"
        assert m["home"] == 1.5
        assert m["draw"] == 4.0
        assert m["away"] == 6.5
        assert m["home_or_draw"] == 1.1
        assert m["home_or_away"] == 1.3
        assert m["draw_or_away"] == 2.5
        assert m["btts_yes"] == 1.6
        assert m["btts_no"] == 2.2
        assert m["over_2_5"] == 1.8
        assert m["under_2_5"] == 2.1

    def test_skips_started_events(self):
        data = {
            "events": {"categories": [{
                "name": "Test",
                "originalId": "1",
                "events": [{
                    "originalId": "1",
                    "state": "STARTED",
                    "startTime": "2026-03-14 15:00:00",
                    "participants": [
                        {"name": "A", "venueRole": "Home"},
                        {"name": "B", "venueRole": "Away"},
                    ],
                    "markets": [],
                }],
            }]},
        }
        assert _parse_events(data) == []


# --- E2E ---

class TestLivescoreBetE2E:

    @pytest.fixture(scope="class")
    def league_data(self):
        return LivescoreBet().get_league(Betid.PREMIERLEAGUE)

    def test_returns_list_with_matches(self, league_data):
        assert isinstance(league_data, list)
        assert len(league_data) > 0, "Expected at least one match"

    def test_match_structure(self, league_data):
        match = league_data[0]
        for field in REQUIRED_FIELDS:
            assert field in match, f"Missing '{field}'"
        assert ' - ' in match['match']
        assert isinstance(match['time'], int)
        assert isinstance(match['league_id'], int)
        assert isinstance(match['match_id'], int)

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
