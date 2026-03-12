"""
LivescoreBet Nigeria odds extraction via Kambi REST API.

Usage:
    from NaijaBet_Api.bookmakers.livescorebet import LivescoreBet
    from NaijaBet_Api.id import Betid

    lsb = LivescoreBet()
    data = lsb.get_league(Betid.PREMIERLEAGUE)
"""

import uuid
import requests
import arrow
from NaijaBet_Api.id import Betid
from typing import List, Dict, Any, Optional


_BASE = "https://gateway-ng.livescorebet.com/sportsbook/gateway"
_EVENTS_URL = _BASE + "/v3/view/events/matches"

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

            results.append(match_dict)

    return results


class LivescoreBet:
    """
    LivescoreBet Nigeria via Kambi REST API.

    Usage:
        lsb = LivescoreBet()
        data = lsb.get_league(Betid.PREMIERLEAGUE)
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

    def get_league(self, league: Betid = Betid.PREMIERLEAGUE) -> List[Dict[str, Any]]:
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
            return _parse_events(res.json())
        except Exception:
            return []

    def get_all(self) -> List[Dict[str, Any]]:
        self.data = []
        for league in COMPETITION_MAP:
            self.data += self.get_league(league)
        return self.data

    def get_team(self, team: str) -> List[Dict[str, Any]]:
        all_matches = self.get_all()
        return [m for m in all_matches if team.lower() in m["match"].lower()]
