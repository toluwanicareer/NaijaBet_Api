"""
Surebet247 odds extraction via direct WebSocket connection.
Connects to GR8 Tech SignalR MessagePack feed — no browser needed.

Installation:
    pip install websockets msgpack

Usage:
    from NaijaBet_Api.bookmakers.surebet247 import Surebet247
    from NaijaBet_Api.id import Betid

    with Surebet247() as sb:
        data = sb.get_league(Betid.PREMIERLEAGUE)
        print(f"Got {len(data)} matches")
"""

import asyncio
import threading
import websockets
import msgpack
from NaijaBet_Api.id import Betid
from typing import List, Dict, Any, Optional


WS_URL = "wss://sport-iframe.serhjs.xyz/direct-feed/feed?brand=CL38B1&X-Api-Key=b8b92942-ce6a-44e8-a5d5-6bf407e316a2"
CONTEXT = ["en", "MOBILE_WEB", "CL38B1", "", "NGN"]

# Betid -> (slug, uuid) for constructing tournament page URLs
TOURNAMENT_MAP = {
    # === England ===
    Betid.PREMIERLEAGUE: ("premier-league", "7f5506e872d14928adf0613efa509494"),
    Betid.CHAMPIONSHIP: ("championship", "eeb107510b84417f833551f3b6e2351c"),
    Betid.LEAGUE_ONE: ("league-one", "f8bee2c7dcdb40fdb604f1a5c14976b6"),
    Betid.LEAGUE_TWO: ("league-two", "ddab861df0aa4411bb5b1f63fcd82a71"),
    Betid.ENGLAND_FA_CUP: ("fa-cup", "9cb76bfbd9d24fa68eafafde5b7dff58"),
    Betid.ENGLAND_EFL_CUP: ("league-cup", "62f32af089604eb895af4b7b1dabe922"),
    Betid.ENGLAND_NATIONAL_LEAGUE: ("national-league", "5ca68aadebc04004b4fdace2fbcfb508"),
    Betid.ENGLAND_ISTHMIAN_LEAGUE: ("isthmian-league", "32d5d1b4edcd486db3e5fd0362b78213"),
    Betid.ENGLAND_WSL: ("women-super-league", "46a475a24c424a94af4f7e35e151650f"),
    # === Germany ===
    Betid.BUNDESLIGA: ("bundesliga", "966112317e2c4ee28d5a36df840662d6"),
    Betid.BUNDESLIGA_2: ("bundesliga-2", "a431130368c648c7845ace77e0a68240"),
    Betid.GERMANY_3_LIGA: ("liga-3", "f9360dc835ce408392e34ac68dfa6ff4"),
    Betid.GERMANY_DFB_POKAL: ("cup", "86eec50260fc49c68c36946427ccb1ac"),
    # === Spain ===
    Betid.LALIGA: ("laliga", "d84ce93378454b0fa61d58b2696a950b"),
    Betid.SPAIN_SEGUNDA_DIVISION: ("segunda-division", "1737bc86744c420aa45ecb49ca345fea"),
    Betid.SPAIN_COPA_DEL_REY: ("copa-del-rey", "a8d2673bcb584ba2b46102401f50d2a8"),
    # === France ===
    Betid.LIGUE_1: ("ligue-1", "254e4ecf1eb84a73b37b9cedffac646d"),
    Betid.LIGUE_2: ("ligue-2", "e1e8f1ea149a406eb01cab13a8900f5a"),
    Betid.FRANCE_NATIONAL: ("national", "3caa77cfd26645d2abd3727198907f63"),
    Betid.COUPE_DE_FRANCE: ("cup", "bda19319df0d4bf9871b22b5c9ba75e2"),
    # === Italy ===
    Betid.SERIEA: ("serie-a", "6d80f3f3fa35431b80d50f516e4ce075"),
    Betid.ITALY_SERIE_B: ("serie-b", "2b71505170924638acfb8474a6635045"),
    Betid.COPPA_ITALIA: ("cup", "716735174b994d60a375730e4aab2a1d"),
    # === Netherlands ===
    Betid.NETHERLANDS_EREDIVISIE: ("eredivisie", "00bf4eb20b8d4ad8b43b46fa5dda5be1"),
    Betid.NETHERLANDS_EERSTE_DIVISIE: ("eerste-divisie", "c6df0f8d829c400497cdd69d107e6ac2"),
    # === Portugal ===
    Betid.PORTUGAL_PRIMEIRA_LIGA: ("primeira-liga", "c2fc983af0c643be85e60663d28585ce"),
    Betid.PORTUGAL_SEGUNDA_LIGA: ("segunda-liga", "5f599a775dc8419aa08c8516b0a0f918"),
    # === Scotland ===
    Betid.SCOTLAND_PREMIERSHIP: ("premiership", "f4a385d5ac43479b902462b206705e77"),
    Betid.SCOTLAND_CHAMPIONSHIP: ("championship", "b9b3faa535c843d88eccce7516f2cdee"),
    Betid.SCOTLAND_LEAGUE_ONE: ("league-one", "3e4263310bbf420685824264cca7db0e"),
    Betid.SCOTLAND_LEAGUE_TWO: ("league-two", "83613004614e43b1bdd88d9744e2225e"),
    # === Belgium ===
    Betid.BELGIUM_PRO_LEAGUE: ("pro-league", "e5bdb73049d54f40a61723262068f462"),
    Betid.BELGIUM_CHALLENGER_PRO_LEAGUE: ("challenger-pro-league", "82d42895a2284836b52279f443cdb317"),
    # === Turkey ===
    Betid.TURKEY_SUPER_LIG: ("super-league", "5af164b314434cd4a4e8a30b0724eeab"),
    Betid.TURKEY_TFF_1_LIG: ("tff-first-league", "1f582be4bbdc4522a07a70e5e82ec6ff"),
    Betid.TURKEY_TFF_2_LIG: ("tff-second-league", "0f50fe11c2414a63a9f83401bfeaf8a4"),
    # === Austria ===
    Betid.AUSTRIA_BUNDESLIGA: ("bundesliga", "fbef856590354ec087ea5a6b5f1fed5f"),
    Betid.AUSTRIA_2_LIGA: ("liga-2", "aafc740b540a4d348b12a6280a527371"),
    # === Switzerland ===
    Betid.SWITZERLAND_SUPER_LEAGUE: ("super-league", "b9ca937509c1440aaaacb4fd7c593b80"),
    Betid.SWITZERLAND_CHALLENGE_LEAGUE: ("challenge-league", "0aad65041f094c72a235377148518019"),
    # === Denmark ===
    Betid.DENMARK_SUPERLIGA: ("superliga", "3b04779beeb04a1f8c4d3b61344e99d6"),
    Betid.DENMARK_1ST_DIVISION: ("first-division", "258ca3af57e4454b92efa4d04cb3642a"),
    # === Norway ===
    Betid.NORWAY_ELITESERIEN: ("eliteserien", "2d4b9686427840a89cc28a65f05ad189"),
    # === Greece ===
    Betid.GREECE_SUPER_LEAGUE: ("super-league-1", "abcb0f035b2b4d5b90ee2dd481487c98"),
    # === Czech Republic ===
    Betid.CZECH_REPUBLIC_LIGA: ("division-1", "ba352b35c9674ef0bc36ad7b24c45719"),
    # === Poland ===
    Betid.POLAND_EKSTRAKLASA: ("ekstraklasa", "c930c57556f4413d8805cb9ae8d4d5a1"),
    # === Romania ===
    Betid.ROMANIA_LIGA_1: ("liga-1", "27d0a98c24754fef95f2b696bf7f4545"),
    # === Croatia ===
    Betid.CROATIA_HNL: ("hnl", "3b7949ae40024f659c48a05d8af5d243"),
    # === Serbia ===
    Betid.SERBIA_SUPER_LIGA: ("super-liga", "6bb44beb20a7451292823d7434d8d0ed"),
    # === Hungary ===
    Betid.HUNGARY_NB_I: ("nb-i", "7eb255d794ec4ebf9eb03c1eb6c981f8"),
    # === Slovenia ===
    Betid.SLOVENIA_PRVA_LIGA: ("1-snl", "6d79756283b448d9a9f80b8a67b8d8db"),
    # === Estonia ===
    Betid.ESTONIA_PREMIUM_LIIGA: ("meistriliiga", "b40fa0521cc7410db93fd9b7befa4248"),
    # === Latvia ===
    Betid.LATVIA_VIRSLIGA: ("virsliga", "d393598efa2a48969d1f49db064278ea"),
    # === Lithuania ===
    Betid.LITHUANIA_A_LIGA: ("a-lyga", "88344e445d6649009416c21e5b00123b"),
    # === South America ===
    Betid.COPA_LIBERTADORES: ("copa-libertadores", "ddccbf1be9ef4c8195ae4645d793899f"),
    Betid.BRAZIL_SERIE_A: ("serie-a", "0f7c91bcf24e4d62a76e7d9d3fee8177"),
    Betid.BRAZIL_SERIE_B: ("serie-b", "dd8f2355b4e3459090ebbcb6db9c7854"),
    Betid.ARGENTINA_PRIMERA_DIVISION: ("liga-profesional", "1bcb9cbd374a481faa39bd89c66bdcab"),
    Betid.COLOMBIA_PRIMERA_A: ("primera-a", "4230df881fd14f319c5499c86a7e647d"),
    Betid.COLOMBIA_PRIMERA_B: ("primera-b", "4fe9a1fe9a1c44488588591ef136eb19"),
    Betid.CHILE_PRIMERA_DIVISION: ("primera-division", "fc7f16ba2ec24f528179d20490404fb5"),
    Betid.ECUADOR_LIGA_PRO: ("serie-a", "dacdb36b733447cba68983a05b5c1412"),
    Betid.PARAGUAY_PRIMERA_DIVISION: ("primera-division", "6703418ed5c24c0896d2d0cb03b2859e"),
    Betid.URUGUAY_PRIMERA_DIVISION: ("primera-division", "cb7e96bacf1c47a5a66ee27603dfa579"),
    # === North & Central America ===
    Betid.USA_MLS: ("mls", "f150eebff97845efb168d2c2c5aa2290"),
    Betid.USA_NWSL: ("women-nwsl", "ae04755748e746ed973259fae30ff7bd"),
    Betid.USA_USL_CHAMPIONSHIP: ("usl-championship", "117dc49af25b45e8932fc89bd8065139"),
    Betid.MEXICO_LIGA_MX: ("liga-mx", "ec048669c38c453eb6eb734421134361"),
    Betid.MEXICO_LIGA_MX_WOMEN: ("women-liga-mx", "b8126867757e4bfda93c0455b1e1d451"),
    Betid.MEXICO_LIGA_EXPANSION: ("liga-de-expansion-mx", "a9b18bb0d31b42f1a33d31cabcf20444"),
    Betid.CONCACAF_CHAMPIONS_CUP: ("concacaf-champions-cup", "c5dcf8c02fc84009920e9487838fa010"),
    Betid.HONDURAS_LIGA_NACIONAL: ("liga-nacional", "a1ff5a57056c43d28dd97f92c2335570"),
    Betid.GUATEMALA_LIGA_NACIONAL: ("liga-nacional", "e83fc447dc9f425db589764f3ae4b8b2"),
    # === Africa ===
    Betid.SOUTH_AFRICA_PREMIERSHIP: ("psl", "92d74199af3a4f4e8ca57b5da026ea3a"),
    Betid.ALGERIA_LIGUE_1: ("ligue-1", "50969496258149c582f8c08beeca6843"),
    # === Asia ===
    Betid.JAPAN_J_LEAGUE: ("j1-league", "df3f21adc87f4370abcf475a047b57eb"),
    Betid.SOUTH_KOREA_K_LEAGUE_1: ("k-league-1", "763fafa353c64330adac5f3598acd73c"),
    Betid.SOUTH_KOREA_K_LEAGUE_2: ("k-league-2", "30643f110baf41d394d53d10684dede3"),
    Betid.INDIA_SUPER_LEAGUE: ("super-league", "18c5555f551344e1bb8359c46937fac4"),
    Betid.INDIA_I_LEAGUE: ("i-league", "75e13fe5d83a406297c4042ba4817b1a"),
    Betid.VIETNAM_V_LEAGUE: ("v-league", "abf568a518f5408184783dd638178bfe"),
    Betid.THAILAND_LEAGUE_1: ("thai-league", "1872d3b387aa4eeb83672e2cab7d26e9"),
    # === Middle East ===
    Betid.SAUDI_PRO_LEAGUE: ("professional-league", "da8b06ab4b864b8e99c34d7c31aa361f"),
    Betid.QATAR_STARS_LEAGUE: ("stars-league", "aa8ed37c4db64b54aedacb13830a11a3"),
    # === Australia ===
    Betid.AUSTRALIA_A_LEAGUE: ("a-league", "e0b463e4d91c4070b16daa12a1ab2878"),
    # === UEFA ===
    Betid.WC_QUAL_UEFA: ("european-qualification", "79b09d96d0bd401188a4188142607c80"),
    Betid.WORLD_CUP_2026: ("group-stage", "c19cb5ffb4404c31b869b53dd90161de"),
}

