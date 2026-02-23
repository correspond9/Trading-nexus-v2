"""
app/margin/mcx_margin_data.py
=============================
Downloads and parses MCX (Multi-Commodity Exchange) SPAN margin data daily.

MCX Files downloaded:
  - Daily SPAN Risk Parameter Files from: 
    https://www.mcxindia.com/education-training/daily-span-risk-parameter-file
  - File pattern: mcxrpf-{YYYYMMDD}-{HHMM}-{SEQUENCE}-i.zip
  - Multiple files per day: Begin Day (05:06 IST) + Intra-day updates (09:30, 11:00, 12:00)
  - We use the Begin Day file (first one after midnight)

MCX file format: ZIP containing SPAN Risk Parameter Files
  - Public download, no authentication required
  - Contains margin data for all commodity contracts
  - Updated daily and intra-day
  
Margin Formula (same as NSE):
  span_margin     = price_scan ├ù quantity / cvf    [for commodity multipliers]
  exposure_margin = ref_price ├ù quantity ├ù elm_pct / 100
  ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
  Total (seller/futures) = span_margin + exposure_margin
"""

import asyncio
import csv
import io
import logging
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta, date as date_type
from typing import Optional

import httpx

log = logging.getLogger(__name__)

# Import database pool for persistence
try:
    from app.database import get_pool
except ImportError:
    get_pool = None
    log.warning("Database not available for MCX margin persistence")

# Import exchange holidays
try:
    from app.margin.exchange_holidays import is_trading_day, get_next_trading_day
except ImportError:
    is_trading_day = None
    get_next_trading_day = None
    log.warning("Exchange holidays module not available")

IST = timezone(timedelta(hours=5, minutes=30))

# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
# MCX Archive URL Templates
# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

# MCX SPAN Risk Parameter Files (public download, no auth required)
# Base URL for daily files
_MCX_RPF_BASE = "https://www.mcxindia.com/docs/default-source/market-operations/daily-span-risk-parameter-file"

# File pattern: {YYYY}/{month_name}/mcxrpf-{YYYYMMDD}-{HHMM}-{SEQUENCE}-i.zip
# Example: 2026/february/mcxrpf-20260220-0506-01-i.zip (Begin Day file at 05:06 IST)
# We prefer the Begin Day file (SEQUENCE=01, downloaded around 05:06 IST) which is the primary SPAN file

# Intra-day files available at:
# - 09:30 IST (SEQUENCE=02)
# - 11:00 IST (SEQUENCE=03)  
# - 12:00 IST (SEQUENCE=04)
# For this system, we only download Begin Day file to match NSE's 08:45 download strategy

# Contract value factors for major MCX commodities
_MCX_CVF = {
    "GOLD": 100,        # grams
    "GOLDM": 100,
    "GOLDGUINEA": 1,
    "GOLDPETAL": 1,
    "GOLDTEN": 1,
    "SILVER": 30000,    # grams
    "SILVERM": 30000,
    "SILVERMIC": 30000,
    "CRUDEOIL": 100,    # barrels
    "CRUDEOILM": 100,
    "NATURALGAS": 10,   # MMBtu
    "NATGASMINI": 10,
    "COPPER": 250,      # kg
    "COPPERM": 250,
    "ZINC": 250,
    "ZINCM": 250,
    "NICKEL": 100,      # kg
    "NICKELM": 100,
    "LEAD": 1000,       # kg
    "LEADM": 1000,
    "PEPPER": 1000,     # kg
    "RUBBER": 100,      # kg
    "MENTHOL": 100,     # kg
    "TURMERIC": 1000,   # kg
    "COTTONM": 100,     # bales
    "COTTON": 100,
    "COREGULD": 100,    # grams (core commodity)
}


@dataclass
class MCXMarginEntry:
    """Single MCX commodity SPAN margin data."""
    symbol: str
    ref_price: float
    price_scan: float
    cvf: float
    elm_pct: float


