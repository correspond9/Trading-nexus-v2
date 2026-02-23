"""
app/instruments/atm_calculator.py
===================================
ATM strike calculation — deterministic and rule-driven.
Recalculated ONLY at: system startup, expiry rollover, explicit admin refresh.
NEVER on every tick.
"""
import logging
from decimal import Decimal, ROUND_HALF_UP

log = logging.getLogger(__name__)

# Cache: underlying → current ATM strike
_atm_cache: dict[str, Decimal] = {}


def calculate_atm(underlying_ltp: float, strike_step: float) -> Decimal:
    """
    ATM = nearest strike to current underlying LTP.
    Rounded using exchange-defined strike intervals.

    Example:
        ltp=22347.5, step=50 → ATM=22350
    """
    step = Decimal(str(strike_step))
    ltp  = Decimal(str(underlying_ltp))
    atm  = (ltp / step).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * step
    return atm


def update_atm(underlying: str, ltp: float, strike_step: float) -> Decimal:
    """
    Compute and cache ATM for an underlying.
    Call only at startup / expiry rollover / explicit admin refresh.
    Returns the new ATM strike.
    """
    atm = calculate_atm(ltp, strike_step)
    prev = _atm_cache.get(underlying)
    _atm_cache[underlying] = atm

    if prev != atm:
        log.info(
            f"ATM updated — {underlying}: {prev} → {atm}  "
            f"(LTP={ltp}, step={strike_step})"
        )
    return atm


def get_atm(underlying: str) -> Decimal | None:
    """Return cached ATM for an underlying, or None if not yet set."""
    return _atm_cache.get(underlying)


def generate_strike_range(
    atm: Decimal,
    strike_step: float,
    num_strikes_each_side: int,
) -> list[Decimal]:
    """
    Generate the full strike list centred on ATM.
    num_strikes_each_side = 50 → 101 total (ATM ± 50)
    num_strikes_each_side = 25 → 51 total
    """
    step   = Decimal(str(strike_step))
    n      = num_strikes_each_side
    return [atm + step * Decimal(i) for i in range(-n, n + 1)]
