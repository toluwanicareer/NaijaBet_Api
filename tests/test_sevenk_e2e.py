"""
E2E test for 7k.bet (SevenKBet) — real API calls, validates all odds fields.

Uses 442hattrick REST API (no browser needed).
"""
import pytest
from NaijaBet_Api.bookmakers.sevenk import SevenKBet, _extract_odds
from NaijaBet_Api.id import Betid

REQUIRED_FIELDS = ['match', 'league', 'match_id']
ODDS_1X2 = ['home', 'draw', 'away']
ODDS_DC = ['home_or_draw', 'home_or_away', 'draw_or_away']
ODDS_OU = ['over_2_5', 'under_2_5']
ODDS_BTTS = ['btts_yes', 'btts_no']


class TestExtractOdds:
    """Unit tests for _extract_odds (no network)."""

    def test_extracts_1x2(self):
        markets = [["id", "FT 1X2", None, "FT 1X2", None, ["ML0"], "ev", "lg", "1", "date", 3, None, "",
                     [
                         ["H", "Home", "Home", "1X2", None, False, 1.5, False, [], 1, 1, {"EN": "Home"}, "id"],
                         ["D", "Draw", "Draw", "1X2", None, False, 3.5, False, [], 2, 1, {"EN": "Tie"}, "id"],
                         ["A", "Away", "Away", "1X2", None, False, 5.0, False, [], 3, 1, {"EN": "Away"}, "id"],
                     ]]]
        odds = _extract_odds(markets)
        assert odds["home"] == 1.5
        assert odds["draw"] == 3.5
        assert odds["away"] == 5.0

    def test_extracts_btts(self):
        markets = [["id", "Both Teams To Score", None, "BTTS", None, ["QA158"], "ev", "lg", "1", "date", 2, None, "",
                     [
                         ["Y", {"EN": "Yes"}, {"EN": "Yes"}, "BTTS", None, False, 1.8, False, [], 1, 0, {}, "id"],
                         ["N", {"EN": "No"}, {"EN": "No"}, "BTTS", None, False, 2.0, False, [], 3, 0, {}, "id"],
                     ]]]
        odds = _extract_odds(markets)
        assert odds["btts_yes"] == 1.8
        assert odds["btts_no"] == 2.0

    def test_skips_suspended(self):
        markets = [["id", "FT 1X2", None, "FT 1X2", None, ["ML0"], "ev", "lg", "1", "date", 3, None, "",
                     [
                         ["H", "Home", "Home", "1X2", None, True, 0, True, [], 1, 1, {"EN": "Home"}, "id"],
                     ]]]
        odds = _extract_odds(markets)
        assert "home" not in odds


class TestSevenKBetFast:
    """Test fast listing (no odds)."""

    @pytest.fixture(scope="class")
    def league_data(self):
        return SevenKBet().get_league_fast(Betid.PREMIERLEAGUE)

    def test_returns_list(self, league_data):
        assert isinstance(league_data, list)

    def test_has_matches(self, league_data):
        assert len(league_data) > 0, "Expected at least one match"

    def test_match_structure(self, league_data):
        match = league_data[0]
        for field in REQUIRED_FIELDS:
            assert field in match, f"Missing '{field}'"
        assert ' - ' in match['match']


class TestSevenKBetDetail:
    """Test full odds extraction (1X2, DC, O/U, BTTS)."""

    @pytest.fixture(scope="class")
    def match_data(self):
        data = SevenKBet().get_league(Betid.PREMIERLEAGUE)
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

    def test_corners_odds(self, match_data):
        corner_keys = [k for k in match_data if k.startswith("corners_")]
        assert len(corner_keys) >= 2, f"Expected corners odds, got {corner_keys}"
        over_keys = [k for k in corner_keys if "over" in k]
        under_keys = [k for k in corner_keys if "under" in k]
        assert len(over_keys) >= 1, "No corners over lines found"
        assert len(under_keys) >= 1, "No corners under lines found"
        for k in corner_keys:
            assert isinstance(match_data[k], (int, float)), f"{k} not numeric"
            assert match_data[k] > 1.0, f"{k}={match_data[k]} should be > 1.0"

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