# Outcome ID -> field name mappings (market_type, outcome_id)
_OUTCOME_MAP = {
    (2, 0): "home", (2, 1): "draw", (2, 3): "away",
    (3, 10): "home_or_draw", (3, 8): "home_or_away", (3, 9): "draw_or_away",
    (28, 14): "btts_yes", (28, 15): "btts_no",
    (5, 4): "over", (5, 5): "under",
    (4, 86): "asian_handicap_1", (4, 87): "asian_handicap_2",   # Asian Handicap
}

# Period 4 = Corners in the GR8 Tech feed
_CORNERS_PERIOD = 4

# --- SignalR MessagePack protocol helpers ---


def _encode_varint(value):
    result = bytearray()
    while value > 0x7F:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.append(value & 0x7F)
    return bytes(result)


def _pack_signalr(msg):
    payload = msgpack.packb(msg)
    return _encode_varint(len(payload)) + payload


def _unpack_signalr(data):
    messages = []
    offset = 0
    while offset < len(data):
        length = 0
        shift = 0
        while True:
            if offset >= len(data):
                return messages
            byte = data[offset]
            length |= (byte & 0x7F) << shift
            offset += 1
            if not (byte & 0x80):
                break
            shift += 7
        if offset + length > len(data):
            break
        payload = data[offset:offset + length]
        try:
            messages.append(msgpack.unpackb(payload, raw=False))
        except Exception:
            pass
        offset += length
    return messages


