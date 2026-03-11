"""
End-to-end tests for 22bet bookmaker.
These tests make real API calls to verify the actual functionality.
"""
import pytest
from NaijaBet_Api.bookmakers.twentytwobet import TwentyTwoBet, ODDS_MAP
from NaijaBet_Api.id import Betid


class TestTwentyTwoBetIds:
    """Test that Betid enum has 22bet IDs"""

    def test_betid_has_twentytwobet_id(self):
        assert hasattr(Betid.PREMIERLEAGUE, 'twentytwobet_id')
        assert Betid.PREMIERLEAGUE.twentytwobet_id == 88637

    def test_all_leagues_have_twentytwobet_id(self):
        for league in Betid:
            assert isinstance(league.twentytwobet_id, int), f"{league.name} missing twentytwobet_id"

    def test_to_endpoint_twentytwobet(self):
        url = Betid.PREMIERLEAGUE.to_endpoint('twentytwobet')
        assert '22bet.ng' in url
        assert 'champs=88637' in url


class TestTwentyTwoBetNormalizer:
    """Unit tests for normalizer logic"""

    def test_normalizer_empty_input(self):
        tb = TwentyTwoBet()
        assert tb.normalizer(None) == []
        assert tb.normalizer({}) == []
        assert tb.normalizer({"Value": []}) == []

    def test_normalizer_parses_match_data(self):
        tb = TwentyTwoBet()
        mock_response = {
            "Value": [{
                "O1": "Arsenal",
                "O2": "Chelsea",
                "S": 1773509400,
                "I": 700169162,
                "L": "England. Premier League",
                "LI": 88637,
                "E": [
                    {"G": 1, "T": 1, "C": 1.5},
                    {"G": 1, "T": 2, "C": 4.0},
                    {"G": 1, "T": 3, "C": 6.5},
                    {"G": 8, "T": 4, "C": 1.1},
                    {"G": 8, "T": 5, "C": 2.5},
                    {"G": 8, "T": 6, "C": 1.3},
                    {"G": 17, "T": 9, "C": 1.8, "P": 2.5},
                    {"G": 17, "T": 10, "C": 2.1, "P": 2.5},
                    {"G": 17, "T": 9, "C": 1.2, "P": 1.5},
                    {"G": 19, "T": 180, "C": 1.6},
                    {"G": 19, "T": 181, "C": 2.2},
                ],
            }]
        }

        result = tb.normalizer(mock_response)
        assert len(result) == 1
        match = result[0]
        assert match["match"] == "Arsenal - Chelsea"
        assert match["league"] == "England. Premier League"
        assert match["time"] == 1773509400
        assert match["match_id"] == 700169162
        assert match["league_id"] == 88637
        assert match["home"] == 1.5
        assert match["draw"] == 4.0
        assert match["away"] == 6.5
        assert match["home_or_draw"] == 1.1
        assert match["draw_or_away"] == 2.5
        assert match["home_or_away"] == 1.3
        assert match["over_2_5"] == 1.8
        assert match["under_2_5"] == 2.1
        assert match["btts_yes"] == 1.6
        assert match["btts_no"] == 2.2
        # Over 1.5 should NOT be included
        assert "over_1_5" not in match

    def test_normalizer_skips_events_without_teams(self):
        tb = TwentyTwoBet()
        mock_response = {
            "Value": [
                {"O1": "", "O2": "Chelsea", "S": 0, "I": 1, "L": "Test", "LI": 1, "E": []},
                {"O1": "Arsenal", "O2": "", "S": 0, "I": 2, "L": "Test", "LI": 1, "E": []},
            ]
        }
        result = tb.normalizer(mock_response)
        assert len(result) == 0


class TestTwentyTwoBetE2E:
    """Live E2E tests for 22bet bookmaker"""

    def test_initialization(self):
        bookmaker = TwentyTwoBet()
        assert bookmaker is not None
        assert bookmaker.site == 'twentytwobet'
        assert bookmaker.session is not None

    def test_initialization_with_proxy(self):
        bookmaker = TwentyTwoBet(proxies={"https": "http://proxy:8080"})
        assert bookmaker.session.proxies == {"https": "http://proxy:8080"}

    @pytest.mark.timeout(120)
    def test_get_league_premier_league(self):
        bookmaker = TwentyTwoBet()
        data = bookmaker.get_league(Betid.PREMIERLEAGUE)

        assert isinstance(data, list), "get_league should return a list"

        if len(data) > 0:
            match = data[0]
            required_fields = ['match', 'league', 'time', 'league_id', 'match_id']
            for field in required_fields:
                assert field in match, f"Match should have '{field}' field"

            assert isinstance(match['match'], str), "match should be a string"
            assert ' - ' in match['match'], "match should contain ' - ' separator"
            assert isinstance(match['league'], str), "league should be a string"
            assert isinstance(match['time'], int), "time should be an integer timestamp"
            assert isinstance(match['league_id'], int), "league_id should be an integer"
            assert isinstance(match['match_id'], int), "match_id should be an integer"

            # Check odds fields
            odds_fields = ['home', 'draw', 'away']
            for field in odds_fields:
                if field in match:
                    assert isinstance(match[field], (int, float)), f"{field} should be numeric"
                    assert match[field] > 0, f"{field} should be positive"

            # Check extended odds if present
            extended_fields = ['home_or_draw', 'home_or_away', 'draw_or_away',
                               'over_2_5', 'under_2_5', 'btts_yes', 'btts_no']
            for field in extended_fields:
                if field in match:
                    assert isinstance(match[field], (int, float)), f"{field} should be numeric"
                    assert match[field] > 0, f"{field} should be positive"

            # Should have multiple over/under lines from event details
            ou_keys = [k for k in match if k.startswith("over_") or k.startswith("under_")]
            assert len(ou_keys) > 4, f"Expected multiple O/U lines, got {ou_keys}"

    @pytest.mark.timeout(120)
    def test_get_league_la_liga(self):
        bookmaker = TwentyTwoBet()
        data = bookmaker.get_league(Betid.LALIGA)
        assert isinstance(data, list), "get_league should return a list"

    @pytest.mark.timeout(120)
    def test_get_league_bundesliga(self):
        bookmaker = TwentyTwoBet()
        data = bookmaker.get_league(Betid.BUNDESLIGA)
        assert isinstance(data, list), "get_league should return a list"

    @pytest.mark.timeout(600)
    def test_get_all(self):
        bookmaker = TwentyTwoBet()
        data = bookmaker.get_all()

        assert isinstance(data, list), "get_all should return a list"

        if len(data) > 0:
            match = data[0]
            required_fields = ['match', 'league', 'time', 'league_id', 'match_id']
            for field in required_fields:
                assert field in match, f"Match should have '{field}' field"

    @pytest.mark.timeout(600)
    def test_get_team(self):
        bookmaker = TwentyTwoBet()
        data = bookmaker.get_team("Arsenal")
        assert isinstance(data, list), "get_team should return a list"
        for match in data:
            assert 'Arsenal' in match['match'], "Match should contain team name"

    @pytest.mark.timeout(120)
    def test_multiple_requests(self):
        bookmaker = TwentyTwoBet()
        data1 = bookmaker.get_league(Betid.PREMIERLEAGUE)
        data2 = bookmaker.get_league(Betid.BUNDESLIGA)
        data3 = bookmaker.get_league(Betid.LALIGA)
        assert isinstance(data1, list)
        assert isinstance(data2, list)
        assert isinstance(data3, list)
