import pytest
from NaijaBet_Api.id import Betid
from NaijaBet_Api.bookmakers.altenar_base import AltenarBaseClass
from NaijaBet_Api.bookmakers.nairabet_altenar import NairabetAltenar
from NaijaBet_Api.bookmakers.betking_altenar import BetkingAltenar


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


class TestAltenarBaseClass:
    def test_cannot_instantiate_without_integration(self):
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
                "marketIds": [1, 2, 3, 4],
            }],
            "markets": [
                {"id": 1, "name": "1x2", "oddIds": [10, 11, 12], "typeId": 1},
                {"id": 2, "name": "Double chance", "oddIds": [20, 21, 22], "typeId": 10},
                {"id": 3, "name": "Total", "oddIds": [30, 31], "typeId": 18, "sv": "2.5"},
                {"id": 4, "name": "Both Teams To Score", "oddIds": [40, 41], "typeId": 29},
            ],
            "odds": [
                {"id": 10, "typeId": 1, "price": 2.5, "name": "Team A"},
                {"id": 11, "typeId": 2, "price": 3.0, "name": "X"},
                {"id": 12, "typeId": 3, "price": 2.8, "name": "Team B"},
                {"id": 20, "typeId": 9, "price": 1.5, "name": "Team A or draw"},
                {"id": 21, "typeId": 10, "price": 1.3, "name": "Team A or Team B"},
                {"id": 22, "typeId": 11, "price": 1.4, "name": "Draw or Team B"},
                {"id": 30, "typeId": 12, "price": 1.72, "name": "Over 2.5"},
                {"id": 31, "typeId": 13, "price": 2.13, "name": "Under 2.5"},
                {"id": 40, "typeId": 74, "price": 1.65, "name": "GG"},
                {"id": 41, "typeId": 76, "price": 2.20, "name": "NG"},
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
        assert match["over_2_5"] == 1.72
        assert match["under_2_5"] == 2.13
        assert match["btts_yes"] == 1.65
        assert match["btts_no"] == 2.20
        assert isinstance(match["time"], int)


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
            assert "over_2_5" in match
            assert "under_2_5" in match
            assert "btts_yes" in match
            assert "btts_no" in match
            assert isinstance(match["home"], float)
            assert isinstance(match["over_2_5"], float)
            assert isinstance(match["btts_yes"], float)
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
            assert "over_2_5" in match
            assert "under_2_5" in match
            assert "btts_yes" in match
            assert "btts_no" in match
            assert isinstance(match["home"], float)
            assert isinstance(match["over_2_5"], float)
            assert isinstance(match["btts_yes"], float)

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