# --- Response parsers ---


def _parse_events(events_data, league_name):
    """Parse events from GetRichEventsByTournamentIdAndStage response."""
    events = {}
    for chunk in events_data:
        if not isinstance(chunk, list) or len(chunk) < 2:
            continue
        for item in chunk[1]:
            if not isinstance(item, list) or len(item) < 3:
                continue
            ev_id = item[1]
            details = item[2]
            if not isinstance(details, list) or len(details) < 11:
                continue
            competitors = details[10]
            home = competitors[0][1] if competitors and len(competitors) > 0 else ""
            away = competitors[1][1] if competitors and len(competitors) > 1 else ""
            ts = details[4]
            if not isinstance(ts, (int, float)):
                ts = 0
            events[ev_id] = {
                "event_id": ev_id,
                "match": f"{home} - {away}",
                "home_team": home,
                "away_team": away,
                "timestamp": ts,
                "league": league_name,
            }
    return events


def _parse_markets(markets_data):
    """Parse full market data into per-event odds dicts."""
    odds = {}
    for chunk in markets_data:
        if not isinstance(chunk, list) or len(chunk) < 2:
            continue
        items = chunk[1] if isinstance(chunk[1], list) else []
        for item in items:
            if not isinstance(item, list) or len(item) < 3:
                continue
            header = item[1]
            if not isinstance(header, list) or len(header) < 4:
                continue
            ev_id, period, mtype, sub = header[0], header[1], header[2], header[3]
            # Accept:
            #   period=1, sub=0: 1X2(2), DC(3), O/U goals(5), BTTS(28), Asian HC(4)
            #   period=66, sub=0: Corners O/U(5)
            is_standard = period == 1 and sub == 0 and mtype in (2, 3, 4, 5, 28)
            is_corners = period == _CORNERS_PERIOD and sub == 0 and mtype == 5
            if not (is_standard or is_corners):
                continue
            if ev_id not in odds:
                odds[ev_id] = {}
            market_data = item[2]
            if not isinstance(market_data, list) or not market_data:
                continue
            lines_groups = market_data[0]
            if not isinstance(lines_groups, list):
                continue
            for lg in lines_groups:
                if not isinstance(lg, list) or len(lg) < 2:
                    continue
                line_params = lg[0]
                outcomes = lg[1]
                line_val = None
                if line_params and isinstance(line_params[0], list) and line_params[0]:
                    line_val = line_params[0][0]
                if not isinstance(outcomes, list):
                    continue
                for o in outcomes:
                    if not isinstance(o, list) or len(o) < 2:
                        continue
                    oid_arr = o[0]
                    odds_raw = o[1]
                    if not isinstance(oid_arr, list) or not oid_arr:
                        continue
                    oid = oid_arr[0]
                    if not isinstance(odds_raw, (int, float)):
                        continue
                    odds_val = odds_raw / 100.0
                    key = (mtype, oid)
                    if key in _OUTCOME_MAP:
                        name = _OUTCOME_MAP[key]
                        if is_corners and mtype == 5 and line_val is not None:
                            # Corners O/U: corners_over_8_5, corners_under_8_5
                            line_key = str(line_val).replace(".", "_")
                            field = f"corners_{name}_{line_key}"
                        elif mtype == 5 and line_val is not None:
                            # Goals O/U: over_2_5, under_2_5
                            line_key = str(line_val).replace(".", "_")
                            field = f"{name}_{line_key}"
                        elif mtype == 4 and line_val is not None:
                            # Asian Handicap: asian_handicap_1_-0_5 etc.
                            line_key = str(line_val).replace(".", "_")
                            field = f"{name}_{line_key}"
                        else:
                            field = name
                        odds[ev_id][field] = odds_val

    # Post-process: pick best Asian Handicap line per event
    for ev_id in odds:
        _pick_asian_handicap_line(odds[ev_id])

    return odds


