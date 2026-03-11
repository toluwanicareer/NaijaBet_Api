"""
E2E test for legacy Nairabet — API domain is dead.
For working Nairabet odds, use NairabetAltenar (see test_altenar_e2e.py).
"""
import pytest
from NaijaBet_Api.bookmakers.nairabet import Nairabet
from NaijaBet_Api.id import Betid

pytestmark = pytest.mark.xfail(
    reason="Legacy Nairabet API (sports-api.nairabet.com) no longer resolves — use NairabetAltenar instead",
    strict=False,
)


class TestNairabetE2E:

    @pytest.fixture(scope="class")
    def league_data(self):
        bookmaker = Nairabet()
        return bookmaker.get_league(Betid.PREMIERLEAGUE)

    def test_returns_list(self, league_data):
        assert isinstance(league_data, list)

    def test_has_matches(self, league_data):
        assert len(league_data) > 0, "Expected at least one match"

    def test_1x2_odds(self, league_data):
        match = league_data[0]
        for field in ['home', 'draw', 'away']:
            assert field in match
            assert isinstance(match[field], (int, float))
            assert match[field] > 1.0
