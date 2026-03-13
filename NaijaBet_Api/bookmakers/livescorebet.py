"""
LivescoreBet Nigeria odds extraction via Kambi REST API.

Usage:
    from NaijaBet_Api.bookmakers.livescorebet import LivescoreBet
    from NaijaBet_Api.id import Betid

    lsb = LivescoreBet()
    data = lsb.get_league(Betid.PREMIERLEAGUE)
"""

import re
import uuid
import requests
import arrow
from NaijaBet_Api.id import Betid
from typing import List, Dict, Any, Optional


_BASE = "https://gateway-ng.livescorebet.com/sportsbook/gateway"
_EVENTS_URL = _BASE + "/v3/view/events/matches"

# Kambi CDN betoffer endpoint — returns ALL markets for a single event.
# The gateway-ng matches endpoint only serves core markets (1X2, DC, BTTS, O/U).
# Extended markets (corners, Asian handicap) require the CDN betoffer endpoint.
_KAMBI_CDN = "https://eu-offering-api.kambicdn.com/offering/v2018"
_BETOFFER_URL = _KAMBI_CDN + "/livescorebet/betoffer/event/{event_id}.json"

# Betid -> SBTC3 category ID
COMPETITION_MAP = {
    # === England ===
    Betid.PREMIERLEAGUE: "SBTC3_40253",
    Betid.CHAMPIONSHIP: "SBTC3_40817",
    Betid.LEAGUE_ONE: "SBTC3_40822",
    Betid.LEAGUE_TWO: "SBTC3_40823",
    Betid.ENGLAND_FA_CUP: "SBTC3_56687",
    Betid.ENGLAND_EFL_CUP: "SBTC3_36690",
    Betid.ENGLAND_NATIONAL_LEAGUE: "SBTC3_42666",
    Betid.ENGLAND_WSL: "SBTC3_42896",
    # === Germany ===
    Betid.BUNDESLIGA: "SBTC3_40481",
    Betid.BUNDESLIGA_2: "SBTC3_40820",
    Betid.GERMANY_3_LIGA: "SBTC3_52969",
    # === Spain ===
    Betid.LALIGA: "SBTC3_40031",
    Betid.SPAIN_SEGUNDA_DIVISION: "SBTC3_44411",
    Betid.SPAIN_COPA_DEL_REY: "SBTC3_41374",
    # === France ===
    Betid.LIGUE_1: "SBTC3_40032",
    Betid.LIGUE_2: "SBTC3_52971",
    Betid.FRANCE_NATIONAL: "SBTC3_41041",
    Betid.FRANCE_NATIONAL_2: "SBTC3_59181",
    Betid.COUPE_DE_FRANCE: "SBTC3_212383",
    # === Italy ===
    Betid.SERIEA: "SBTC3_40030",
    Betid.ITALY_SERIE_B: "SBTC3_42884",
    # === Netherlands ===
    Betid.NETHERLANDS_EREDIVISIE: "SBTC3_41372",
    Betid.NETHERLANDS_EERSTE_DIVISIE: "SBTC3_41371",
    # === Portugal ===
    Betid.PORTUGAL_PRIMEIRA_LIGA: "SBTC3_44069",
    Betid.PORTUGAL_SEGUNDA_LIGA: "SBTC3_55903",
    # === Scotland ===
    Betid.SCOTLAND_PREMIERSHIP: "SBTC3_40818",
    Betid.SCOTLAND_CHAMPIONSHIP: "SBTC3_42885",
    Betid.SCOTLAND_LEAGUE_ONE: "SBTC3_43314",
    # === UEFA / International ===
    Betid.UEFA_CHAMPIONS_LEAGUE: "SBTC3_40685",
    Betid.WORLD_CUP_2026: "SBTC3_209533",
    Betid.COPA_LIBERTADORES: "SBTC3_87864",
    Betid.CONCACAF_CHAMPIONS_CUP: "SBTC3_212345",
    Betid.CAF_CHAMPIONS_LEAGUE: "SBTC3_94795",
    # === Belgium ===
    Betid.BELGIUM_PRO_LEAGUE: "SBTC3_40815",
    Betid.BELGIUM_CHALLENGER_PRO_LEAGUE: "SBTC3_41092",
    # === Turkey ===
    Betid.TURKEY_SUPER_LIG: "SBTC3_41090",
    Betid.TURKEY_TFF_1_LIG: "SBTC3_59028",
    Betid.TURKEY_TFF_2_LIG: "SBTC3_68780",
    # === Austria ===
    Betid.AUSTRIA_BUNDESLIGA: "SBTC3_42282",
    Betid.AUSTRIA_2_LIGA: "SBTC3_44056",
    # === Switzerland ===
    Betid.SWITZERLAND_SUPER_LEAGUE: "SBTC3_41373",
    Betid.SWITZERLAND_CHALLENGE_LEAGUE: "SBTC3_44904",
    # === Denmark ===
    Betid.DENMARK_SUPERLIGA: "SBTC3_40816",
    Betid.DENMARK_1ST_DIVISION: "SBTC3_44174",
    Betid.DENMARK_2ND_DIVISION: "SBTC3_24756",
    # === Scandinavia ===
    Betid.NORWAY_ELITESERIEN: "SBTC3_84553",
    Betid.SWEDEN_ALLSVENSKAN: "SBTC3_84731",
    Betid.SWEDEN_SVENSKA_CUP: "SBTC3_39853",
    # === Eastern Europe ===
    Betid.GREECE_SUPER_LEAGUE: "SBTC3_52938",
    Betid.GREECE_SUPER_LEAGUE_2: "SBTC3_198222",
    Betid.CZECH_REPUBLIC_LIGA: "SBTC3_45024",
    Betid.POLAND_EKSTRAKLASA: "SBTC3_40145",
    Betid.POLAND_I_LIGA: "SBTC3_53413",
    Betid.POLAND_II_LIGA: "SBTC3_41141",
    Betid.ROMANIA_LIGA_1: "SBTC3_43764",
    Betid.ROMANIA_LIGA_2: "SBTC3_56515",
    Betid.CROATIA_HNL: "SBTC3_44419",
    Betid.SERBIA_SUPER_LIGA: "SBTC3_45092",
    Betid.HUNGARY_NB_I: "SBTC3_44465",
    Betid.HUNGARY_NB_II: "SBTC3_41260",
    Betid.SLOVAKIA_SUPER_LIGA: "SBTC3_43965",
    Betid.SLOVENIA_PRVA_LIGA: "SBTC3_55864",
    Betid.BULGARIA_FIRST_LEAGUE: "SBTC3_41257",
    Betid.CYPRUS_FIRST_DIVISION: "SBTC3_59145",
    Betid.ESTONIA_PREMIUM_LIIGA: "SBTC3_90322",
    Betid.LATVIA_VIRSLIGA: "SBTC3_35349",
    Betid.LITHUANIA_A_LIGA: "SBTC3_90321",
    Betid.UKRAINE_PREMIER_LEAGUE: "SBTC3_212487",
    Betid.AZERBAIJAN_PREMIER_LEAGUE: "SBTC3_55862",
    Betid.BOSNIA_PREMIER_LEAGUE: "SBTC3_52892",
    # === British Isles ===
    Betid.NORTHERN_IRELAND_PREMIERSHIP: "SBTC3_59353",
    Betid.IRELAND_PREMIER_DIVISION: "SBTC3_34565",
    Betid.IRELAND_FIRST_DIVISION: "SBTC3_43867",
    Betid.WALES_PREMIER_LEAGUE: "SBTC3_52936",
    Betid.FAROE_ISLANDS_1ST_DEILD: "SBTC3_212649",
    # === South America ===
    Betid.ARGENTINA_PRIMERA_DIVISION: "SBTC3_59107",
    Betid.BRAZIL_SERIE_A: "SBTC3_38529",
    Betid.BRAZIL_SERIE_B: "SBTC3_39039",
    Betid.BRAZIL_COPA_DO_BRASIL: "SBTC3_56688",
    Betid.CHILE_PRIMERA_DIVISION: "SBTC3_53411",
    Betid.COLOMBIA_PRIMERA_A: "SBTC3_33073",
    Betid.COLOMBIA_PRIMERA_B: "SBTC3_23854",
    Betid.ECUADOR_LIGA_PRO: "SBTC3_215643",
    Betid.PARAGUAY_PRIMERA_DIVISION: "SBTC3_55791",
    Betid.PERU_LIGA_1: "SBTC3_215645",
    Betid.URUGUAY_PRIMERA_DIVISION: "SBTC3_33339",
    Betid.VENEZUELA_PRIMERA_DIVISION: "SBTC3_43552",
    # === North & Central America ===
    Betid.USA_MLS: "SBTC3_89345",
    Betid.MEXICO_LIGA_MX: "SBTC3_44525",
    Betid.MEXICO_LIGA_MX_WOMEN: "SBTC3_104685",
    Betid.MEXICO_LIGA_EXPANSION: "SBTC3_44647",
    Betid.COSTA_RICA_PRIMERA: "SBTC3_44659",
    Betid.HONDURAS_LIGA_NACIONAL: "SBTC3_94471",
    Betid.GUATEMALA_LIGA_NACIONAL: "SBTC3_44752",
    # === Africa ===
    Betid.NIGERIA_PREMIER_LEAGUE: "SBTC3_214914",
    Betid.SOUTH_AFRICA_PREMIERSHIP: "SBTC3_59257",
    Betid.EGYPT_SECOND_DIVISION: "SBTC3_19006",
    Betid.ALGERIA_LIGUE_1: "SBTC3_56854",
    Betid.ETHIOPIA_PREMIER_LEAGUE: "SBTC3_85573",
    Betid.UGANDA_PREMIER_LEAGUE: "SBTC3_59036",
    Betid.ZAMBIA_SUPER_LEAGUE: "SBTC3_42062",
    # === Asia ===
    Betid.SOUTH_KOREA_K_LEAGUE_1: "SBTC3_90093",
    Betid.CHINA_SUPER_LEAGUE: "SBTC3_3106",
    Betid.INDIA_SUPER_LEAGUE: "SBTC3_78859",
    Betid.THAILAND_LEAGUE_1: "SBTC3_43497",
    Betid.VIETNAM_V_LEAGUE: "SBTC3_34273",
    Betid.IRAQ_LEAGUE: "SBTC3_10512",
    # === Middle East ===
    Betid.SAUDI_PRO_LEAGUE: "SBTC3_72057",
    Betid.QATAR_STARS_LEAGUE: "SBTC3_25815",
    Betid.BAHRAIN_PREMIER_LEAGUE: "SBTC3_69267",
    Betid.JORDAN_LEAGUE: "SBTC3_83019",
    # === Australia ===
    Betid.AUSTRALIA_A_LEAGUE: "SBTC3_94677",
}