def _pick_asian_handicap_line(ev_odds):
    """Post-process Asian Handicap: pick the line closest to 0 for the
    convenience fields asian_handicap_1, asian_handicap_2, asian_handicap_line.

    Called once per event after all markets have been parsed.
    Reads the per-line fields (asian_handicap_1_X, asian_handicap_2_X)
    and selects the pair whose absolute line value is smallest.
    """
    best_line = None
    best_abs = None
    # Scan for all stored AH lines
    for key in list(ev_odds.keys()):
        if not key.startswith("asian_handicap_1_"):
            continue
        line_key = key[len("asian_handicap_1_"):]
        away_key = f"asian_handicap_2_{line_key}"
        if away_key not in ev_odds:
            continue
        # Reconstruct the numeric line from the key (e.g. "-1_5" -> -1.5)
        line_str = line_key.replace("_", ".", 1)
        # Handle negative lines like "-1_5" -> already "-1.5"
        # Handle keys like "0" -> "0"
        try:
            lv = float(line_str)
        except (TypeError, ValueError):
            continue
        a = abs(lv)
        if best_abs is None or a < best_abs:
            best_abs = a
            best_line = line_key

    if best_line is not None:
        line_str = best_line.replace("_", ".", 1)
        ev_odds["asian_handicap_1"] = ev_odds[f"asian_handicap_1_{best_line}"]
        ev_odds["asian_handicap_2"] = ev_odds[f"asian_handicap_2_{best_line}"]
        ev_odds["asian_handicap_line"] = line_str


