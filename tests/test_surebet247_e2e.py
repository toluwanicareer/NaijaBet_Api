"""
E2E test for Surebet247 — real WebSocket calls, validates all odds fields.

Uses direct WebSocket connection to GR8 Tech SignalR feed (no browser needed).
"""
import pytest
from NaijaBet_Api.bookmakers.surebet247 import Surebet247
from NaijaBet_Api.id import Betid

REQUIRED_FIELDS = ['match', 'league', 'match_id']
ODDS_1X2 = ['home', 'draw', 'away']
ODDS_DC = ['home_or_draw', 'home_or_away', 'draw_or_away']
ODDS_OU = ['over_2_5', 'under_2_5']
ODDS_BTTS = ['btts_yes', 'btts_no']


class TestSurebet247Fast:
    """Test fast listing (1X2 only)."""

    @pytest.fixture(scope="class")
    def league_data(self):
        with Surebet247() as sb:
            return sb.get_league_fast(Betid.PREMIERLEAGUE)

    def test_returns_list(self, league_data):
        assert isinstance(league_data, list)

    def test_has_matches(self, league_data):
        assert len(league_data) > 0, "Expected at least one match"

    def test_match_structure(self, league_data):
        match = league_data[0]
        for field in REQUIRED_FIELDS:
            assert field in match, f"Missing '{field}'"
        assert ' - ' in match['match']

    def test_1x2_odds(self, league_data):
        match = league_data[0]
        for field in ODDS_1X2:
            assert field in match, f"Missing '{field}'"
            assert isinstance(match[field], (int, float)), f"{field} not numeric"
            assert match[field] > 1.0, f"{field}={match[field]} should be > 1.0"


class TestSurebet247Detail:
    """Test full odds extraction (1X2, DC, O/U, BTTS)."""

    @pytest.fixture(scope="class")
    def match_data(self):
        with Surebet247() as sb:
            data = sb.get_league(Betid.PREMIERLEAGUE)
            assert len(data) > 0, "No matches found"
            return data[0]

    def test_1x2_odds(self, match_data):
        for field in ODDS_1X2:
            assert field in match_data, f"Missing '{field}'"
            assert isinstance(match_data[field], (int, float))
            assert match_data[field] > 1.0

    def test_double_chance_odds(self, match_data):
        for field in ODDS_DC:
            assert field in match_data, f"Missing '{field}'"
            assert isinstance(match_data[field], (int, float))
            assert match_data[field] > 1.0

    def test_over_under_odds(self, match_data):
        for field in ODDS_OU:
            assert field in match_data, f"Missing '{field}'"
            assert isinstance(match_data[field], (int, float))
            assert match_data[field] > 1.0

        ou_keys = [k for k in match_data if k.startswith("over_") or k.startswith("under_")]
        assert len(ou_keys) >= 10, f"Expected 10+ O/U lines, got {len(ou_keys)}: {ou_keys}"

    def test_btts_odds(self, match_data):
        for field in ODDS_BTTS:
            assert field in match_data, f"Missing '{field}'"
            assert isinstance(match_data[field], (int, float))
            assert match_data[field] > 1.0

    @pytest.fixture(scope="class")
    def league_data(self):
        with Surebet247() as sb:
            return sb.get_league(Betid.PREMIERLEAGUE)

    def test_corners_odds(self, league_data):
        """At least one match in the league should have corners odds."""
        for match in league_data:
            corner_keys = [k for k in match if k.startswith("corners_")]
            if corner_keys:
                for k in corner_keys:
                    assert isinstance(match[k], (int, float)), f"{k} not numeric"
                    assert match[k] > 1.0, f"{k}={match[k]} should be > 1.0"
                return
        pytest.fail(f"No match in {len(league_data)} results has corners odds")

    def test_all_odds_summary(self, match_data):
        """Print summary for manual verification."""
        all_odds = ODDS_1X2 + ODDS_DC + ODDS_OU + ODDS_BTTS
        present = [f for f in all_odds if f in match_data]
        missing = [f for f in all_odds if f not in match_data]
        ou_keys = sorted([k for k in match_data if k.startswith("over_") or k.startswith("under_")])
        corner_keys = sorted([k for k in match_data if k.startswith("corners_")])
        print(f"\n  Match: {match_data['match']}")
        print(f"  1X2: H={match_data.get('home')} D={match_data.get('draw')} A={match_data.get('away')}")
        print(f"  DC: {match_data.get('home_or_draw')} / {match_data.get('home_or_away')} / {match_data.get('draw_or_away')}")
        print(f"  BTTS: Y={match_data.get('btts_yes')} N={match_data.get('btts_no')}")
        print(f"  O/U lines ({len(ou_keys)}): {ou_keys}")
        print(f"  Corners lines ({len(corner_keys)}): {corner_keys}")
        print(f"  Present: {present}")
        print(f"  Missing: {missing}")
        assert len(missing) == 0, f"Missing odds fields: {missing}"
