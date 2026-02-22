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

  const wsRef    = useRef(null);
  const timerRef = useRef(null);
  const mountedRef = useRef(true);

  // ── REST fetch ──────────────────────────────────────────────────────────
  const fetchData = useCallback(async (ul = underlying, exp = expiry) => {
    if (!ul || !exp) return;
    setLoading(true);
    setError(null);
    try {
      const result = await apiService.get('/options/live', { underlying: ul, expiry: exp });
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

  // ── Helpers ───────────────────────────────────────────────────────────────
  const getATMStrike = useCallback((ltp) => {
    const interval = Number(data?.strike_interval || getStrikeInterval(underlying) || 0);
    const price = Number(ltp || data?.underlying_ltp || 0);
    if (!interval || !price) return data?.atm_strike ?? data?.atm ?? null;
    return Math.round(price / interval) * interval;
  }, [data, underlying]);

  const lotSize = getLotSize(underlying);

  const refresh = useCallback(() => fetchData(), [fetchData]);

  return { data, loading, error, refresh, getATMStrike, getLotSize: () => lotSize, servedExpiry };
}

export default useAuthoritativeOptionChain;
