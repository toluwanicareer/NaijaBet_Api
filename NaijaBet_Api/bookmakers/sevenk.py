"""
SevenKBet (7k.bet) bookmaker — 442hattrick/Cactus Sportsbook REST API.

No browser automation needed. Uses simple HTTP requests:
1. Load /en/spbk?operatorToken=logout to get session cookies
2. GET /api/eventlist/eu/events/v2/league-events for event list
3. GET /api/eventpage/events/{id} for full market data per event
"""
import requests
from NaijaBet_Api.bookmakers.BaseClass import BookmakerBaseClass
from NaijaBet_Api.id import Betid
from typing import List, Dict, Any, Optional


_BASE = "https://prod20379-179369742.442hattrick.com"

# Betid → 7k.bet MasterLeagueId (used in league-events endpoint)
LEAGUE_MAP = {
    # England
    Betid.PREMIERLEAGUE: '24',
    Betid.CHAMPIONSHIP: '43',
    Betid.LEAGUE_ONE: '52',
    Betid.LEAGUE_TWO: '53',
    Betid.ENGLAND_FA_CUP: '89',
    Betid.ENGLAND_NATIONAL_LEAGUE: '54',
    # Germany
    Betid.BUNDESLIGA: '110',
    Betid.BUNDESLIGA_2: '113',
    Betid.GERMANY_3_LIGA: '2336',
    Betid.GERMANY_DFB_POKAL: '5768',
    # Spain
    Betid.LALIGA: '38',
    Betid.SPAIN_COPA_DEL_REY: '105',
    # France
    Betid.LIGUE_1: '25',
    Betid.LIGUE_2: '97',
    Betid.COUPE_DE_FRANCE: '35',
    # Italy
    Betid.SERIEA: '74',
    Betid.ITALY_SERIE_B: '80',
    # Netherlands
    Betid.NETHERLANDS_EREDIVISIE: '111',
    Betid.NETHERLANDS_EERSTE_DIVISIE: '120',
    # Portugal
    Betid.PORTUGAL_PRIMEIRA_LIGA: '32',
    Betid.PORTUGAL_SEGUNDA_LIGA: '122',
    # Scotland
    Betid.SCOTLAND_PREMIERSHIP: '47',
    Betid.SCOTLAND_CHAMPIONSHIP: '55',
    Betid.SCOTLAND_LEAGUE_ONE: '56',
    Betid.SCOTLAND_LEAGUE_TWO: '57',
    # UEFA
    Betid.UEFA_CHAMPIONS_LEAGUE: '125',
    Betid.UEFA_EUROPA_LEAGUE: '2719',
    # Turkey
    Betid.TURKEY_SUPER_LIG: '123',
    Betid.TURKEY_TFF_1_LIG: '267',
    # Belgium
    Betid.BELGIUM_PRO_LEAGUE: '26',
    Betid.BELGIUM_CHALLENGER_PRO_LEAGUE: '37',
    # Switzerland
    Betid.SWITZERLAND_SUPER_LEAGUE: '157',
    # Denmark
    Betid.DENMARK_SUPERLIGA: '203',
    # Norway
    Betid.NORWAY_ELITESERIEN: '235',
    # Sweden
    Betid.SWEDEN_ALLSVENSKAN: '237',
    # Greece
    Betid.GREECE_SUPER_LEAGUE: '27',
    # Poland
    Betid.POLAND_EKSTRAKLASA: '202',
    # Romania
    Betid.ROMANIA_LIGA_1: '191',
    # Serbia
    Betid.SERBIA_SUPER_LIGA: '185',
    # Hungary
    Betid.HUNGARY_NB_I: '204',
    # Austria
    Betid.AUSTRIA_BUNDESLIGA: '156',
    # Croatia
    Betid.CROATIA_HNL: '179',
    # Ukraine
    Betid.UKRAINE_PREMIER_LEAGUE: '187',
    # Cyprus
    Betid.CYPRUS_FIRST_DIVISION: '414',
    # South America
    Betid.ARGENTINA_PRIMERA_DIVISION: '150',
    Betid.BRAZIL_SERIE_A: '530',
    Betid.BRAZIL_SERIE_B: '1439',
    Betid.CHILE_PRIMERA_DIVISION: '115',
    Betid.COLOMBIA_PRIMERA_A: '1070',
    # North America
    Betid.USA_MLS: '224',
    Betid.MEXICO_LIGA_MX: '632',
    # Middle East
    Betid.SAUDI_PRO_LEAGUE: '492',
    # Africa
    Betid.NIGERIA_PREMIER_LEAGUE: '2906',
    Betid.SOUTH_AFRICA_PREMIERSHIP: '1062',
    # Asia
    Betid.JAPAN_J_LEAGUE: '193',
    Betid.SOUTH_KOREA_K_LEAGUE_1: '329',
    Betid.CHINA_SUPER_LEAGUE: '276',
    Betid.INDIA_SUPER_LEAGUE: '6884',
    # Australia
    Betid.AUSTRALIA_A_LEAGUE: '452',
}

