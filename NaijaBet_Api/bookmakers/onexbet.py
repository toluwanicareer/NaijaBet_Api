from NaijaBet_Api.bookmakers.onexbet_base import OneXBetBase
from typing import Dict, Optional


class OneXBet(OneXBetBase):
    """
    Bookmaker class for 1xbet.ng.

    Uses the /service-api/LineFeed/ API endpoints (same format as 22bet).
    1xbet.ng has aggressive rate limiting — retry with backoff is built in.
    Supports proxy configuration for requests.
    """

    _site = 'onexbet'
    _domain = 'https://1xbet.ng'
    _country = 132
    _partner = 159
    _referer_path = "/en/line/football/"

    def __init__(self, proxies: Optional[Dict[str, str]] = None):
        super().__init__(proxies=proxies)
