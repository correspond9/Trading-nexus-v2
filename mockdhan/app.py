import asyncio
import json
import math
import struct
import time
from dataclasses import dataclass
from datetime import datetime, timedelta

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="Mock Dhan Engine", version="1.0.0")


@dataclass(frozen=True)
class UnderlyingDef:
    name: str
    security_id: int
    base: float
    strike_step: int


UNDERLYINGS = {
    13: UnderlyingDef(name="NIFTY", security_id=13, base=22350.0, strike_step=50),
    25: UnderlyingDef(name="BANKNIFTY", security_id=25, base=48600.0, strike_step=100),
    51: UnderlyingDef(name="SENSEX", security_id=51, base=73500.0, strike_step=100),
}

EXCHANGE_SEGMENT_BYTE = 1


def _now_epoch() -> int:
    return int(time.time())


def _spot_price(defn: UnderlyingDef) -> float:
    t = time.time()
    wave_1 = math.sin(t / 6.0) * (defn.strike_step * 2.5)
    wave_2 = math.sin(t / 17.0) * (defn.strike_step * 1.2)
    return round(defn.base + wave_1 + wave_2, 2)


def _encode_option_token(underlying_security_id: int, strike: int, is_ce: bool) -> int:
    # Deterministic token format for mock options.
    # Example: 13 22350 CE -> 13223501
    return int(f"{underlying_security_id}{strike:05d}{1 if is_ce else 2}")


def _decode_option_token(token: int) -> tuple[int, int, bool] | None:
    token_s = str(token)
    if len(token_s) < 7:
        return None
    try:
        underlying_sid = int(token_s[:2])
        strike = int(token_s[2:-1])
        side = token_s[-1]
    except ValueError:
        return None
    if underlying_sid not in UNDERLYINGS:
        return None
    if side not in ("1", "2"):
        return None
    return underlying_sid, strike, side == "1"


def _option_ltp(spot: float, strike: float, is_ce: bool) -> float:
    intrinsic = max(spot - strike, 0.0) if is_ce else max(strike - spot, 0.0)
    time_value = max(8.0, 120.0 - abs(spot - strike) * 0.25)
    noise = math.sin(time.time() / 3.5) * 1.8
    return round(max(0.5, intrinsic + time_value + noise), 2)


def _build_optionchain(underlying: UnderlyingDef, expiry: str) -> dict:
    spot = _spot_price(underlying)
    atm = round(spot / underlying.strike_step) * underlying.strike_step
    start = atm - (underlying.strike_step * 20)
    end = atm + (underlying.strike_step * 20)

    oc: dict[str, dict] = {}
    for strike in range(int(start), int(end) + underlying.strike_step, underlying.strike_step):
        ce_ltp = _option_ltp(spot, strike, True)
        pe_ltp = _option_ltp(spot, strike, False)
        ce_token = _encode_option_token(underlying.security_id, strike, True)
        pe_token = _encode_option_token(underlying.security_id, strike, False)
        common = {
            "implied_volatility": round(12.5 + abs(spot - strike) / max(underlying.strike_step, 1) * 0.15, 4),
            "previous_oi": int(5000 + abs(strike - atm) * 8),
        }
        oc[str(strike)] = {
            "ce": {
                "security_id": ce_token,
                "last_price": ce_ltp,
                "previous_close_price": round(ce_ltp * 0.98, 2),
                "greeks": {
                    "delta": round(max(0.01, min(0.99, 0.5 + (spot - strike) / 1500.0)), 4),
                    "theta": round(-0.05 - abs(spot - strike) / 100000.0, 4),
                    "gamma": 0.0008,
                    "vega": 0.12,
                },
                **common,
            },
            "pe": {
                "security_id": pe_token,
                "last_price": pe_ltp,
                "previous_close_price": round(pe_ltp * 0.98, 2),
                "greeks": {
                    "delta": round(max(-0.99, min(-0.01, -0.5 + (spot - strike) / 1500.0)), 4),
                    "theta": round(-0.05 - abs(spot - strike) / 100000.0, 4),
                    "gamma": 0.0008,
                    "vega": 0.12,
                },
                **common,
            },
        }

    return {
        "underlying": underlying.name,
        "expiry": expiry,
        "last_price": spot,
        "oc": oc,
    }


