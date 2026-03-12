from NaijaBet_Api.bookmakers.onexbet_base import OneXBetBase, ODDS_MAP  # noqa: F401
from typing import Dict, Optional


class TwentyTwoBet(OneXBetBase):
    """
    Bookmaker class for 22bet.ng (1xBet white-label).

    Uses the /service-api/LineFeed/ API endpoints.
    Fetches event details for full over/under lines.
    Supports proxy configuration for requests.
    """

    _site = 'twentytwobet'
    _domain = 'https://22bet.ng'
    _country = 159
    _partner = None
    _referer_path = "/line/Football/"

    def __init__(self, proxies: Optional[Dict[str, str]] = None):
        super().__init__(proxies=proxies)