def _parse_main_markets(markets_data):
    """Parse 1X2 odds from GetMainMarketsByProfileAndEventIds response."""
    odds = {}
    for chunk in markets_data:
        if not isinstance(chunk, list) or len(chunk) < 2:
            continue
        items = chunk[1] if isinstance(chunk[1], list) else []
        for item in items:
            if not isinstance(item, list) or len(item) < 3:
                continue
            header = item[1]
            if not isinstance(header, list) or len(header) < 1:
                continue
            ev_id = header[0]
            if ev_id not in odds:
                odds[ev_id] = {}
            market_data = item[2]
            if not isinstance(market_data, list) or not market_data:
                continue
            lines_groups = market_data[0]
            if not isinstance(lines_groups, list):
                continue
            for lg in lines_groups:
                if not isinstance(lg, list) or len(lg) < 2:
                    continue
                outcomes = lg[1]
                if not isinstance(outcomes, list):
                    continue
                for o in outcomes:
                    if not isinstance(o, list) or len(o) < 2:
                        continue
                    oid_arr = o[0]
                    odds_raw = o[1]
                    if not isinstance(oid_arr, list) or not oid_arr:
                        continue
                    oid = oid_arr[0]
                    if not isinstance(odds_raw, (int, float)):
                        continue
                    odds_val = odds_raw / 100.0
                    key = (2, oid)  # main markets are 1X2 (type 2)
                    if key in _OUTCOME_MAP:
                        odds[ev_id][_OUTCOME_MAP[key]] = odds_val
    return odds