def _packet_for_token(token: int) -> bytes:
    ltp, close = _price_for_token(token)

    open_p = round(close * 1.001, 2)
    high_p = round(max(ltp, open_p) * 1.002, 2)
    low_p = round(min(ltp, open_p) * 0.998, 2)

    data = bytearray(162)
    struct.pack_into("<B", data, 0, 8)               # response code: FULL
    struct.pack_into("<H", data, 1, 162)             # message length
    struct.pack_into("<B", data, 3, EXCHANGE_SEGMENT_BYTE)
    struct.pack_into("<I", data, 4, token)

    struct.pack_into("<f", data, 8, float(ltp))
    struct.pack_into("<H", data, 12, 1)              # ltq
    struct.pack_into("<I", data, 14, 0)              # ltt epoch (0 => parser stores None)
    struct.pack_into("<f", data, 18, float(ltp))     # atp
    struct.pack_into("<I", data, 22, 10000)          # volume
    struct.pack_into("<I", data, 26, 5000)           # sellq
    struct.pack_into("<I", data, 30, 5000)           # buyq
    struct.pack_into("<I", data, 34, 20000)          # oi
    struct.pack_into("<I", data, 38, 25000)          # oi_high
    struct.pack_into("<I", data, 42, 15000)          # oi_low
    struct.pack_into("<f", data, 46, float(open_p))
    struct.pack_into("<f", data, 50, float(close))
    struct.pack_into("<f", data, 54, float(high_p))
    struct.pack_into("<f", data, 58, float(low_p))

    for i in range(5):
        off = 62 + (i * 20)
        bid_qty = 150 + i * 10
        ask_qty = 180 + i * 10
        bid_px = round(ltp - (i + 1) * 0.05, 2)
        ask_px = round(ltp + (i + 1) * 0.05, 2)
        struct.pack_into("<I", data, off, bid_qty)
        struct.pack_into("<I", data, off + 4, ask_qty)
        struct.pack_into("<H", data, off + 8, 1)
        struct.pack_into("<H", data, off + 10, 1)
        struct.pack_into("<f", data, off + 12, float(bid_px))
        struct.pack_into("<f", data, off + 16, float(ask_px))

    return bytes(data)


def _price_for_token(token: int) -> tuple[float, float]:
    decode = _decode_option_token(token)
    if decode:
        underlying_sid, strike, is_ce = decode
        spot = _spot_price(UNDERLYINGS[underlying_sid])
        ltp = _option_ltp(spot, strike, is_ce)
        close = round(ltp * 0.98, 2)
    elif token in UNDERLYINGS:
        spot = _spot_price(UNDERLYINGS[token])
        ltp = round(spot, 2)
        close = round(ltp * 0.995, 2)
    else:
        # Generic token behavior for any unknown subscriptions.
        base = 100.0 + (token % 1000)
        ltp = round(base + math.sin(time.time() / 5.0) * 1.5, 2)
        close = round(base, 2)

    return ltp, close


def _extract_tokens_from_payload(payload: dict) -> list[int]:
    """Accept multiple request shapes to mirror Dhan and internal callers."""
    out: set[int] = set()

    def _add(v) -> None:
        try:
            out.add(int(str(v)))
        except Exception:
            return

    if not isinstance(payload, dict):
        return []

    for k in ("SecurityId", "security_id", "token", "instrument_token"):
        if k in payload:
            _add(payload.get(k))

    for k in ("tokens", "instrument_tokens", "security_ids"):
        vals = payload.get(k)
        if isinstance(vals, list):
            for v in vals:
                _add(v)

    for seg in ("NSE_EQ", "NSE_FNO", "BSE_EQ", "BSE_FNO", "MCX_FO", "NSE_COM"):
        vals = payload.get(seg)
        if isinstance(vals, list):
            for v in vals:
                _add(v)

    if not out and isinstance(payload.get("InstrumentList"), list):
        for item in payload.get("InstrumentList") or []:
            if isinstance(item, dict):
                for key in ("SecurityId", "security_id", "token"):
                    if key in item:
                        _add(item.get(key))

    return list(out)


def _build_quote_response(tokens: list[int]) -> dict:
    quotes = []
    for token in tokens:
        ltp, close = _price_for_token(token)
        quotes.append(
            {
                "securityId": str(token),
                "lastTradedPrice": float(ltp),
                "lastPrice": float(ltp),
                "ltp": float(ltp),
                "close": float(close),
            }
        )

    return {
        "status": "success",
        "data": {
            "quotes": quotes,
        },
    }


