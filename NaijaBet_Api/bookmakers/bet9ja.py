from NaijaBet_Api.bookmakers.BaseClass import BookmakerBaseClass
from NaijaBet_Api.utils.normalizer import bet9ja_match_normalizer
from NaijaBet_Api.utils import jsonpaths
from NaijaBet_Api.id import Betid


"""
[summary]
"""


class Bet9ja(BookmakerBaseClass):
    """
     This class provides access to https://sports.bet9ja.com 's odds data.

     it provides a variety of methods to query the endpoints and obtain
     odds data at a competiton and match level.

    Attributes:
        session: holds a requests session object for the class as a static variable.
    """

    _site = 'bet9ja'
    _url = "https://bet9ja.com"
    _headers = {
        "sec-ch-ua": '"Chromium";v="94", "Microsoft Edge";v="94", ";Not A Brand";v="99"',
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Chrome/94.0.4606.81",
        "referer": "https://sports.bet9ja.com",
    }

    def normalizer(self, args):
        return bet9ja_match_normalizer(jsonpaths.bet9ja_validator(args))

    def _fetch_extra_markets(self, league, market_type, validator_func):
        """Fetch extra market data (corners or Asian handicap) for a league."""
        try:
            url = league.to_endpoint(self.site, market_type=market_type)
            res = self.session.get(url=url, headers=self._headers)
            if res.status_code == 200:
                return validator_func(res.json())
        except Exception:
            pass
        return []

    def get_league(self, league: Betid = Betid.PREMIERLEAGUE):
        """
        Provides access to available league level odds for unplayed matches,
        including corners over/under and Asian handicap markets.

        Returns:
            list[dict]: Normalized match data with all available markets.
        """
        # Get main markets (1X2, DC, OU, BTTS)
        main_results = super().get_league(league)
        if not main_results:
            return main_results

        # Fetch corners and Asian handicap from their respective endpoints
        corners = self._fetch_extra_markets(
            league, 'corners', jsonpaths.bet9ja_corners_validator
        )
        asian_handicap = self._fetch_extra_markets(
            league, 'asian_handicap', jsonpaths.bet9ja_asian_handicap_validator
        )

        # Merge extra markets into main results by match_id
        return jsonpaths.merge_bet9ja_markets(main_results, corners, asian_handicap)
