"""
E2E test for 22bet — one real API call, validates all odds fields.
"""
import pytest
from NaijaBet_Api.bookmakers.twentytwobet import TwentyTwoBet, ODDS_MAP
from NaijaBet_Api.id import Betid

REQUIRED_FIELDS = ['match', 'league', 'time', 'league_id', 'match_id']
ODDS_1X2 = ['home', 'draw', 'away']
ODDS_DC = ['home_or_draw', 'home_or_away', 'draw_or_away']
ODDS_OU = ['over_2_5', 'under_2_5']
ODDS_BTTS = ['btts_yes', 'btts_no']


# --- Unit tests (no network) ---

class TestTwentyTwoBetNormalizer:

    def test_normalizer_empty_input(self):
        tb = TwentyTwoBet()
        assert tb.normalizer(None) == []
        assert tb.normalizer({}) == []
        assert tb.normalizer({"Value": []}) == []

    def test_normalizer_parses_match_data(self):
        tb = TwentyTwoBet()
        mock_response = {
            "Value": [{
                "O1": "Arsenal", "O2": "Chelsea",
                "S": 1773509400, "I": 700169162,
                "L": "England. Premier League", "LI": 88637,
                "E": [
                    {"G": 1, "T": 1, "C": 1.5},
                    {"G": 1, "T": 2, "C": 4.0},
                    {"G": 1, "T": 3, "C": 6.5},
                    {"G": 8, "T": 4, "C": 1.1},
                    {"G": 8, "T": 5, "C": 2.5},
                    {"G": 8, "T": 6, "C": 1.3},
                    {"G": 17, "T": 9, "C": 1.8, "P": 2.5},
                    {"G": 17, "T": 10, "C": 2.1, "P": 2.5},
                    {"G": 19, "T": 180, "C": 1.6},
                    {"G": 19, "T": 181, "C": 2.2},
                ],
            }]
        }
        result = tb.normalizer(mock_response)
        assert len(result) == 1
        m = result[0]
        assert m["match"] == "Arsenal - Chelsea"
        assert m["home"] == 1.5
        assert m["draw"] == 4.0
        assert m["away"] == 6.5
        assert m["home_or_draw"] == 1.1
        assert m["draw_or_away"] == 2.5
        assert m["home_or_away"] == 1.3
        assert m["over_2_5"] == 1.8
        assert m["under_2_5"] == 2.1
        assert m["btts_yes"] == 1.6
        assert m["btts_no"] == 2.2

    def test_normalizer_skips_events_without_teams(self):
        tb = TwentyTwoBet()
        mock_response = {
            "Value": [
                {"O1": "", "O2": "Chelsea", "S": 0, "I": 1, "L": "Test", "LI": 1, "E": []},
                {"O1": "Arsenal", "O2": "", "S": 0, "I": 2, "L": "Test", "LI": 1, "E": []},
            ]
        }
        assert len(tb.normalizer(mock_response)) == 0


# --- E2E ---

class TestTwentyTwoBetE2E:

    @pytest.fixture(scope="class")
    def league_data(self):
        return TwentyTwoBet().get_league(Betid.PREMIERLEAGUE)

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