def _parse_betoffers(data):
    """Extract corners O/U and Asian handicap from Kambi CDN betoffer response.

    The CDN ``/betoffer/event/{id}.json`` endpoint returns *all* markets for an
    event.  Each betOffer has:
      - ``criterion.label`` — market name (e.g. "Total Corners", "Asian Handicap")
      - ``criterion.lifetime`` — period (e.g. "FULL_TIME")
      - ``betOfferType.name`` — type (e.g. "Over/Under", "Asian Handicap")
      - ``outcomes`` — list with ``label``, ``odds`` (int, millis), ``line``
        (int, millis), and optionally ``participant``.

    Returns a dict of extracted fields ready to merge into a match dict.
    """
    result = {}
    betoffers = data.get("betOffers", [])

    for bo in betoffers:
        criterion = bo.get("criterion", {})
        label = criterion.get("label", "")
        lifetime = criterion.get("lifetime", "")
        outcomes = bo.get("outcomes", [])

        # --- Total Corners (Full Time) — Over/Under lines ---
        if label == "Total Corners" and lifetime == "FULL_TIME":
            for outcome in outcomes:
                otype = outcome.get("type", "")
                odds_millis = outcome.get("odds")
                line_millis = outcome.get("line")
                if odds_millis is None or line_millis is None:
                    continue
                odds_val = odds_millis / 1000
                # line_millis 10500 -> "10_5", 8500 -> "8_5"
                line_val = line_millis / 1000
                line_str = str(line_val).replace(".", "_")
                if otype == "OT_OVER":
                    result[f"corners_over_{line_str}"] = odds_val
                elif otype == "OT_UNDER":
                    result[f"corners_under_{line_str}"] = odds_val

        # --- Asian Handicap (Full Time) ---
        # Each betoffer is one handicap line with 2 outcomes (home / away).
        # ``line`` is in millis: -250 → -0.25, 750 → 0.75, etc.
        # Home is always listed first in outcomes.
        elif label == "Asian Handicap" and lifetime == "FULL_TIME":
            if len(outcomes) < 2:
                continue
            home_out = outcomes[0]
            away_out = outcomes[1]
            home_odds = home_out.get("odds")
            away_odds = away_out.get("odds")
            home_line = home_out.get("line")
            if home_odds is None or away_odds is None or home_line is None:
                continue
            handicap_line = home_line / 1000  # e.g. 750 -> 0.75
            # Store every line: asian_handicap_1_+0_75 / asian_handicap_2_+0_75
            sign = "+" if handicap_line >= 0 else ""
            line_tag = f"{sign}{handicap_line}".replace(".", "_")
            result[f"asian_handicap_1_{line_tag}"] = home_odds / 1000
            result[f"asian_handicap_2_{line_tag}"] = away_odds / 1000

    return result