# Target market type codes → market names in the event page response
_TARGET_MARKETS = {
    "FT 1X2", "Double Chance", "Total Goals O/U", "Both Teams To Score",
    "Corners FT O/U", "Corners FT Asian Handicap", "FT Asian Handicap",
}


def _extract_odds(markets: list) -> Dict[str, Any]:
    """Extract standardized odds from an event page market array."""
    odds = {}
    # Collect Asian handicap candidates to pick the main line afterwards.
    # Each entry: (abs_line, line_value, home_odds, away_odds)
    ah_candidates: list = []
    corners_ah_candidates: list = []

    for m in markets:
        mname = m[1]
        if mname not in _TARGET_MARKETS:
            continue
        selections = m[13]

        # --- Asian handicap markets need pair collection first ---
        if mname in ("FT Asian Handicap", "Corners FT Asian Handicap"):
            # Group selections into (home, away) pairs by absolute line value.
            # sel[9]==1 → home, sel[9]==3 → away; sel[16] → line
            pairs: Dict[float, Dict[str, float]] = {}
            for sel in selections:
                dec_odds = sel[6]
                suspended = sel[5]
                if suspended or not isinstance(dec_odds, (int, float)) or dec_odds <= 0:
                    continue
                line = sel[16]
                pos = sel[9]
                if line is None:
                    continue
                abs_line = abs(line)
                if abs_line not in pairs:
                    pairs[abs_line] = {}
                if pos == 1:
                    pairs[abs_line]["home"] = dec_odds
                    pairs[abs_line]["home_line"] = line
                elif pos == 3:
                    pairs[abs_line]["away"] = dec_odds
                    pairs[abs_line]["away_line"] = line
            # Keep only complete pairs (both home and away present)
            target = corners_ah_candidates if mname == "Corners FT Asian Handicap" else ah_candidates
            for abs_line, pair in pairs.items():
                if "home" in pair and "away" in pair:
                    target.append((abs_line, pair["home_line"], pair["home"], pair["away"]))
            continue

        for sel in selections:
            dec_odds = sel[6]
            suspended = sel[5]
            if suspended or not isinstance(dec_odds, (int, float)) or dec_odds <= 0:
                continue

            if mname == "FT 1X2":
                pos = sel[9]
                if pos == 1:
                    odds["home"] = dec_odds
                elif pos == 2:
                    odds["draw"] = dec_odds
                elif pos == 3:
                    odds["away"] = dec_odds

            elif mname == "Double Chance":
                pos = sel[9]
                if pos == 1:
                    odds["home_or_draw"] = dec_odds
                elif pos == 3:
                    odds["draw_or_away"] = dec_odds
                elif pos == 2:
                    odds["home_or_away"] = dec_odds

            elif mname == "Both Teams To Score":
                name = sel[1]
                if isinstance(name, dict):
                    name = name.get("EN", "")
                if name == "Yes":
                    odds["btts_yes"] = dec_odds
                elif name == "No":
                    odds["btts_no"] = dec_odds

            elif mname == "Total Goals O/U":
                line = sel[16]
                direction = sel[2]
                if isinstance(direction, dict):
                    direction = direction.get("EN", "")
                if line is None:
                    continue
                line_key = str(line).replace(".", "_")
                if "Over" in str(direction):
                    odds[f"over_{line_key}"] = dec_odds
                elif "Under" in str(direction):
                    odds[f"under_{line_key}"] = dec_odds

            elif mname == "Corners FT O/U":
                line = sel[16]
                direction = sel[2]
                if isinstance(direction, dict):
                    direction = direction.get("EN", "")
                if line is None:
                    continue
                line_key = str(line).replace(".", "_")
                if "Over" in str(direction):
                    odds[f"corners_over_{line_key}"] = dec_odds
                elif "Under" in str(direction):
                    odds[f"corners_under_{line_key}"] = dec_odds

    # Pick main Asian handicap line (smallest absolute line with active odds)
    if ah_candidates:
        ah_candidates.sort(key=lambda x: x[0])
        _, home_line, home_odds, away_odds = ah_candidates[0]
        odds["asian_handicap_1"] = home_odds
        odds["asian_handicap_2"] = away_odds
        odds["asian_handicap_line"] = home_line

    if corners_ah_candidates:
        corners_ah_candidates.sort(key=lambda x: x[0])
        _, home_line, home_odds, away_odds = corners_ah_candidates[0]
        odds["corners_asian_handicap_1"] = home_odds
        odds["corners_asian_handicap_2"] = away_odds
        odds["corners_asian_handicap_line"] = home_line

    return odds


