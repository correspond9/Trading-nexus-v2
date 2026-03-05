import React, { useState, useEffect, useCallback, useRef } from "react";
import { apiService } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';
import { useMarketPulse } from '../hooks/useMarketPulse';
import { useWebSocket } from '../hooks/useWebSocket';
import { RefreshCw, X, Plus, Search, ChevronDown } from "lucide-react";
import { formatOptionLabel } from '../utils/formatInstrumentLabel';

// ─── helpers ───────────────────────────────────────────────────────────────────
const WATCHLIST_STORAGE_KEY_PREFIX = "watchlists:";
const DEFAULT_TABS = [
  { id: 1, name: "Watchlist 1", instruments: [] },
  { id: 2, name: "Watchlist 2", instruments: [] },
  { id: 3, name: "Watchlist 3", instruments: [] },
];

const loadFromStorage = (userId) => {
  try {
    const raw = localStorage.getItem(WATCHLIST_STORAGE_KEY_PREFIX + userId);
    if (raw) return JSON.parse(raw);
  } catch {}
  return null;
};

const saveToStorage = (userId, tabs) => {
  try {
    localStorage.setItem(WATCHLIST_STORAGE_KEY_PREFIX + userId, JSON.stringify(tabs));
  } catch {}
};

const extractWatchlistItems = (response) => {
  const direct = response?.data;
  if (Array.isArray(direct)) return direct;
  if (Array.isArray(direct?.data)) return direct.data;
  if (Array.isArray(response)) return response;
  return [];
};