def _parse_events(data):
    """Parse LivescoreBet events+markets response into standardized dicts."""
    results = []
    categories = data.get("events", {}).get("categories", [])
    if not categories:
        return results

    for category in categories:
        league_name = category.get("name", "")
        cat_id = category.get("originalId", "0")

        for event in category.get("events", []):
            if event.get("state") != "NOTSTARTED":
                continue

            participants = event.get("participants", [])
            if len(participants) < 2:
                continue

            home_name = participants[0].get("name", "")
            away_name = participants[1].get("name", "")
            if not home_name or not away_name:
                continue

            # Parse timestamp
            start_str = event.get("startTime", "")
            try:
                ts = arrow.get(start_str, "YYYY-MM-DD HH:mm:ss").int_timestamp
            except Exception:
                ts = 0

            # Parse event ID
            original_id = event.get("originalId", "0")
            try:
                match_id = int(original_id)
            except (ValueError, TypeError):
                match_id = 0

            try:
                league_id = int(cat_id)
            except (ValueError, TypeError):
                league_id = 0

            match_dict = {
                "match": f"{home_name} - {away_name}",
                "league": league_name,
                "time": ts,
                "league_id": league_id,
                "match_id": match_id,
            }

            # Extract odds from markets
            for market in event.get("markets", []):
                name = market.get("name", "")
                period = market.get("periodType", "")
                selections = market.get("selections", [])

                if name == "Full Time" and period == "FT":
                    for sel in selections:
                        sel_name = sel.get("name", "")
                        odds = sel.get("odds")
                        if odds is None:
                            continue
                        if sel_name == home_name:
                            match_dict["home"] = float(odds)
                        elif sel_name == "Draw":
                            match_dict["draw"] = float(odds)
                        elif sel_name == away_name:
                            match_dict["away"] = float(odds)

                elif name == "Double Chance" and period == "FT":
                    for sel in selections:
                        sel_name = sel.get("name", "")
                        odds = sel.get("odds")
                        if odds is None:
                            continue
                        low = sel_name.lower()
                        if "or draw" in low and "draw or" not in low:
                            match_dict["home_or_draw"] = float(odds)
                        elif low.startswith("draw or"):
                            match_dict["draw_or_away"] = float(odds)
                        else:
                            match_dict["home_or_away"] = float(odds)

                elif name == "Both Teams To Score" and period == "FT":
                    for sel in selections:
                        sel_name = sel.get("name", "")
                        odds = sel.get("odds")
                        if odds is None:
                            continue
                        if sel_name == "Yes":
                            match_dict["btts_yes"] = float(odds)
                        elif sel_name == "No":
                            match_dict["btts_no"] = float(odds)

                elif name == "Total Goals" and period == "FT":
                    for sel in selections:
                        sel_name = sel.get("name", "")
                        odds = sel.get("odds")
                        if odds is None:
                            continue
                        parts = sel_name.split()
                        if len(parts) == 2:
                            direction = parts[0].lower()
                            line = parts[1].replace(".", "_")
                            if direction in ("over", "under"):
                                match_dict[f"{direction}_{line}"] = float(odds)

                elif name == "Total Corners" and period == "FT":
                    for sel in selections:
                        sel_name = sel.get("name", "")
                        odds = sel.get("odds")
                        if odds is None:
                            continue
                        parts = sel_name.split()
                        if len(parts) == 2:
                            direction = parts[0].lower()
                            line = parts[1].replace(".", "_")
                            if direction in ("over", "under"):
                                match_dict[f"corners_{direction}_{line}"] = float(odds)

                elif name == "Asian Handicap" and period == "FT":
                    if len(selections) >= 2:
                        home_sel = selections[0]
                        away_sel = selections[1]
                        h_odds = home_sel.get("odds")
                        a_odds = away_sel.get("odds")
                        h_name = home_sel.get("name", "")
                        if h_odds is not None and a_odds is not None:
                            # Extract handicap line from selection name
                            # e.g. "Arsenal (+0.75)" -> "+0_75"
                            m = re.search(r'([+-]?\d+\.?\d*)', h_name)
                            if m:
                                line_val = float(m.group(1))
                                sign = "+" if line_val >= 0 else ""
                                tag = f"{sign}{line_val}".replace(".", "_")
                                match_dict[f"asian_handicap_1_{tag}"] = float(h_odds)
                                match_dict[f"asian_handicap_2_{tag}"] = float(a_odds)

            results.append(match_dict)

    return results