class SevenKBet(BookmakerBaseClass):
    """
    Bookmaker class for 7k.bet (442hattrick/Cactus Sportsbook).

    Uses REST API at prod20379-179369742.442hattrick.com.
    Auth: load sportsbook HTML page to get session cookies.
    """

    _site = 'sevenk'
    _url = 'https://ng.7k.bet'

    def __init__(self, proxies: Optional[Dict[str, str]] = None):
        self.site = self._site
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
        })
        if proxies:
            self.session.proxies = proxies
        self._init_session()

    def _init_session(self):
        """Load the sportsbook page to get authorization and session cookies."""
        self.session.get(f"{_BASE}/en/spbk?operatorToken=logout", timeout=20)
        for c in self.session.cookies:
            if c.name in ("authorization", "session"):
                self.session.headers[c.name] = c.value

    def _fetch_league_events(self, master_league_id: str) -> list:
        """Fetch the event list for a league (no odds, just event IDs/metadata)."""
        try:
            r = self.session.get(
                f"{_BASE}/api/eventlist/eu/events/v2/league-events",
                params={"leagueId": master_league_id},
                timeout=15,
            )
            if r.status_code != 200:
                return []
            return r.json().get("data", [])
        except Exception:
            return []

    def _fetch_event_odds(self, event_id: str) -> Dict[str, Any]:
        """Fetch full odds for a single event from the event page."""
        try:
            r = self.session.get(
                f"{_BASE}/api/eventpage/events/{event_id}",
                params={"hideX25X75Selections": "false"},
                timeout=30,
            )
            if r.status_code != 200:
                return {}
            data = r.json()
            ev = data.get("data", [])
            if not ev:
                return {}
            markets = ev[0][20]
            return _extract_odds(markets)
        except Exception:
            return {}

    def normalizer(self, data=None):
        return []

    def get_league_fast(self, league: Betid = Betid.PREMIERLEAGUE) -> List[Dict[str, Any]]:
        """
        Fetch match list for a league without detailed odds.

        Returns matches with basic info (teams, date, IDs) but no odds.
        Use get_league() for full odds.
        """
        master_id = LEAGUE_MAP.get(league)
        if not master_id:
            return []

        events = self._fetch_league_events(master_id)
        results = []
        for ev in events:
            # ev[26] == "Fixture" for prematch, skip outrights etc.
            if ev[26] != "Fixture":
                continue
            teams = ev[8]
            if len(teams) < 2:
                continue
            home = teams[0][1]
            away = teams[1][1]
            if isinstance(home, dict):
                home = home.get("EN", "")
            if isinstance(away, dict):
                away = away.get("EN", "")
            results.append({
                "match": f"{home} - {away}",
                "league": ev[2],
                "match_id": ev[0],
                "time": ev[11],
            })
        return results

    def get_league(self, league: Betid = Betid.PREMIERLEAGUE) -> List[Dict[str, Any]]:
        """
        Fetch odds for a league.

        Fetches the event list, then for each event fetches full market
        data (1X2, Double Chance, Over/Under lines, BTTS).
        """
        master_id = LEAGUE_MAP.get(league)
        if not master_id:
            return []

        events = self._fetch_league_events(master_id)
        results = []
        for ev in events:
            if ev[26] != "Fixture":
                continue
            teams = ev[8]
            if len(teams) < 2:
                continue
            home = teams[0][1]
            away = teams[1][1]
            if isinstance(home, dict):
                home = home.get("EN", "")
            if isinstance(away, dict):
                away = away.get("EN", "")

            match_dict = {
                "match": f"{home} - {away}",
                "league": ev[2],
                "match_id": ev[0],
                "time": ev[11],
            }

            event_odds = self._fetch_event_odds(ev[0])
            match_dict.update(event_odds)
            results.append(match_dict)

        return results

    def get_all(self) -> List[Dict[str, Any]]:
        """Fetch odds for all mapped leagues."""
        self.data = []
        for league in Betid:
            if league not in LEAGUE_MAP:
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
