import json
import re
from typing import ChainMap
import arrow
from pathlib import Path
import difflib
from NaijaBet_Api.utils.logger import get_logger

logger = get_logger(__name__)


def match_normalizer(list, pathstr: str):
    path = Path(__file__).parent / pathstr
    if list is None:
        return {}
    data = list[:]

    def helper(string):
        with open(path, "r") as f:
            normalizer = json.load(f)
            try:
                return normalizer[string]
            except KeyError:
                logger.warning(f"{string} not found in {pathstr} normalizer")
                path_b9 = Path(__file__).parent / "bet9ja_normalizer.json"
                path_bk = Path(__file__).parent / "betking_normalizer.json"
                path_nb = Path(__file__).parent / "nairabet_normalizer.json"

                map = ChainMap(
                    json.load(open(path_b9, "r")), json.load(open(path_bk, "r")), json.load(open(path_nb, "r")))
                try:
                    return map[string]
                except KeyError:
                    logger.warning(f"{string} not found in normalizer")
                    res = difflib.get_close_matches(string, map.keys(), 1, 0.8)
                    logger.warning(f'found possible matches {res}')
                    if res:
                        return map[res[0]]
                    else:
                        logger.warning(f"No close matches found for {string}, returning original")
                        return string

    # List of odds fields that should be converted to floats
    odds_fields = ['home', 'draw', 'away', 'home_or_draw', 'home_or_away', 'draw_or_away',
                   'over_0_5', 'under_0_5', 'over_1_5', 'under_1_5',
                   'over_2_5', 'under_2_5', 'over_3_5', 'under_3_5',
                   'over_4_5', 'under_4_5', 'over_5_5', 'under_5_5',
                   'over_6_5', 'under_6_5', 'btts_yes', 'btts_no']

    # Dynamic odds fields: corners_*, ah_*, asian_handicap_*
    dynamic_prefixes = ('corners_over_', 'corners_under_',
                        'ah_minus_', 'ah_plus_', 'ah_0_',
                        'asian_handicap_1', 'asian_handicap_2')

    for event in data:
        teams = event.get("match", None)
        if teams is not None:
            home, away = re.split(r"\s-\s", teams, maxsplit=1)
            home = helper(home.strip())
            away = helper(away.strip())
            event["match"] = "{0} - {1}".format(home, away)

        time = event.get("time", None)
        if time is not None:
            event["time"] = arrow.get(event["time"]).int_timestamp

        league = event.get("league", None)
        if league is not None:
            event['league'] = helper(event['league'])

        # Convert odds fields from strings to floats
        for field in odds_fields:
            if field in event and event[field] is not None:
                try:
                    event[field] = float(event[field])
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert {field}={event[field]} to float")
                    pass

        # Convert dynamic odds fields (corners, Asian handicap) to floats
        for field in [k for k in event]:
            if field.startswith(dynamic_prefixes) and event[field] is not None:
                try:
                    event[field] = float(event[field])
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert {field}={event[field]} to float")
                    pass

    return data


def bet9ja_match_normalizer(list):
    return match_normalizer(list, "bet9ja_normalizer.json")


def nairabet_match_normalizer(list):
    return match_normalizer(list, "nairabet_normalizer.json")


def betking_match_normalizer(list):
    return match_normalizer(list, "betking_normalizer.json")
