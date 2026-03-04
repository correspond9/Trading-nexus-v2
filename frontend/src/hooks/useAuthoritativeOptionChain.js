import { useState, useEffect, useRef, useCallback } from 'react';
import { apiService } from '../services/apiService';
import { getLotSize, getStrikeInterval } from '../config/tradingConfig';

const DEFAULT_POLL_INTERVAL = 5000; // ms between REST polls when WS not available

/**
 * useAuthoritativeOptionChain
 * Fetches option chain data via REST and streams via WebSocket.
 * Returns { data, loading, error, refresh, getATMStrike, getLotSize, servedExpiry }
 */
export function useAuthoritativeOptionChain(
  underlying,
  expiry,
  {
    autoRefresh = true,
    refreshInterval = 1000,
    pollInterval = DEFAULT_POLL_INTERVAL,
  } = {}
) {
  const [data, setData]           = useState(null);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState(null);
  const [servedExpiry, setServedExpiry] = useState(expiry);

  const wsRef          = useRef(null);
  const timerRef       = useRef(null);
  const mountedRef     = useRef(true);

  // ── ATM drift detection ──────────────────────────────────────────────────
  // Tracks the ATM at the time of the last full calibration (re-fetch).
  // When the live ATM drifts ≥ ATM_DRIFT_THRESHOLD strikes away from that
  // baseline, a fresh REST fetch is triggered so the backend can return a
  // correctly-centred strike window.
  const ATM_DRIFT_THRESHOLD = 7;   // strikes before re-centering
  const baseAtmRef      = useRef(null);  // ATM at last calibration
  const driftFetchingRef = useRef(false); // prevent concurrent drift re-fetches

  // ── REST fetch ──────────────────────────────────────────────────────────
  const fetchData = useCallback(async (ul = underlying, exp = expiry) => {
    if (!ul || !exp) return;
    setLoading(true);
    setError(null);
    try {
      // Request strikes_around=50 to get the full available range from the backend.
      // The frontend already slices to ATM±15 for display, so having 101 strikes ensures
      // the true ATM (derived from live option premiums) is always inside the dataset,
      // even when the backend's cached ATM or the index LTP is stale.
      const result = await apiService.get('/options/live', { underlying: ul, expiry: exp, strikes_around: 50 });
      if (!mountedRef.current) return;
      // Backend returns an object: { underlying, expiry, underlying_ltp, lot_size, strike_interval, atm, strikes }
      if (result && typeof result === 'object' && !Array.isArray(result)) {
        const normalized = {
          ...result,
          // keep older UI fields working
          atm_strike: result.atm_strike ?? result.atm ?? null,
        };
        setData(normalized);
      } else {
        // Legacy fallback (shouldn't happen): treat as empty.
        setData(null);
      }
      setServedExpiry(exp);
    } catch (e) {
      if (mountedRef.current) setError(e.message || 'Failed to load option chain');
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, [underlying, expiry]);

  // ── WebSocket stream ─────────────────────────────────────────────────────
  const connectWS = useCallback(() => {
    if (!underlying || !expiry) return;
    try {
      const base = apiService.baseURL;
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      const wsBase = base.startsWith('/')
        ? `${protocol}//${host}${base}`
        : base.replace(/^https?:/, protocol);
      const url = `${wsBase}/options/ws/live?underlying=${underlying}&expiry=${expiry}`;

      if (wsRef.current) wsRef.current.close();
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onmessage = (evt) => {
        if (!mountedRef.current) return;
        try {
          const msg = JSON.parse(evt.data);
          // Backend WS sends: { type: 'option_chain', strikes: { ... } }
          if (msg && typeof msg === 'object' && msg.strikes) {
            setData((prev) => ({
              ...(prev && typeof prev === 'object' ? prev : {}),
              strikes: msg.strikes,
              atm_strike: (prev && prev.atm_strike) || (prev && prev.atm) || null,
            }));
          } else if (msg && typeof msg === 'object' && msg.prices) {
            // ignore unrelated messages
          }
        } catch { /* ignore parse errors */ }
      };

      ws.onclose = () => {
        // Fall back to polling
        if (mountedRef.current && timerRef.current === null && autoRefresh) {
          timerRef.current = setInterval(() => fetchData(), pollInterval);
        }
      };
    } catch (e) {
      console.warn('[useAuthoritativeOptionChain] WS error:', e);
      if (autoRefresh) timerRef.current = setInterval(() => fetchData(), pollInterval);
    }
  }, [underlying, expiry, fetchData, autoRefresh, pollInterval]);

  useEffect(() => {
    mountedRef.current = true;
    if (underlying && expiry) {
      fetchData();
      connectWS();
      if (autoRefresh) {
        clearInterval(timerRef.current);
        timerRef.current = setInterval(() => fetchData(), Math.max(250, Number(refreshInterval) || 1000));
      }
    }
    return () => {
      mountedRef.current = false;
      clearInterval(timerRef.current);
      timerRef.current = null;
      if (wsRef.current) wsRef.current.close();
    };
  }, [underlying, expiry, fetchData, connectWS, autoRefresh, refreshInterval]);

  // ── ATM drift detection effects ───────────────────────────────────────────

  // Reset baseline whenever the user switches index or expiry so the new
  // instrument starts fresh (first data load sets a new baseline).
  useEffect(() => {
    baseAtmRef.current     = null;
    driftFetchingRef.current = false;
  }, [underlying, expiry]);

  // After every REST update, check whether the min-premium ATM (derived from live
  // option prices — reliable even when the index LTP in the DB is stale) has drifted
  // far from the midpoint of the returned strike range. If so, a re-fetch is triggered.
  // NOTE: We no longer rely on data.underlying_ltp because that field is sourced from
  // the market_data table for the index token, which may not receive live ticks and
  // can stay at yesterday's close all day.
  useEffect(() => {
    if (!data?.strikes || Object.keys(data.strikes).length === 0) return;

    const interval = Number(data.strike_interval || getStrikeInterval(underlying) || 0);
    if (!interval) return;

    // Derive the true ATM from live option premiums (min straddle) — this is always reliable.
    let minPremiumStrike = null;
    let minPremium      = null;
    Object.entries(data.strikes).forEach(([k, v]) => {
      const strike = parseFloat(k);
      const ce = v?.CE?.ltp || 0;
      const pe = v?.PE?.ltp || 0;
      if (ce <= 0 && pe <= 0) return;
      const sum = ce + pe;
      if (minPremium === null || sum < minPremium) { minPremium = sum; minPremiumStrike = strike; }
    });
    if (minPremiumStrike === null) return;

    const allStrikes   = Object.keys(data.strikes).map(Number).sort((a, b) => a - b);
    const midStrike    = allStrikes[Math.floor(allStrikes.length / 2)];
    const driftInStrikes = Math.abs(minPremiumStrike - midStrike) / interval;

    if (baseAtmRef.current === null) {
      // First data load — record where we are, no re-fetch needed.
      baseAtmRef.current = minPremiumStrike;
      if (driftInStrikes > 0) {
        console.log(
          `[OptionChain] Initial load: min-premium ATM ${minPremiumStrike} is ${driftInStrikes} strikes ` +
          `from centre of returned range (mid=${midStrike}). Data range covers it.`
        );
      }
      return;
    }

    // Re-fetch if the premium-derived ATM is more than threshold strikes from the
    // midpoint of what the backend returned.
    if (driftInStrikes >= ATM_DRIFT_THRESHOLD && !driftFetchingRef.current) {
      driftFetchingRef.current = true;
      console.log(
        `[OptionChain] Premium-ATM drift ≥ ${ATM_DRIFT_THRESHOLD} strikes for ${underlying}: ` +
        `ATM=${minPremiumStrike}, range-mid=${midStrike}, drift=${driftInStrikes} strikes. Re-fetching.`
      );
      baseAtmRef.current = minPremiumStrike;
      fetchData().finally(() => {
        if (mountedRef.current) driftFetchingRef.current = false;
      });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data?.strikes]);

  // ── Helpers ───────────────────────────────────────────────────────────────
  const getATMStrike = useCallback((ltp) => {
    const interval = Number(data?.strike_interval || getStrikeInterval(underlying) || 0);
    const price = Number(ltp || data?.underlying_ltp || 0);
    if (!interval || !price) return data?.atm_strike ?? data?.atm ?? null;
    return Math.round(price / interval) * interval;
  }, [data, underlying]);

  const lotSize = getLotSize(underlying);

  const refresh = useCallback(() => fetchData(), [fetchData]);

  /**
   * recalibrate — manually resets the ATM drift baseline to null so that the
   * very next data response re-establishes it from the current live LTP.
   * Use this when you want to force a fresh ATM-centred window on demand.
   */
  const recalibrate = useCallback(() => {
    baseAtmRef.current      = null;
    driftFetchingRef.current = false;
    console.log(`[OptionChain] Manual recalibration triggered for ${underlying}`);
    fetchData();
  }, [fetchData, underlying]);

  return { data, loading, error, refresh, recalibrate, getATMStrike, getLotSize: () => lotSize, servedExpiry };
}

export default useAuthoritativeOptionChain;
