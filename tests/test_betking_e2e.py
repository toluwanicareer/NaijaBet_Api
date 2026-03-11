"""
E2E test for legacy Betking — Cloudflare-blocked, all tests xfail.
For working Betking odds, use BetkingAltenar (see test_altenar_e2e.py).
"""
import pytest
from NaijaBet_Api.bookmakers.betking import Betking
from NaijaBet_Api.id import Betid

pytestmark = pytest.mark.xfail(
    reason="Betking API blocked by Cloudflare — use BetkingAltenar instead",
    strict=False,
)


class TestBetkingE2E:

    @pytest.fixture(scope="class")
    def league_data(self):
        bookmaker = Betking()
        return bookmaker.get_league(Betid.PREMIERLEAGUE)

    def test_returns_list(self, league_data):
        assert isinstance(league_data, list)

    def test_has_matches(self, league_data):
        assert len(league_data) > 0, "Cloudflare blocks this"

    def test_1x2_odds(self, league_data):
        match = league_data[0]
        for field in ['home', 'draw', 'away']:
            assert field in match
            assert isinstance(match[field], (int, float))
            assert match[field] > 1.0