def _build_results(events, odds_map, league_name):
    """Combine events + odds into standardized output format."""
    results = []
    for ev_id, ev in events.items():
        match_dict = {
            "match": ev["match"],
            "league": league_name,
            "time": ev["timestamp"],
            "league_id": 0,
            "match_id": int(ev_id) if ev_id.isdigit() else 0,
        }
        od = odds_map.get(ev_id, {})
        match_dict.update(od)
        results.append(match_dict)
    return results


class Surebet247:
    """
    Surebet247 bookmaker via direct WebSocket to GR8 Tech SignalR feed.
    No browser needed — uses websockets + msgpack.

    Usage:
        with Surebet247() as sb:
            data = sb.get_league(Betid.PREMIERLEAGUE)
    """

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._ws = None
        self._req_id = 0

    def __enter__(self):
        self._start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop()

    def _start(self):
        if self._loop is not None:
            return
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()
        self._run(self._connect())

    def _stop(self):
        if self._ws:
            try:
                self._run(self._ws.close())
            except Exception:
                pass
            self._ws = None
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
        if self._loop:
            self._loop.close()
            self._loop = None

    def _run(self, coro):
        """Run async coroutine on the background event loop."""
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=self.timeout + 30)

    async def _connect(self):
        self._ws = await websockets.connect(WS_URL, max_size=10_000_000)
        await self._ws.send('{"protocol":"messagepack","version":1}\x1e')
        await self._ws.recv()  # handshake response

    def _next_id(self):
        self._req_id += 1
        return self._req_id

    async def _ws_stream(self, method, args, timeout=None, idle_timeout=3):
        """Send StreamInvocation and collect responses with idle timeout."""
        timeout = timeout or self.timeout
        req_id = str(self._next_id())
        msg = [4, {}, req_id, method, args]
        await self._ws.send(_pack_signalr(msg))

        all_data = []
        got_data = False
        while True:
            t = idle_timeout if got_data else timeout
            try:
                raw = await asyncio.wait_for(self._ws.recv(), timeout=t)
            except asyncio.TimeoutError:
                break
            if isinstance(raw, str):
                continue
            for m in _unpack_signalr(raw):
                if not isinstance(m, list) or len(m) < 3:
                    continue
                if m[0] == 2 and m[2] == req_id:
                    all_data.append(m[3])
                    got_data = True
                elif m[0] == 3 and m[2] == req_id:
                    return all_data
        return all_data

    async def _ws_fire_and_collect(self, requests, timeout=None, idle_timeout=4):
        """Fire multiple StreamInvocations, collect all responses by req_id."""
        timeout = timeout or self.timeout
        for req_id, method, args in requests:
            msg = [4, {}, str(req_id), method, args]
            await self._ws.send(_pack_signalr(msg))

        pending = {str(r[0]) for r in requests}
        results = {str(r[0]): [] for r in requests}
        got_any = False

        while pending:
            t = idle_timeout if got_any else timeout
            try:
                raw = await asyncio.wait_for(self._ws.recv(), timeout=t)
            except asyncio.TimeoutError:
                break
            if isinstance(raw, str):
                continue
            for m in _unpack_signalr(raw):
                if not isinstance(m, list) or len(m) < 3:
                    continue
                rid = m[2]
                if m[0] == 2 and rid in pending:
                    results[rid].append(m[3])
                    got_any = True
                elif m[0] == 3 and rid in pending:
                    pending.discard(rid)

        return results

    async def _get_events(self, tournament_id):
        """Fetch events for a tournament."""
        return await self._ws_stream(
            "GetRichEventsByTournamentIdAndStage",
            [tournament_id, 1, CONTEXT],
        )

    async def _get_full_markets(self, event_ids):
        """Fetch full markets (1X2, DC, O/U, BTTS, Asian HC, Corners) for event IDs."""
        all_odds = {}
        BATCH = 50
        for i in range(0, len(event_ids), BATCH):
            batch = event_ids[i:i + BATCH]
            data = await self._ws_stream(
                "GetMarketsByEventIds",
                [batch, "true", CONTEXT],
                timeout=self.timeout,
                idle_timeout=3,
            )
            all_odds.update(_parse_markets(data))
        return all_odds

    async def _get_main_markets(self, event_ids):
        """Fetch 1X2 odds only via main markets profile."""
        return await self._ws_stream(
            "GetMainMarketsByProfileAndEventIds",
            ["pro_main_period", event_ids, 4, 1, CONTEXT],
        )

    def get_league(self, league: Betid = Betid.PREMIERLEAGUE) -> List[Dict[str, Any]]:
        """
        Fetch full odds for a league (1X2, DC, O/U, BTTS, Asian HC, Corners).

        Args:
            league: League to fetch (from Betid enum)

        Returns:
            List of match dicts with standardized odds fields
        """
        if self._ws is None:
            self._start()

        entry = TOURNAMENT_MAP.get(league)
        if not entry:
            return []

        slug, tournament_id = entry
        league_name = slug.replace("-", " ").title()

        async def _fetch():
            events_data = await self._get_events(tournament_id)
            events = _parse_events(events_data, league_name)
            if not events:
                return []
            event_ids = list(events.keys())
            odds_map = await self._get_full_markets(event_ids)
            return _build_results(events, odds_map, league_name)

        return self._run(_fetch())

    def get_league_fast(self, league: Betid = Betid.PREMIERLEAGUE) -> List[Dict[str, Any]]:
        """
        Fetch 1X2 odds only. Faster than get_league().

        Args:
            league: League to fetch

        Returns:
            List of match dicts with 1X2 odds only
        """
        if self._ws is None:
            self._start()

        entry = TOURNAMENT_MAP.get(league)
        if not entry:
            return []

        slug, tournament_id = entry
        league_name = slug.replace("-", " ").title()

        async def _fetch():
            events_data = await self._get_events(tournament_id)
            events = _parse_events(events_data, league_name)
            if not events:
                return []
            event_ids = list(events.keys())
            main_data = await self._get_main_markets(event_ids)
            odds_map = _parse_main_markets(main_data)
            return _build_results(events, odds_map, league_name)

        return self._run(_fetch())

    def get_all(self) -> List[Dict[str, Any]]:
        """
        Fetch full odds for all mapped leagues using batched WebSocket calls.

        Returns:
            List of all matches from all leagues with full odds
        """
        if self._ws is None:
            self._start()

        async def _fetch():
            # Phase 1: Fetch events for all leagues in parallel batches
            all_events = {}
            BATCH = 20

            league_items = list(TOURNAMENT_MAP.items())
            for batch_start in range(0, len(league_items), BATCH):
                batch = league_items[batch_start:batch_start + BATCH]
                requests = []
                id_to_league = {}
                for betid, (slug, tid) in batch:
                    rid = self._next_id()
                    league_name = slug.replace("-", " ").title()
                    id_to_league[str(rid)] = league_name
                    requests.append((rid, "GetRichEventsByTournamentIdAndStage",
                                     [tid, 1, CONTEXT]))

                results = await self._ws_fire_and_collect(requests, idle_timeout=4)
                for rid, data in results.items():
                    evs = _parse_events(data, id_to_league[rid])
                    all_events.update(evs)

            if not all_events:
                return []

            # Phase 2: Fetch markets for all events in sequential batches
            event_ids = list(all_events.keys())
            all_odds = await self._get_full_markets(event_ids)

            # Build results
            results = []
            for ev_id, ev in all_events.items():
                match_dict = {
                    "match": ev["match"],
                    "league": ev["league"],
                    "time": ev["timestamp"],
                    "league_id": 0,
                    "match_id": int(ev_id) if ev_id.isdigit() else 0,
                }
                od = all_odds.get(ev_id, {})
                match_dict.update(od)
                results.append(match_dict)

            self.data = results
            return results

        return self._run(_fetch())

    def get_team(self, team: str) -> List[Dict[str, Any]]:
        """Fetch odds for matches involving a specific team."""
        all_matches = self.get_all()

        def filter_func(data):
            match: str = data["match"]
            return match.lower().find(team.lower()) != -1

        return list(filter(filter_func, all_matches))
