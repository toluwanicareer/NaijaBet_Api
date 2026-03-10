"""Bookmakers module

Available bookmakers:
- Bet9ja: Full support, no browser automation needed
- Betking: Standard version (Cloudflare blocked), Playwright version available
- BetkingAltenar: Betking via Altenar API, no browser needed
- Nairabet: Legacy (API dead)
- NairabetAltenar: Nairabet via Altenar API
"""

from .bet9ja import Bet9ja
from .betking import Betking
from .nairabet import Nairabet
from .nairabet_altenar import NairabetAltenar
from .betking_altenar import BetkingAltenar

# Playwright version (optional - only if playwright installed)
try:
    from .betking_playwright import BetkingPlaywright
    __all__ = ['Bet9ja', 'Betking', 'Nairabet', 'BetkingPlaywright',
               'NairabetAltenar', 'BetkingAltenar']
except ImportError:
    __all__ = ['Bet9ja', 'Betking', 'Nairabet',
               'NairabetAltenar', 'BetkingAltenar']