# In-memory cache of MCX margins
class _MCXStore:
    def __init__(self):
        self.margins: dict[str, MCXMarginEntry] = {}
        self.last_download: Optional[date_type] = None
        self.fallback_used: bool = False


_mcx_store = _MCXStore()


async def download_and_refresh(
    target_date: Optional[date_type] = None,
) -> dict:
    """
    Download MCX SPAN margin data for the given date.
    
    Strategy:
      1. If target_date is a holiday: try NEXT trading day first (future data)
      2. Then try: target_date, yesterday, 2 days back, 3 days back
      3. Fallback to database cache perpetually (previous day's data)
    
    Args:
        target_date: Date to download (defaults to today IST)
    
    Returns:
        dict with status, symbol_count, elm_pct, download_date
    """
    if target_date is None:
        target_date = datetime.now(tz=IST).date()
    
    log.info(f"MCX margin download starting for {target_date}")
    
    # Check if today is a holiday; if so, prefer next trading day
    if is_trading_day and get_next_trading_day:
        is_trading = await is_trading_day("MCX", target_date)
        if not is_trading:
            log.info(f"{target_date} is MCX holiday; attempting next trading day")
            next_trading = await get_next_trading_day("MCX", target_date)
            if next_trading:
                log.info(f"Trying next trading day: {next_trading}")
                target_date = next_trading
    
    # Attempt download with fallback chain
    download_strategy = [
        target_date,
        target_date - timedelta(days=1),
        target_date - timedelta(days=2),
        target_date - timedelta(days=3),
    ]
    
    for attempt_date in download_strategy:
        status = await _attempt_download(attempt_date)
        
        if status['success']:
            log.info(f"MCX margin download successful for {attempt_date}: {status['symbol_count']} symbols")
            await _log_download_attempt("MCX", attempt_date, "success", status)
            return status
        else:
            log.debug(f"MCX margin download failed for {attempt_date}")
    
    # All downloads failed; try database cache
    log.warning("All MCX margin downloads failed; falling back to database cache")
    loaded = await _load_latest_from_db()
    
    if loaded:
        log.info(f"Loaded {len(_mcx_store.margins)} MCX margins from database cache")
        await _log_download_attempt("MCX", target_date, "cached", {
            'symbol_count': len(_mcx_store.margins),
            'source': 'database_cache',
        })
        _mcx_store.fallback_used = True
        return {
            'success': True,
            'symbol_count': len(_mcx_store.margins),
            'source': 'database_cache',
            'download_date': _mcx_store.last_download,
        }
    
    # Complete failure: no fresh downloads AND no database cache
    # This only happens on first startup before any data downloaded
    log.error("MCX margin data completely unavailable: no downloads and no cache")
    log.error("MCX margin calculations will fail until data is downloaded")
    await _log_download_attempt("MCX", target_date, "failed", {
        'error': 'MCX margins unavailable - waiting for first successful download',
    })
    _mcx_store.fallback_used = False
    return {
        'success': False,
        'symbol_count': 0,
        'source': None,
        'download_date': None,
        'error': 'No MCX margin data available',
    }