// ─── WatchlistPage ──────────────────────────────────────────────────────────────
const WatchlistPage = ({ onOpenOrderModal, compact = false }) => {
  const { user } = useAuth();
  const { pulse } = useMarketPulse();

  const [tabs, setTabs] = useState(DEFAULT_TABS);
  const [activeTabId, setActiveTabId] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const searchTimeout = useRef(null);
  const searchSeq = useRef(0);
  const hydrateSeq = useRef(0);
  const [showDepthFor, setShowDepthFor] = useState({});
  const [tickByToken, setTickByToken] = useState({});
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const searchBoxRef = useRef(null);

  const wsFeedUrl = (() => {
    try {
      const base = apiService.baseURL;
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      if (base.startsWith('/')) return `${protocol}//${host}${base}/ws/feed`;
      return base.replace(/^https?:/, protocol === 'wss:' ? 'wss:' : 'ws:') + '/ws/feed';
    } catch {
      return null;
    }
  })();

  const { lastMessage: feedMsg, sendMessage: sendFeed, readyState: feedState } = useWebSocket(wsFeedUrl);

  const mapServerItems = (serverItems) => (serverItems || []).map(item => ({
    id: item.id || item.token,
    symbol: item.symbol,
    exchange: item.exchange,
    token: item.token,
    instrumentType: item.instrument_type || item.instrumentType,
    ltp: item.ltp ?? null,
    close: item.close ?? null,
    underlying: item.underlying || '',
    expiryDate: item.expiry_date ?? null,
    strikePrice: item.strike_price ?? null,
    optionType: item.option_type ?? null,
    change_pct: item.change_pct ?? null,
    tier: item.tier || 'B',  // 'A' = on-demand, 'B' = always subscribed
    hasPosition: item.has_position ?? false,  // whether in open positions
    addedAt: item.added_at ?? null,  // timestamp when added to watchlist
  }));

  const hydrateFromServer = useCallback(async () => {
    if (!user?.id) return { instruments: [], tokens: new Set() };
    // Grab a sequence number BEFORE the async fetch so we can detect stale responses.
    const seq = ++hydrateSeq.current;
    const res = await apiService.get(`/watchlist/${user.id}`);
    // If a newer hydrate call already started (and possibly finished), discard this response
    // to prevent an older, stale server snapshot from overwriting fresher state.
    if (seq !== hydrateSeq.current) return { instruments: [], tokens: new Set() };
    const serverItems = extractWatchlistItems(res);
    const instruments = mapServerItems(serverItems);
    const tokens = new Set(instruments.map(i => String(i.token)));
    const canonicalByToken = new Map(instruments.map(i => [String(i.token), i]));

    setTabs(prev => {
      const base = Array.isArray(prev) && prev.length ? prev : DEFAULT_TABS;
      return base.map(t => {
        const nextInstruments = (t.id === 1 ? instruments : (t.instruments || [])).map(it => {
          const c = canonicalByToken.get(String(it.token));
          return c ? { ...it, ...c } : it;
        });
        return { ...t, instruments: nextInstruments };
      });
    });
    return { instruments, tokens };
  }, [user?.id]);

  // Load from server + localStorage
  useEffect(() => {
    if (!user?.id) return;
    const savedTabs = loadFromStorage(user.id);
    if (savedTabs && savedTabs.length > 0) {
      setTabs(savedTabs);
    }

    (async () => {
      try {
        const { tokens: serverTokens } = await hydrateFromServer();

        // Best-effort: if earlier UI versions stored watchlists only in localStorage,
        // sync those instruments into the server watchlist so prices can hydrate.
        const localTab1 = (savedTabs || []).find(t => t?.id === 1)?.instruments || [];
        const toSync = localTab1
          .map(i => ({
            token: i?.token,
            symbol: i?.symbol,
            exchange: i?.exchange,
            instrumentType: i?.instrumentType || i?.instrument_type,
          }))
          .filter(i => {
            const tok = String(i.token || '').trim();
            if (!tok || !/^\d+$/.test(tok)) return false;
            return !serverTokens.has(tok);
          })
          .slice(0, 50);

        if (toSync.length) {
          await Promise.allSettled(toSync.map(i => apiService.post('/watchlist/add', {
            user_id: String(user?.id || ''),
            token: String(i.token),
            symbol: i.symbol,
            exchange: i.exchange,
          })));
          await hydrateFromServer();
        }
      } catch {}
    })();
  }, [user?.id, hydrateFromServer]);

  useEffect(() => {
    const handler = () => { hydrateFromServer(); };
    window.addEventListener('tn-watchlist-refresh', handler);
    return () => window.removeEventListener('tn-watchlist-refresh', handler);
  }, [hydrateFromServer]);

  // Persist on change
  useEffect(() => {
    if (user?.id) saveToStorage(user.id, tabs);
  }, [tabs, user]);

  const activeTab = tabs.find(t => t.id === activeTabId) || tabs[0];
  const activeTabTokenList = (activeTab?.instruments || [])
    .map(i => Number(i.token))
    .filter(n => Number.isFinite(n) && n > 0);
  const activeTabTokenKey = activeTabTokenList.join(',');

  // Close dropdown on outside click or Escape.
  useEffect(() => {
    const onDown = (e) => {
      if (e.key === 'Escape') {
        setDropdownOpen(false);
        setSearchQuery('');
        setSearchResults([]);
      }
    };
    const onClick = (e) => {
      const el = searchBoxRef.current;
      if (!el) return;
      if (!el.contains(e.target)) {
        setDropdownOpen(false);
        setSearchQuery('');
        setSearchResults([]);
      }
    };
    document.addEventListener('keydown', onDown);
    document.addEventListener('mousedown', onClick);
    return () => {
      document.removeEventListener('keydown', onDown);
      document.removeEventListener('mousedown', onClick);
    };
  }, []);

  // Subscribe WS feed to active watchlist tokens (for bid/ask snapshot when market is open).
  useEffect(() => {
    if (feedState !== WebSocket.OPEN) return;
    const tokens = activeTabTokenList;
    if (tokens.length === 0) return;
    sendFeed({ action: 'subscribe', tokens });
    return () => {
      try { sendFeed({ action: 'unsubscribe', tokens }); } catch {}
    };
  }, [feedState, activeTabId, activeTabTokenKey]);

  useEffect(() => {
    if (!feedMsg) return;
    const msg = feedMsg;
    if (msg?.type === 'snapshot' && Array.isArray(msg.data)) {
      setTickByToken(prev => {
        const next = { ...prev };
        msg.data.forEach(t => {
          if (t?.instrument_token) next[String(t.instrument_token)] = t;
        });
        return next;
      });
    }
    if (msg?.type === 'tick' && msg?.data?.instrument_token) {
      setTickByToken(prev => ({ ...prev, [String(msg.data.instrument_token)]: msg.data }));
    }
  }, [feedMsg]);

  // ── search ──
  const handleSearchInput = (e) => {
    const q = e.target.value;
    setSearchQuery(q);
    if (searchTimeout.current) clearTimeout(searchTimeout.current);
    if (!q.trim() || q.length < 2) { setSearchResults([]); return; }
    searchTimeout.current = setTimeout(() => runSearch(q.trim()), 350);
  };

  const runSearch = async (q) => {
    const seq = ++searchSeq.current;
    setIsSearching(true);
    try {
      const [tierA, tierB, futures, optStrikes, equity] = await Promise.allSettled([
        apiService.get('/subscriptions/search', { tier: 'TIER_A', q }),
        apiService.get('/subscriptions/search', { tier: 'TIER_B', q }),
        apiService.get('/instruments/futures/search', { q }),
        apiService.get('/options/strikes/search', { q }),
        apiService.get('/instruments/search', { q }),
      ]);
      const results = [];
      const seen = new Set();
      const addResults = (res) => {
        if (res.status !== 'fulfilled') return;
        const list = res.value?.data || res.value || [];
        if (!Array.isArray(list)) return;
        list.forEach(item => {
          const key = item.token || item.security_id || item.symbol;
          if (!key || seen.has(key)) return;
          seen.add(key);
          results.push({
            id: key,
            symbol: item.symbol || item.tradingsymbol || key,
            exchange: item.exchange_segment || item.exchange || 'NSE',
            token: item.token || item.security_id || key,
            instrumentType: item.instrument_type || item.instrumentType || 'EQ',
            underlying: item.underlying || '',
            displayName: item.display_name || item.displayName || '',
            tradingSymbol: item.trading_symbol || item.tradingSymbol || '',
            strikePrice: item.strike_price ?? item.strikePrice ?? null,
            optionType: item.option_type ?? item.optionType ?? null,
            expiryDate: item.expiry_date ?? item.expiryDate ?? null,
            ltp: item.ltp ?? null,
            close: item.close ?? null,
            change_pct: item.change_pct ?? null,
          });
        });
      };
      [tierA, tierB, futures, optStrikes, equity].forEach(addResults);
      const normalize = (s) => String(s || '').toUpperCase().replace(/[^A-Z0-9]+/g, ' ').trim();
      const qTokens = normalize(q).split(/\s+/).filter(Boolean);
      const qStrike = qTokens.find(t => /^\d{3,}$/.test(t)) || null;
      const qStrikeNum = qStrike ? Number(qStrike) : null;
      const qFirstAlpha = qTokens.find(t => /^[A-Z]+$/.test(t) && t !== 'CE' && t !== 'PE') || '';

      const score = (r) => {
        const symU = String(r.symbol || '').toUpperCase();
        const undU = String(r.underlying || '').toUpperCase();
        const dispU = String(r.displayName || '').toUpperCase();
        const tsU = String(r.tradingSymbol || '').toUpperCase();
        const symN = normalize(r.symbol);
        const undN = normalize(r.underlying);
        const dispN = normalize(r.displayName);
        const tsN = normalize(r.tradingSymbol);

        const it = String(r.instrumentType || '').toUpperCase();
        const isOption = it.startsWith('OPT');
        const isFuture = it.startsWith('FUT');
        const isCash = String(r.exchange || '').toUpperCase().includes('_EQ') || it === 'EQUITY';
        const isEtf = isCash && (dispU.includes('ETF') || symU.includes('BEES') || symU.includes('ETF'));

        let s = 0;
        if (isCash) s += 12000;
        if (isEtf) s += 400;
        if (isFuture) s += 8000;
        if (isOption) s += 6000;

        if (qFirstAlpha) {
          if (undU === qFirstAlpha) s += 5000;
          if (symU === qFirstAlpha) s += 5200;
        }

        const qU = qTokens.join(' ');
        if (symN === qU) s += 5000;

        // starts-with / contains ranking based on first token only
        if (qFirstAlpha) {
          if (symU.startsWith(qFirstAlpha)) s += 4200;
          if (undU.startsWith(qFirstAlpha)) s += 4000;
          if (dispU.startsWith(qFirstAlpha)) s += 4100;
          if (tsU.startsWith(qFirstAlpha)) s += 4050;
          const si = symU.indexOf(qFirstAlpha);
          const ui = undU.indexOf(qFirstAlpha);
          const di = dispU.indexOf(qFirstAlpha);
          const ti = tsU.indexOf(qFirstAlpha);
          if (si >= 0) s += 3000 - Math.min(si, 50);
          if (ui >= 0) s += 2800 - Math.min(ui, 50);
          if (di >= 0) s += 2900 - Math.min(di, 50);
          if (ti >= 0) s += 2850 - Math.min(ti, 50);
        }

        // Exact strike match when user typed one
        if (qStrikeNum !== null && r.strikePrice !== null && r.strikePrice !== undefined) {
          const sp = Number(r.strikePrice);
          if (!Number.isNaN(sp)) {
            if (sp === qStrikeNum) s += 8000;
            else s += Math.max(0, 1200 - Math.min(Math.abs(sp - qStrikeNum), 1200));
          }
        }

        s += Math.max(0, 500 - Math.min(symU.length, 500));
        return s;
      };

      const ranked = results
        .filter(r => {
          const symN = normalize(r.symbol);
          const undN = normalize(r.underlying);
          const dispN = normalize(r.displayName);
          const tsN = normalize(r.tradingSymbol);
          return qTokens.every(t => symN.includes(t) || undN.includes(t) || dispN.includes(t) || tsN.includes(t));
        })
        .sort((a, b) => score(b) - score(a));

      if (seq === searchSeq.current) {
        setSearchResults(ranked.slice(0, 20));
        setDropdownOpen(true);
      }
    } catch {}
    if (seq === searchSeq.current) setIsSearching(false);
  };

  const handleAddInstrument = async (instrument) => {
    const tokenNum = Number(instrument?.token);
    if (!Number.isFinite(tokenNum) || tokenNum <= 0) {
      return;
    }

    setTabs(prev => prev.map(tab => {
      if (tab.id !== activeTabId) return tab;
      if (tab.instruments.find(i => Number(i.token) === tokenNum)) return tab;
      return { ...tab, instruments: [...tab.instruments, { ...instrument, token: tokenNum }] };
    }));

    try {
      const addRes = await apiService.post('/watchlist/add', {
        user_id: String(user?.id || ''),
        token: String(tokenNum),
        symbol: instrument.symbol,
        exchange: instrument.exchange,
      });

      if (addRes && addRes.success === false) {
        setTabs(prev => prev.map(tab => {
          if (tab.id !== activeTabId) return tab;
          return { ...tab, instruments: tab.instruments.filter(i => Number(i.token) !== tokenNum) };
        }));
        return;
      }

      const serverToken = Number(addRes?.token || tokenNum);
      if (Number.isFinite(serverToken) && serverToken > 0 && serverToken !== tokenNum) {
        setTabs(prev => prev.map(tab => {
          if (tab.id !== activeTabId) return tab;
          return {
            ...tab,
            instruments: tab.instruments.map(i =>
              Number(i.token) === tokenNum ? { ...i, token: serverToken, id: serverToken } : i
            )
          };
        }));
      }

      await hydrateFromServer();
    } catch {
      // rollback optimistic row on failure
      setTabs(prev => prev.map(tab => {
        if (tab.id !== activeTabId) return tab;
        return { ...tab, instruments: tab.instruments.filter(i => Number(i.token) !== tokenNum) };
      }));
    }
    // Keep dropdown open so user can add multiple items via +
  };

  const handleRemoveInstrument = (token) => {
    setTabs(prev => prev.map(tab => {
      if (tab.id !== activeTabId) return tab;
      return { ...tab, instruments: tab.instruments.filter(i => i.token !== token) };
    }));
    apiService.post('/watchlist/remove', { user_id: String(user?.id || ''), token: String(token) }).catch(() => {});
  };

  const getDisplayedPrice = (instrument) => {
    const prices = pulse?.prices;
    const token = String(instrument.token);
    const p = prices ? (prices[token] ?? prices[instrument.symbol]) : null;
    if (p !== null && p !== undefined) return p;

    const liveTick = tickByToken[String(instrument.token)];
    if (liveTick?.ltp !== null && liveTick?.ltp !== undefined) return liveTick.ltp;

    const ex = String(instrument?.exchange || '').toUpperCase();
    const isCommodity = ex.includes('MCX') || ex.includes('COM');
    const marketActive = isCommodity
      ? (pulse?.marketActiveCommodity ?? pulse?.marketActive ?? pulse?.market_active_commodity ?? pulse?.market_active)
      : (pulse?.marketActiveEquity ?? pulse?.marketActive ?? pulse?.market_active_equity ?? pulse?.market_active);

    if (marketActive === false) return instrument.close ?? instrument.ltp ?? null;
    return instrument.ltp ?? null;
  };

  const formatOptionLabel = (r) => {
    const it = String(r.instrumentType || r.instrument_type || '').toUpperCase();
    const expiry = r.expiryDate || r.expiry_date;
    const strike = r.strikePrice ?? r.strike_price;
    const opt = r.optionType || r.option_type;
    const underlying = (r.underlying || r.symbol || '').toUpperCase();
    const isOpt = it.startsWith('OPT') && expiry && strike !== null && strike !== undefined && opt;
    if (!isOpt) return null;
    const d = new Date(expiry);
    const monthShort = d.toLocaleString('en-GB', { month: 'short' });
    const day = String(d.getDate()).padStart(2, '0');
    const strikeNum = Number(strike);
    const strikeTxt = Number.isFinite(strikeNum) ? String(Math.trunc(strikeNum)) : String(strike);
    return `${underlying} ${strikeTxt} ${String(opt).toUpperCase()} ${day} ${monthShort}`;
  };

  const getChangePct = (instrument, ltpOverride = null) => {
    const ltp = ltpOverride !== null && ltpOverride !== undefined ? ltpOverride : instrument?.ltp;
    const close = instrument?.close;
    if (typeof instrument?.change_pct === 'number') return instrument.change_pct;
    if (ltp == null || close == null || Number(close) === 0) return null;
    const pct = ((Number(ltp) - Number(close)) / Number(close)) * 100;
    return Number.isFinite(pct) ? pct : null;
  };

  // styles
  const card = { backgroundColor: 'var(--surface)', borderRadius: '8px', border: '1px solid var(--border)', overflow: 'hidden' };
  const tabRow = { display: 'flex', borderBottom: '2px solid var(--border)', backgroundColor: 'var(--surface2)' };
  const tabBtn = (active) => ({ flex: 1, padding: '10px 4px', border: 'none', cursor: 'pointer', fontSize: '12px', fontWeight: active ? 700 : 500, color: active ? 'var(--accent)' : 'var(--muted)', backgroundColor: 'transparent', borderBottom: active ? '2px solid var(--accent)' : '2px solid transparent', marginBottom: '-2px', transition: 'all 0.15s' });
  const instrRow = { display: 'flex', alignItems: 'center', padding: '10px 14px', borderBottom: '1px solid var(--border)', gap: '8px' };
  const symbolStyle = { flex: 1, fontSize: '13px', fontWeight: 600, color: 'var(--text)' };
  const exStyle = { fontSize: '10px', color: 'var(--muted)', marginLeft: '4px' };
  const ltpStyle = (v) => ({ fontSize: '13px', fontWeight: 600, color: v === null ? 'var(--muted)' : 'var(--text)', minWidth: '60px', textAlign: 'right' });
  const removeBtn = { border: 'none', background: 'none', cursor: 'pointer', padding: '4px', color: '#dc2626', display: 'flex', alignItems: 'center' };

  return (
    <div
      style={{
        minHeight: compact ? '100%' : '100vh',
        height: compact ? '100%' : 'auto',
        padding: compact ? '0' : '24px',
        backgroundColor: compact ? 'transparent' : 'var(--bg)',
        fontFamily: "system-ui, -apple-system, sans-serif",
        color: 'var(--text)'
      }}
    >
      <div
        style={{
          maxWidth: compact ? '100%' : '480px',
          margin: compact ? '0' : '0 auto',
          height: compact ? '100%' : 'auto',
          display: compact ? 'flex' : 'block',
          flexDirection: compact ? 'column' : 'row'
        }}
      >
        {!compact && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 700, color: 'var(--text)' }}>Watchlist</h2>
          </div>
        )}

        <div ref={searchBoxRef} style={{ ...card, marginBottom: compact ? '8px' : '12px', padding: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', border: '1px solid var(--border)', borderRadius: '8px', padding: '6px 10px', backgroundColor: 'var(--surface)' }}>
            <Search size={14} color="var(--muted)" />
            <input
              value={searchQuery}
              onChange={handleSearchInput}
              onFocus={() => { if (searchResults.length) setDropdownOpen(true); }}
              placeholder="Search symbol, equities/ETFs, futures, options…"
              style={{ flex: 1, border: 'none', outline: 'none', background: 'transparent', fontSize: '13px', color: 'var(--text)' }}
            />
            {isSearching && <RefreshCw size={14} className="animate-spin" color="var(--muted)" />}
          </div>
          {dropdownOpen && searchResults.length > 0 && (
            <div style={{ marginTop: '8px', maxHeight: '240px', overflowY: 'auto' }}>
              {searchResults.map(r => (
                <div key={r.id} style={{ padding: '8px 10px', borderRadius: '6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '10px' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--surface2)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', flex: 1 }}>
                    {(() => {
                        const label = formatOptionLabel(r);
                        if (label) {
                        const price = r.ltp ?? r.close;
                        const pct = (typeof r.change_pct === 'number') ? r.change_pct : null;
                        return (
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                              <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text)' }}>{label}</span>
                            <span style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '10px', fontSize: '12px' }}>
                              {pct !== null && <span style={{ color: '#a1a1aa' }}>{pct.toFixed(2)} %</span>}
                              {price != null && <span style={{ color: 'var(--text)', fontWeight: 800 }}>{Number(price).toFixed(2)}</span>}
                            </span>
                          </div>
                        );
                      }
                      return (
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '10px' }}>
                          <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text)' }}>{r.symbol}</span>
                          <span style={{ fontSize: '11px', color: 'var(--muted)' }}>{r.exchange} · {r.instrumentType}</span>
                        </div>
                      );
                    })()}
                  </div>

                  <button
                    type="button"
                    onClick={() => handleAddInstrument(r)}
                    style={{ border: '1px solid var(--border)', background: 'var(--surface)', color: 'var(--text)', cursor: 'pointer', borderRadius: '8px', padding: '6px 10px', display: 'flex', alignItems: 'center', gap: '6px' }}
                    title="Add"
                  >
                    <Plus size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}
          {searchQuery.length >= 2 && !isSearching && searchResults.length === 0 && (
            <div style={{ padding: '8px', fontSize: '13px', color: 'var(--muted)', textAlign: 'center' }}>No results</div>
          )}
        </div>

        <div style={compact ? { ...card, display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 } : card}>
          <div style={tabRow}>
            {tabs.map(tab => (
              <button key={tab.id} style={tabBtn(tab.id === activeTabId)} onClick={() => setActiveTabId(tab.id)}>
                {tab.name} <span style={{ ...exStyle, display: 'inline' }}>({tab.instruments.length})</span>
              </button>
            ))}
          </div>
          <div style={compact ? { flex: 1, minHeight: 0, overflowY: 'auto' } : undefined}>
            {activeTab.instruments.length === 0 ? (
              <div
                style={compact
                  ? { minHeight: '220px', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px', textAlign: 'center', color: 'var(--muted)', fontSize: '13px' }
                  : { padding: '32px', textAlign: 'center', color: 'var(--muted)', fontSize: '13px' }
                }
              >
                No instruments in this watchlist.<br />Click Add to search and add instruments.
              </div>
            ) : (
              activeTab.instruments.map(inst => {
                const ltp = getDisplayedPrice(inst);
                const ex = String(inst?.exchange || '').toUpperCase();
                const isCommodity = ex.includes('MCX') || ex.includes('COM');
                const marketActive = isCommodity
                  ? (pulse?.marketActiveCommodity ?? pulse?.marketActive ?? pulse?.market_active_commodity ?? pulse?.market_active) !== false
                  : (pulse?.marketActiveEquity ?? pulse?.marketActive ?? pulse?.market_active_equity ?? pulse?.market_active) !== false;
                const tick = tickByToken[String(inst.token)];
                const bid = tick?.bid_depth?.[0]?.price ?? tick?.best_bid ?? tick?.bid ?? tick?.bid_price ?? null;
                const ask = tick?.ask_depth?.[0]?.price ?? tick?.best_ask ?? tick?.ask ?? tick?.ask_price ?? null;

                const label = formatOptionLabel({
                  instrumentType: inst.instrumentType,
                  expiryDate: inst.expiryDate,
                  strikePrice: inst.strikePrice,
                  optionType: inst.optionType,
                  underlying: inst.underlying,
                  symbol: inst.symbol,
                });
                const title = label || inst.symbol;
                const pct = getChangePct(inst, ltp);
                return (
                  <div key={inst.token} style={{ ...instrRow, flexDirection: 'column', alignItems: 'stretch' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={symbolStyle}>{title}</span>
                        {/* Tier indicator badge (show only Tier-A) */}
                        {inst.tier === 'A' && (
                          <span style={{
                            fontSize: '10px',
                            padding: '2px 6px',
                            borderRadius: '3px',
                            backgroundColor: 'rgba(255,165,0,0.2)',
                            color: '#FFA500',
                            fontWeight: 600,
                            whiteSpace: 'nowrap'
                          }}>
                            Tier-A
                          </span>
                        )}
                        {/* Position indicator */}
                        {inst.tier === 'A' && (
                          <span style={{
                            fontSize: '10px',
                            padding: '2px 6px',
                            borderRadius: '3px',
                            backgroundColor: inst.hasPosition ? 'rgba(76,175,80,0.2)' : 'rgba(244,67,54,0.2)',
                            color: inst.hasPosition ? '#4CAF50' : '#F44336',
                            fontWeight: 600,
                            whiteSpace: 'nowrap'
                          }}>
                            {inst.hasPosition ? '✓ Position' : '⊘ No Position'}
                          </span>
                        )}
                      </div>
                      <span style={exStyle}>{inst.exchange}</span>
                    </div>
                    {pct !== null && <span style={{ fontSize: '12px', color: 'var(--muted)', minWidth: '70px', textAlign: 'right' }}>{pct.toFixed(2)} %</span>}
                    <span style={ltpStyle(ltp)}>{ltp !== null ? Number(ltp).toFixed(2) : '—'}</span>

                    <button
                      style={{ border: 'none', background: 'transparent', cursor: 'pointer', padding: '4px', color: 'var(--muted)', display: 'flex', alignItems: 'center' }}
                      title="Bid/Ask"
                      onClick={() => setShowDepthFor(prev => ({ ...prev, [String(inst.token)]: !prev[String(inst.token)] }))}
                    >
                      <ChevronDown size={14} />
                    </button>

                    <button className="trade-btn buy" onClick={() => onOpenOrderModal?.({ symbol: inst.symbol, displaySymbol: label || inst.symbol, token: inst.token, exchange: inst.exchange, ltp: ltp, instrumentType: inst.instrumentType, expiryDate: inst.expiryDate, strikePrice: inst.strikePrice, optionType: inst.optionType, underlying: inst.underlying }, 'BUY')}>BUY</button>
                    <button className="trade-btn sell" onClick={() => onOpenOrderModal?.({ symbol: inst.symbol, displaySymbol: label || inst.symbol, token: inst.token, exchange: inst.exchange, ltp: ltp, instrumentType: inst.instrumentType, expiryDate: inst.expiryDate, strikePrice: inst.strikePrice, optionType: inst.optionType, underlying: inst.underlying }, 'SELL')}>SELL</button>
                    <button style={removeBtn} onClick={() => handleRemoveInstrument(inst.token)} title="Remove"><X size={14} /></button>
                    </div>

                    {showDepthFor[String(inst.token)] && (
                      <div style={{ marginTop: '8px', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--surface)', display: 'flex', justifyContent: 'space-between' }}>
                        <div style={{ fontSize: '12px', color: 'var(--text)' }}>
                          <div style={{ fontSize: '11px', color: 'var(--muted)', marginBottom: '4px' }}>Bid</div>
                          <div style={{ fontWeight: 700 }}>{bid !== null ? Number(bid).toFixed(2) : '—'}</div>
                        </div>
                        <div style={{ fontSize: '12px', color: 'var(--text)', textAlign: 'right' }}>
                          <div style={{ fontSize: '11px', color: 'var(--muted)', marginBottom: '4px' }}>Ask</div>
                          <div style={{ fontWeight: 700 }}>{ask !== null ? Number(ask).toFixed(2) : '—'}</div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WatchlistPage;
