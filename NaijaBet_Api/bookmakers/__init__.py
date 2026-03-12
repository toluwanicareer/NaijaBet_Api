"""Bookmakers module

Available bookmakers:
- Bet9ja: Full support, no browser automation needed
- Betking: Standard version (Cloudflare blocked), Playwright version available
- BetkingAltenar: Betking via Altenar API, no browser needed
- Nairabet: Legacy (API dead)
- NairabetAltenar: Nairabet via Altenar API
- TwentyTwoBet: 22bet.ng via 1xBet LineFeed API
- OneXBet: 1xbet.ng via 1xBet LineFeed API (supports proxies)
- Surebet247: Surebet247 via direct WebSocket (no browser needed)
- SevenKBet: 7k.bet via 442hattrick REST API (no browser needed)
- LivescoreBet: LivescoreBet Nigeria via Kambi REST API
"""

from .bet9ja import Bet9ja
from .betking import Betking
from .nairabet import Nairabet
from .nairabet_altenar import NairabetAltenar
from .betking_altenar import BetkingAltenar
from .twentytwobet import TwentyTwoBet
from .onexbet import OneXBet
from .sevenk import SevenKBet
from .livescorebet import LivescoreBet

# Surebet247 (optional - only if websockets + msgpack installed)
try:
    from .surebet247 import Surebet247
except ImportError:
    pass

# Playwright versions (optional - only if playwright installed)
try:
    from .betking_playwright import BetkingPlaywright
except ImportError:
    pass

__all__ = ['Bet9ja', 'Betking', 'Nairabet', 'NairabetAltenar',
           'BetkingAltenar', 'TwentyTwoBet', 'OneXBet', 'SevenKBet',
           'LivescoreBet']

# Add optional exports if available
for _name in ('Surebet247', 'BetkingPlaywright'):
    if _name in dir():
        __all__.append(_name)