async def _attempt_download(attempt_date: date_type) -> dict:
    """
    Attempt to download MCX SPAN Risk Parameter File for a specific date.
    
    MCX files are hosted at:
    https://www.mcxindia.com/docs/default-source/market-operations/daily-span-risk-parameter-file/{YYYY}/{month}/mcxrpf-{YYYYMMDD}-{HHMM}-{SEQUENCE}-i.zip
    
    We download the Begin Day file (SEQUENCE=01, released around 05:06 IST).
    Files are updated daily and several times intra-day (09:30, 11:00, 12:00 IST).
    
    Returns dict with 'success' bool and optional 'symbol_count', 'file_size', 'error'
    """
    try:
        # Build month name for URL (e.g., "february" for Feb)
        month_names = [
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december"
        ]
        month_name = month_names[attempt_date.month - 1]
        
        # MCX Begin Day file is typically YYYYMMDD-0506-01 (05:06 IST, sequence 01)
        date_str = attempt_date.strftime("%Y%m%d")
        year = attempt_date.strftime("%Y")
        
        # Try the Begin Day file URL (05:06 IST release, sequence 01)
        url = f"{_MCX_RPF_BASE}/{year}/{month_name}/mcxrpf-{date_str}-0506-01-i.zip"
        
        log.info(f"Downloading MCX SPAN file: {url}")
        
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            resp = await client.get(url)
            
            if resp.status_code == 404:
                # Try alternate times if 05:06 not available yet
                log.debug(f"Begin Day file (05:06) not found; trying intra-day files...")
                
                # Try 09:30 IST (sequence 02)
                url = f"{_MCX_RPF_BASE}/{year}/{month_name}/mcxrpf-{date_str}-0930-02-i.zip"
                log.debug(f"Trying: {url}")
                resp = await client.get(url)
                
                if resp.status_code == 404:
                    # Try 11:00 IST (sequence 03)
                    url = f"{_MCX_RPF_BASE}/{year}/{month_name}/mcxrpf-{date_str}-1100-03-i.zip"
                    log.debug(f"Trying: {url}")
                    resp = await client.get(url)
                
                if resp.status_code == 404:
                    # Try 12:00 IST (sequence 04)
                    url = f"{_MCX_RPF_BASE}/{year}/{month_name}/mcxrpf-{date_str}-1200-04-i.zip"
                    log.debug(f"Trying: {url}")
                    resp = await client.get(url)
            
            if resp.status_code != 200:
                log.warning(f"MCX SPAN file not available for {attempt_date}: HTTP {resp.status_code}")
                return {'success': False, 'error': f'HTTP {resp.status_code}', 'url': url}
            
            # Successfully downloaded ZIP file
            log.info(f"MCX SPAN file downloaded: {len(resp.content):,} bytes")
            
            # TODO: Parse ZIP contents and extract SPAN data
            # MCX files contain Risk Parameter data that needs to be parsed
            # Format to be confirmed from actual file structure
            # Expected: commodity symbols, reference prices, scan ranges, CVF values
            
            return {
                'success': True,
                'symbol_count': 0,  # TODO: Update after parsing implementation
                'file_size': len(resp.content),
                'url': url,
            }
    
    except Exception as exc:
        log.warning(f"MCX SPAN download attempt failed for {attempt_date}: {exc}")
        return {'success': False, 'error': str(exc)}


