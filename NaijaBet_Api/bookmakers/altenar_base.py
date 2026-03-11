import requests
import arrow
from NaijaBet_Api.bookmakers.BaseClass import BookmakerBaseClass
from NaijaBet_Api.id import Betid
from typing import List, Dict, Any, Optional


# Altenar odds typeId -> standardized field name
ODDS_TYPE_MAP = {
    1: "home",
    2: "draw",
    3: "away",
    9: "home_or_draw",
    10: "home_or_away",
    11: "draw_or_away",
    74: "btts_yes",
    76: "btts_no",
}

# Over/Under odds typeId -> field name (needs market context to filter by line)
OVER_UNDER_TYPE_MAP = {
    12: "over_{line}",
    13: "under_{line}",
}

_EVENT_DETAILS_URL = (
    "https://sb2frontend-altenar2.biahosted.com/api/widget/GetEventDetails"
    "?culture=en-GB&timezoneOffset=-60&integration={integration}"
    "&deviceType=1&numFormat=en-GB&countryCode=NG&eventId={event_id}"
)


class AltenarBaseClass(BookmakerBaseClass):
    """
    Base class for bookmakers powered by the Altenar sportsbook platform.

    Subclasses must set:
        _integration: str -- Altenar integration name (e.g. "nairabet", "betking")
        _site: str -- site identifier
        _url: str -- base site URL
    """

    _site = 'altenar'
    _url = 'https://sb2frontend-altenar2.biahosted.com'

    _headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, '_integration'):
            raise NotImplementedError("Altenar subclasses must define _integration")

    def __init__(self, proxies: Optional[Dict[str, str]] = None):
        """
        Args:
            proxies: Optional dict for requests, e.g. {"https": "http://user:pass@host:port"}
        """
        self.site = 'altenar'
        self.session = requests.Session()
        self.session.headers.update(self._headers)
        if proxies:
            self.session.proxies = proxies

    def _build_url(self, league: Betid) -> str:
        """Build the Altenar API URL for a league."""
        return league.to_endpoint('altenar').format(integration=self._integration)

    def _fetch_event_odds(self, event_id: int) -> Dict[str, float]:
        """
        Fetch all odds for a single event from GetEventDetails.

        Returns a dict of all available odds including all over/under lines.
        """
        url = _EVENT_DETAILS_URL.format(
            integration=self._integration, event_id=event_id
        )
        try:
            res = self.session.get(url)
            if res.status_code != 200:
                return {}
            data = res.json()
        except Exception:
            return {}

        markets = data.get("markets", [])
        odds_list = data.get("odds", [])
        odds_by_id = {o["id"]: o for o in odds_list}

        # Collect oddIds from Total markets (typeId=18) for over/under extraction
        total_odd_ids = set()
        for m in markets:
            if m.get("typeId") == 18:
                for row in m.get("desktopOddIds", []):
                    if isinstance(row, list):
                        total_odd_ids.update(row)

        odds_dict = {}

        # Extract standard odds from all odds in the response
        for odd in odds_list:
            type_id = odd.get("typeId")
            price = odd.get("price")
            if price is None:
                continue

            # Standard markets (1x2, double chance, BTTS)
            field = ODDS_TYPE_MAP.get(type_id)
            if field and field not in odds_dict:
                odds_dict[field] = price
                continue

            # Over/Under from the Total market only
            if odd["id"] in total_odd_ids:
                sv = odd.get("sv", "")
                if not sv:
                    continue
                line_key = sv.replace(".", "_")
                if type_id == 12:
                    odds_dict[f"over_{line_key}"] = price
                elif type_id == 13:
                    odds_dict[f"under_{line_key}"] = price

        return odds_dict

    def normalizer(self, data: Any) -> List[Dict[str, Any]]:
        """
        Join the relational Altenar response into standardized match dicts.
        Used for basic league-level data (without event details enrichment).
        """
        if not data or not isinstance(data, dict):
            return []

        events = data.get("events", [])
        if not events:
            return []

        odds_list = data.get("odds", [])
        markets_list = data.get("markets", [])
        champs_list = data.get("champs", [])

        odds_by_id = {o["id"]: o for o in odds_list}
        markets_by_id = {m["id"]: m for m in markets_list}
        champs_by_id = {c["id"]: c for c in champs_list}

        results = []
        for event in events:
            champ = champs_by_id.get(event.get("champId"), {})

            # Collect odds from all supported markets
            match_odds = {}
            for mid in event.get("marketIds", []):
                market = markets_by_id.get(mid, {})
                market_type = market.get("typeId")

                for oid in market.get("oddIds", []):
                    odd = odds_by_id.get(oid, {})
                    type_id = odd.get("typeId")

                    # Standard markets (1x2, double chance, BTTS)
                    field = ODDS_TYPE_MAP.get(type_id)
                    if field:
                        match_odds[field] = odd.get("price")
                        continue

                    # Over/Under from Total markets
                    if market_type == 18:
                        ou_field = OVER_UNDER_TYPE_MAP.get(type_id)
                        if ou_field:
                            line = market.get("sv", "").replace(".", "_")
                            match_odds[ou_field.format(line=line)] = odd.get("price")

            # Convert "Team A vs. Team B" to "Team A - Team B"
            name = event.get("name", "")
            match_name = name.replace(" vs. ", " - ")

            # Convert ISO timestamp to unix int
            start_date = event.get("startDate", "")
            try:
                time_val = arrow.get(start_date).int_timestamp
            except Exception:
                time_val = 0

            match_dict = {
                "match": match_name,
                "league": champ.get("name", ""),
                "time": time_val,
                "league_id": event.get("champId", 0),
                "match_id": event.get("id", 0),
            }
            match_dict.update(match_odds)
            results.append(match_dict)

        return results

    def get_league(self, league: Betid = Betid.PREMIERLEAGUE) -> List[Dict[str, Any]]:
        """
        Fetch odds for a league via the Altenar API.

        First fetches the league event list, then for each event
        fetches detailed odds (including all over/under lines).
        """
        try:
            url = self._build_url(league)
            res = self.session.get(url)
            if res.status_code != 200:
                print(f"Warning: HTTP {res.status_code} for {self._integration}")
                return []
            league_data = res.json()
            if league_data is None:
                return []
        except Exception as e:
            print(f"Error fetching league for {self._integration}: {e}")
            return []

        events = league_data.get("events", [])
        if not events:
            return []

        champs_list = league_data.get("champs", [])
        champs_by_id = {c["id"]: c for c in champs_list}

        results = []
        for event in events:
            champ = champs_by_id.get(event.get("champId"), {})

            name = event.get("name", "")
            match_name = name.replace(" vs. ", " - ")

            start_date = event.get("startDate", "")
            try:
                time_val = arrow.get(start_date).int_timestamp
            except Exception:
                time_val = 0

            match_dict = {
                "match": match_name,
                "league": champ.get("name", ""),
                "time": time_val,
                "league_id": event.get("champId", 0),
                "match_id": event.get("id", 0),
            }

            # Fetch full odds from event details
            event_odds = self._fetch_event_odds(event.get("id", 0))
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
