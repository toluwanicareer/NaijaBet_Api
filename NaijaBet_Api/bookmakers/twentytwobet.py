import requests
from NaijaBet_Api.bookmakers.BaseClass import BookmakerBaseClass
from NaijaBet_Api.id import Betid
from typing import List, Dict, Any, Optional


# 22bet odds mapping (1xBet white-label format)
# E array entries: G=market group, T=type, C=coefficient, P=parameter
ODDS_MAP = {
    # 1X2 (G=1)
    (1, 1): "home",
    (1, 2): "draw",
    (1, 3): "away",
    # Double Chance (G=8)
    (8, 4): "home_or_draw",
    (8, 5): "draw_or_away",
    (8, 6): "home_or_away",
    # BTTS (G=19)
    (19, 180): "btts_yes",
    (19, 181): "btts_no",
}

_EVENT_DETAILS_URL = (
    "https://22bet.ng/service-api/LineFeed/GetGameZip"
    "?id={event_id}&lng=en&cfview=0&is498=true&country=159"
)


class TwentyTwoBet(BookmakerBaseClass):
    """
    Bookmaker class for 22bet.ng (1xBet white-label).

    Uses the /service-api/LineFeed/ API endpoints.
    Fetches event details for full over/under lines.
    Supports proxy configuration for requests.
    """

    _site = 'twentytwobet'
    _url = 'https://22bet.ng'

    _headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://22bet.ng/line/Football/",
    }

    def __init__(self, proxies: Optional[Dict[str, str]] = None):
        """
        Args:
            proxies: Optional dict for requests, e.g. {"https": "http://user:pass@host:port"}
        """
        self.site = self._site
        self.session = requests.Session()
        self.session.headers.update(self._headers)
        if proxies:
            self.session.proxies = proxies

    def _build_url(self, league: Betid) -> str:
        return league.to_endpoint('twentytwobet')

    def _fetch_event_odds(self, event_id: int) -> Dict[str, Any]:
        """
        Fetch all odds for a single event from GetGameZip.

        Returns a dict with all standard odds + all over/under lines.
        """
        url = _EVENT_DETAILS_URL.format(event_id=event_id)
        try:
            res = self.session.get(url)
            if res.status_code != 200:
                return {}
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

            # Standard markets (1x2, double chance, BTTS)
            field = ODDS_MAP.get((g, t))
            if field:
                odds_dict[field] = float(c)
                continue

            # All Over/Under lines (G=17, T=9 over, T=10 under)
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
        """
        Transform 22bet API response into standardized match dicts.
        Used for basic parsing without event detail enrichment.
        """
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
        """
        Fetch odds for a league via the 22bet API.

        First fetches league event list, then for each event
        fetches detailed odds (including all over/under lines).
        """
        try:
            url = self._build_url(league)
            res = self.session.get(url)
            if res.status_code != 200:
                print(f"Warning: HTTP {res.status_code} for {self.site}")
                return []
            data = res.json()
            if data is None:
                return []
        except Exception as e:
            print(f"Error fetching league for {self.site}: {e}")
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

            # Fetch full odds from event details
            event_odds = self._fetch_event_odds(event.get("I", 0))
            match_dict.update(event_odds)

            results.append(match_dict)

        return results

    def get_all(self) -> List[Dict[str, Any]]:
        """Fetch odds for all implemented leagues."""
        self.data = []
        for league in Betid:
            self.data += self.get_league(league)
        return self.data

    def get_team(self, team: str) -> List[Dict[str, Any]]:
        """Fetch odds for matches involving a specific team."""
        self.get_all()

        def filter_func(data):
            match: str = data["match"]
            return match.lower().find(team.lower()) != -1

        return list(filter(filter_func, self.data))