def _depth_packet(token: int, response_code: int, ltp: float, sequence: int) -> bytes:
    # Header: int16 len, byte code, byte exch, int32 security_id, uint32 sequence
    data = bytearray(12 + 20 * 16)
    struct.pack_into("<H", data, 0, len(data))
    struct.pack_into("<B", data, 2, response_code)
    struct.pack_into("<B", data, 3, EXCHANGE_SEGMENT_BYTE)
    struct.pack_into("<i", data, 4, token)
    struct.pack_into("<I", data, 8, sequence)

    for i in range(20):
        off = 12 + i * 16
        px = ltp - (i + 1) * 0.1 if response_code == 41 else ltp + (i + 1) * 0.1
        qty = 200 + i * 15
        orders = 1 + (i % 4)
        struct.pack_into("<d", data, off, float(round(px, 2)))
        struct.pack_into("<I", data, off + 8, qty)
        struct.pack_into("<I", data, off + 12, orders)

    return bytes(data)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "mockdhan"}


@app.get("/v2/profile")
async def profile() -> dict:
    return {
        "status": "success",
        "data": {
            "dhanClientId": "mock_client",
            "name": "Mock Dhan User",
        },
    }


@app.post("/v2/optionchain")
async def optionchain(payload: dict) -> dict:
    underlying_scrip = int(payload.get("UnderlyingScrip") or 13)
    expiry = payload.get("Expiry") or (datetime.utcnow().date() + timedelta(days=7)).isoformat()
    underlying = UNDERLYINGS.get(underlying_scrip, UNDERLYINGS[13])
    return {"status": "success", "data": _build_optionchain(underlying, str(expiry))}


@app.post("/v2/marketfeed/quote")
async def marketfeed_quote(payload: dict) -> dict:
    tokens = _extract_tokens_from_payload(payload)
    return _build_quote_response(tokens)


@app.post("/v2/marketfeed/ltp")
async def marketfeed_ltp(payload: dict) -> dict:
    tokens = _extract_tokens_from_payload(payload)
    return _build_quote_response(tokens)


@app.websocket("/")
async def live_feed(websocket: WebSocket) -> None:
    await websocket.accept()
    subscribed: set[int] = set()
    cursor = 0
    batch_size = 300

    try:
        while True:
            try:
                incoming = await asyncio.wait_for(websocket.receive_text(), timeout=0.5)
                payload = json.loads(incoming)
                request_code = int(payload.get("RequestCode") or 0)

                if request_code in (15, 17, 21):
                    for item in payload.get("InstrumentList", []):
                        sid = item.get("SecurityId")
                        if sid is not None:
                            subscribed.add(int(sid))
                elif request_code == 22:
                    for item in payload.get("InstrumentList", []):
                        sid = item.get("SecurityId")
                        if sid is not None:
                            subscribed.discard(int(sid))
                elif request_code == 12:
                    await websocket.close()
                    return
            except asyncio.TimeoutError:
                pass

            if not subscribed:
                continue

            token_list = list(subscribed)
            if cursor >= len(token_list):
                cursor = 0
            chunk = token_list[cursor: cursor + batch_size]
            if len(chunk) < batch_size and token_list:
                chunk += token_list[: max(0, batch_size - len(chunk))]
            cursor = (cursor + batch_size) % max(1, len(token_list))

            for token in chunk:
                await websocket.send_bytes(_packet_for_token(token))
    except (WebSocketDisconnect, RuntimeError):
        return


@app.websocket("/twentydepth")
async def depth_feed(websocket: WebSocket) -> None:
    await websocket.accept()
    subscribed: set[int] = set()
    sequence = 1

    try:
        while True:
            try:
                incoming = await asyncio.wait_for(websocket.receive_text(), timeout=0.8)
                payload = json.loads(incoming)
                request_code = int(payload.get("RequestCode") or 0)
                if request_code == 23:
                    for item in payload.get("InstrumentList", []):
                        sid = item.get("SecurityId")
                        if sid is not None:
                            subscribed.add(int(sid))
                elif request_code == 12:
                    await websocket.close()
                    return
            except asyncio.TimeoutError:
                pass

            if not subscribed:
                continue

            for token in list(subscribed):
                decode = _decode_option_token(token)
                if decode:
                    underlying_sid, strike, is_ce = decode
                    spot = _spot_price(UNDERLYINGS[underlying_sid])
                    ltp = _option_ltp(spot, strike, is_ce)
                elif token in UNDERLYINGS:
                    ltp = _spot_price(UNDERLYINGS[token])
                else:
                    ltp = 100.0 + (token % 500)
                await websocket.send_bytes(_depth_packet(token, 41, ltp, sequence))
                sequence += 1
                await websocket.send_bytes(_depth_packet(token, 51, ltp, sequence))
                sequence += 1
    except (WebSocketDisconnect, RuntimeError):
        return
