import time
import requests
from NaijaBet_Api.id import Betid
from typing import List, Dict, Any, Optional


# 1xBet LineFeed format odds mapping
# E array entries: G=market group, T=type, C=coefficient, P=parameter
ODDS_MAP = {
    # 1X2 (G=1)
    (1, 1): "home",
    (1, 2): "draw",
    (1, 3): "away",
    # Double Chance (G=8)
    (8, 4): "home_or_draw",
    (8, 5): "home_or_away",
    (8, 6): "draw_or_away",
    # BTTS (G=19)
    (19, 180): "btts_yes",
    (19, 181): "btts_no",
}


class OneXBetBase:
    """
    Shared base class for bookmakers using the 1xBet LineFeed API format.

    Subclasses must set:
        _site (str): Site identifier (e.g. 'twentytwobet', 'onexbet')
        _domain (str): Base domain (e.g. 'https://22bet.ng', 'https://1xbet.ng')
        _country (int): Country param for API calls
        _partner (int or None): Partner param for API calls (None to omit)
        _referer_path (str): Referer path suffix (e.g. '/line/Football/')
    """

    _site: str
    _domain: str
    _country: int
    _partner: Optional[int] = None
    _referer_path: str = "/line/Football/"
    _max_retries: int = 3
    _retry_delay: float = 2.0

    _headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self, proxies: Optional[Dict[str, str]] = None):
        """
        Args:
            proxies: Optional dict for requests, e.g. {"https": "http://user:pass@host:port"}
        """
        self.site = self._site
        self.session = requests.Session()
        self.session.headers.update(self._headers)
        self.session.headers["Referer"] = self._domain + self._referer_path
        if proxies:
            self.session.proxies = proxies

    def _build_league_url(self, league: Betid) -> str:
        league_id = league.twentytwobet_id
        params = (
            f"sports=1&champs={league_id}&count=50"
            f"&lng=en&tf=3000000&tz=1&mode=4&country={self._country}"
        )
        if self._partner is not None:
            params += f"&partner={self._partner}"
        return f"{self._domain}/service-api/LineFeed/Get1x2_VZip?{params}"

    def _build_event_url(self, event_id: int) -> str:
        params = f"id={event_id}&lng=en&cfview=0&is498=true&country={self._country}"
        if self._partner is not None:
            params += f"&partner={self._partner}"
        return f"{self._domain}/service-api/LineFeed/GetGameZip?{params}"

    def _request_with_retry(self, url: str) -> Optional[requests.Response]:
        for attempt in range(self._max_retries):
            try:
                res = self.session.get(url, timeout=15)
                if res.status_code == 200:
                    return res
                if res.status_code == 406 and attempt < self._max_retries - 1:
                    time.sleep(self._retry_delay * (attempt + 1))
                    continue
                return res
            except Exception:
                if attempt < self._max_retries - 1:
                    time.sleep(self._retry_delay * (attempt + 1))
                    continue
                return None
        return None

    def _fetch_event_odds(self, event_id: int) -> Dict[str, Any]:
        """Fetch all odds for a single event from GetGameZip."""
        url = self._build_event_url(event_id)
        res = self._request_with_retry(url)
        if res is None or res.status_code != 200:
            return {}
        try:
            data = res.json()
        except Exception:
            return {}

        val = data.get("Value", {})
        if not isinstance(val, dict):
            return {}

        odds_dict = {}
        for e in val.get("E", []):
            g = e.get("G")
            t = e.get("T")
            c = e.get("C")
            p = e.get("P")
            if c is None:
                continue

            field = ODDS_MAP.get((g, t))
            if field:
                odds_dict[field] = float(c)
                continue

            # Over/Under lines (G=17, T=9 over, T=10 under)
            if g == 17:
                if p is None:
                    continue
                line_key = str(p).replace(".", "_")
                if t == 9:
                    odds_dict[f"over_{line_key}"] = float(c)
                elif t == 10:
                    odds_dict[f"under_{line_key}"] = float(c)

        return odds_dict

    def normalizer(self, data: Any) -> List[Dict[str, Any]]:
        """Transform LineFeed API response into standardized match dicts."""
        if not data or not isinstance(data, dict):
            return []

        events = data.get("Value", [])
        if not events:
            return []

        results = []
        for event in events:
            o1 = event.get("O1", "")
            o2 = event.get("O2", "")
            if not o1 or not o2:
                continue

            match_odds = {}
            for e in event.get("E", []):
                g = e.get("G")
                t = e.get("T")
                c = e.get("C")
                p = e.get("P")

                field = ODDS_MAP.get((g, t))
                if field:
                    match_odds[field] = float(c) if c is not None else None
                    continue

                if g == 17 and p == 2.5:
                    if t == 9:
                        match_odds["over_2_5"] = float(c) if c is not None else None
                    elif t == 10:
                        match_odds["under_2_5"] = float(c) if c is not None else None

            match_dict = {
                "match": f"{o1} - {o2}",
                "league": event.get("L", ""),
                "time": event.get("S", 0),
                "league_id": event.get("LI", 0),
                "match_id": event.get("I", 0),
            }
            match_dict.update(match_odds)
            results.append(match_dict)

        return results

    def get_league(self, league: Betid = Betid.PREMIERLEAGUE) -> List[Dict[str, Any]]:
        """Fetch odds for a league. Fetches event details for full O/U lines."""
        url = self._build_league_url(league)
        res = self._request_with_retry(url)
        if res is None or res.status_code != 200:
            print(f"Warning: could not fetch league for {self.site}")
            return []
        try:
            data = res.json()
            if data is None:
                return []
        except Exception as e:
            print(f"Error parsing league response for {self.site}: {e}")
            return []

        events = data.get("Value", [])
        if not events:
            return []

        results = []
        for event in events:
            o1 = event.get("O1", "")
            o2 = event.get("O2", "")
            if not o1 or not o2:
                continue

            match_dict = {
                "match": f"{o1} - {o2}",
                "league": event.get("L", ""),
                "time": event.get("S", 0),
                "league_id": event.get("LI", 0),
                "match_id": event.get("I", 0),
            }

            event_odds = self._fetch_event_odds(event.get("I", 0))
            match_dict.update(event_odds)
            results.append(match_dict)

        return results

    def get_all(self) -> List[Dict[str, Any]]:
        """Fetch odds for all leagues with a valid twentytwobet_id."""
        self.data = []
        for league in Betid:
            if league.twentytwobet_id == 0:
                continue
            self.data += self.get_league(league)
        return self.data

    def get_team(self, team: str) -> List[Dict[str, Any]]:
        """Fetch odds for matches involving a specific team."""
        self.get_all()

        def filter_func(data):
            match: str = data["match"]
            return match.lower().find(team.lower()) != -1

        return list(filter(filter_func, self.data))