class LivescoreBet:
    """
    LivescoreBet Nigeria via Kambi REST API.

    Usage:
        lsb = LivescoreBet()
        data = lsb.get_league(Betid.PREMIERLEAGUE)

    Extended markets (corners O/U, Asian handicap) are fetched from the
    Kambi CDN betoffer endpoint per event.  Pass ``extended=False`` to
    ``get_league`` to skip the extra requests.
    """

    _headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    def __init__(self, proxies: Optional[Dict[str, str]] = None):
        self.session = requests.Session()
        self.session.headers.update(self._headers)
        if proxies:
            self.session.proxies = proxies

    # ------------------------------------------------------------------
    # Internal: fetch extended markets from Kambi CDN
    # ------------------------------------------------------------------

    def _fetch_event_betoffers(self, event_id: int) -> Dict[str, Any]:
        """Fetch all betoffers for *event_id* from the Kambi CDN.

        Returns a dict of extra fields (corners, Asian handicap) to merge
        into the match dict, or an empty dict on failure.
        """
        url = _BETOFFER_URL.format(event_id=event_id)
        try:
            res = self.session.get(
                url,
                params={"lang": "en_GB", "market": "NG"},
                timeout=10,
            )
            if res.status_code != 200:
                return {}
            return _parse_betoffers(res.json())
        except Exception:
            return {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_league(
        self,
        league: Betid = Betid.PREMIERLEAGUE,
        extended: bool = True,
    ) -> List[Dict[str, Any]]:
        cat_id = COMPETITION_MAP.get(league)
        if not cat_id:
            return []

        try:
            res = self.session.get(
                _EVENTS_URL,
                params={"categoryid": cat_id},
                headers={"Request-Id": str(uuid.uuid4())},
            )
            if res.status_code != 200:
                return []
            matches = _parse_events(res.json())
        except Exception:
            return []

        if extended:
            for match_dict in matches:
                event_id = match_dict.get("match_id")
                if not event_id:
                    continue
                # Skip CDN call if gateway already provided corners/handicap
                has_corners = any(k.startswith("corners_") for k in match_dict)
                has_ah = any(k.startswith("asian_handicap_") for k in match_dict)
                if has_corners and has_ah:
                    continue
                extra = self._fetch_event_betoffers(event_id)
                match_dict.update(extra)

        return matches

    def get_all(self, extended: bool = True) -> List[Dict[str, Any]]:
        self.data = []
        for league in COMPETITION_MAP:
            self.data += self.get_league(league, extended=extended)
        return self.data

    def get_team(self, team: str, extended: bool = True) -> List[Dict[str, Any]]:
        all_matches = self.get_all(extended=extended)
        return [m for m in all_matches if team.lower() in m["match"].lower()]