async def _load_latest_from_db() -> bool:
    """
    Load the most recent MCX SPAN data from database into memory cache.
    
    Returns True if data was loaded successfully.
    """
    if not get_pool:
        log.warning("Database not available; cannot load cached MCX margins")
        return False
    
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT symbol, ref_price, price_scan, contract_value_factor, elm_pct, downloaded_at
                FROM mcx_span_margin_cache
                WHERE is_latest = true
                ORDER BY symbol
                """
            )
            
            if not rows:
                log.info("No cached MCX margins found in database")
                return False
            
            _mcx_store.margins.clear()
            for row in rows:
                _mcx_store.margins[row['symbol']] = MCXMarginEntry(
                    symbol=row['symbol'],
                    ref_price=float(row['ref_price']),
                    price_scan=float(row['price_scan']),
                    cvf=float(row['contract_value_factor']),
                    elm_pct=float(row['elm_pct']),
                )
            
            if rows:
                _mcx_store.last_download = rows[0]['downloaded_at']
            
            log.info(f"Loaded {len(_mcx_store.margins)} MCX margins from database")
            return True
    
    except Exception as exc:
        log.error(f"Failed to load MCX margins from database: {exc}")
        return False


async def _save_to_db(
    margins: dict[str, MCXMarginEntry],
    download_date: date_type,
) -> None:
    """Save MCX margins to database for persistence."""
    if not get_pool:
        log.warning("Database not available; skipping MCX margin persistence")
        return
    
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            rows = [
                (
                    entry.symbol,
                    entry.ref_price,
                    entry.price_scan,
                    entry.cvf,
                    entry.elm_pct,
                    download_date,
                )
                for entry in margins.values()
            ]
            
            if rows:
                await conn.executemany(
                    """
                    INSERT INTO mcx_span_margin_cache 
                        (symbol, ref_price, price_scan, contract_value_factor, elm_pct, downloaded_at, is_latest)
                    VALUES ($1, $2, $3, $4, $5, $6, true)
                    """,
                    rows,
                )
                
                # Mark old entries as non-latest
                await conn.execute(
                    "UPDATE mcx_span_margin_cache SET is_latest = false WHERE downloaded_at < $1",
                    download_date,
                )
                
                log.info(f"Saved {len(rows)} MCX margins to database for {download_date}")
    
    except Exception as exc:
        log.error(f"Failed to save MCX margins to database: {exc}")


async def _log_download_attempt(
    exchange: str,
    download_date: date_type,
    status: str,
    details: dict,
) -> None:
    """Log MCX margin download attempt to database."""
    if not get_pool:
        return
    
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO margin_download_logs 
                    (exchange, download_date, status, symbol_count, error_message, file_sources)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (exchange, download_date) DO UPDATE
                SET status = EXCLUDED.status, symbol_count = EXCLUDED.symbol_count
                """,
                "MCX",
                download_date,
                status,
                details.get('symbol_count'),
                details.get('error'),
                details,
            )
    except Exception as exc:
        log.debug(f"Failed to log MCX download: {exc}")


async def get_margin(
    symbol: str,
    quantity: int,
    is_sell: bool = False,
) -> dict:
    """
    Calculate MCX margin requirement for a commodity position.
    
    Args:
        symbol: MCX commodity symbol (e.g., 'GOLD', 'SILVER')
        quantity: Number of contracts (lots)
        is_sell: True for seller (futures/forwards), False for buyer (options premium)
    
    Returns:
        dict with 'span_margin', 'elm_margin', 'total_margin' in INR
    """
    if symbol not in _mcx_store.margins:
        # ERROR: Symbol not in cache - cannot calculate margin without proper data
        log.error(f"MCX symbol {symbol} not found in margins cache; cannot provide margin calculation")
        return {
            'symbol': symbol,
            'span_margin': None,
            'elm_margin': None,
            'total_margin': None,
            'error': f'Symbol {symbol} not found in MCX margins cache',
        }
    
    entry = _mcx_store.margins[symbol]
    cvf = _MCX_CVF.get(symbol, entry.cvf)
    
    # SPAN margin = price_scan ├ù quantity / cvf
    span_margin = entry.price_scan * quantity / cvf if cvf > 0 else 0
    
    # ELM margin = ref_price ├ù quantity ├ù elm_pct / 100 / cvf
    elm_margin = (entry.ref_price * quantity * entry.elm_pct / 100) / cvf if cvf > 0 else 0
    
    total_margin = span_margin + elm_margin if is_sell else 0
    
    return {
        'symbol': symbol,
        'ref_price': entry.ref_price,
        'price_scan': entry.price_scan,
        'cvf': cvf,
        'elm_pct': entry.elm_pct,
        'span_margin': round(span_margin, 2),
        'elm_margin': round(elm_margin, 2),
        'total_margin': round(total_margin, 2),
        'quantity': quantity,
        'is_sell': is_sell,
    }


def get_all_margins() -> dict[str, MCXMarginEntry]:
    """Return all cached MCX margins."""
    return _mcx_store.margins.copy()


def is_fallback_active() -> bool:
    """Check if fallback 3% ELM is currently in use."""
    return _mcx_store.fallback_used
