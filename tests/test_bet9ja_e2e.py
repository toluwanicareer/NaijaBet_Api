"""
E2E test for Bet9ja — one real API call, validates all odds fields.
"""
import pytest
from NaijaBet_Api.bookmakers.bet9ja import Bet9ja
from NaijaBet_Api.id import Betid

REQUIRED_FIELDS = ['match', 'league', 'time', 'league_id', 'match_id']
ODDS_1X2 = ['home', 'draw', 'away']
ODDS_DC = ['home_or_draw', 'home_or_away', 'draw_or_away']
ODDS_OU = ['over_2_5', 'under_2_5']
ODDS_BTTS = ['btts_yes', 'btts_no']


class TestBet9jaE2E:

    @pytest.fixture(scope="class")
    def league_data(self):
        bookmaker = Bet9ja()
        return bookmaker.get_league(Betid.PREMIERLEAGUE)

    def test_returns_list(self, league_data):
        assert isinstance(league_data, list)

    def test_has_matches(self, league_data):
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
            assert isinstance(match[field], (int, float)), f"{field} not numeric"
            assert match[field] > 1.0, f"{field}={match[field]} should be > 1.0"

    def test_double_chance_odds(self, league_data):
        match = league_data[0]
        for field in ODDS_DC:
            assert field in match, f"Missing '{field}'"
            assert isinstance(match[field], (int, float)), f"{field} not numeric"
            assert match[field] > 1.0, f"{field}={match[field]} should be > 1.0"

    def test_over_under_odds(self, league_data):
        match = league_data[0]
        for field in ODDS_OU:
            assert field in match, f"Missing '{field}'"
            assert isinstance(match[field], (int, float)), f"{field} not numeric"
            assert match[field] > 1.0, f"{field}={match[field]} should be > 1.0"

        # Bet9ja extracts O/U lines via JMESPath (0.5 through 6.5)
        ou_keys = [k for k in match if k.startswith("over_") or k.startswith("under_")]
        assert len(ou_keys) >= 4, f"Expected multiple O/U lines, got {ou_keys}"

    def test_btts_odds(self, league_data):
        match = league_data[0]
        for field in ODDS_BTTS:
            assert field in match, f"Missing '{field}'"
            assert isinstance(match[field], (int, float)), f"{field} not numeric"
            assert match[field] > 1.0, f"{field}={match[field]} should be > 1.0"

    def test_corners_odds(self, league_data):
        match = league_data[0]
        corner_keys = [k for k in match if k.startswith("corners_")]
        assert len(corner_keys) >= 2, f"Expected corners odds, got {corner_keys}"
        over_keys = [k for k in corner_keys if "over" in k]
        under_keys = [k for k in corner_keys if "under" in k]
        assert len(over_keys) >= 1, "No corners over lines found"
        assert len(under_keys) >= 1, "No corners under lines found"
        for k in corner_keys:
            assert isinstance(match[k], (int, float)), f"{k} not numeric"
            assert match[k] > 1.0, f"{k}={match[k]} should be > 1.0"

    def test_all_odds_summary(self, league_data):
        """Print a summary of the first match for manual verification."""
        match = league_data[0]
        all_odds = ODDS_1X2 + ODDS_DC + ODDS_OU + ODDS_BTTS
        present = [f for f in all_odds if f in match]
        missing = [f for f in all_odds if f not in match]
        ou_keys = sorted([k for k in match if k.startswith("over_") or k.startswith("under_")])
        corner_keys = sorted([k for k in match if k.startswith("corners_")])
        print(f"\n  Match: {match['match']}")
        print(f"  League: {match['league']}")
        print(f"  Present: {present}")
        print(f"  Missing: {missing}")
        print(f"  O/U lines: {ou_keys}")
        print(f"  Corners lines ({len(corner_keys)}): {corner_keys}")
        assert len(missing) == 0, f"Missing odds fields: {missing}"
