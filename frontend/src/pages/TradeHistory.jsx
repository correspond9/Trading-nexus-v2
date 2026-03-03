import React, { useState, useCallback, useEffect, useMemo } from "react";
import { apiService } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';

const daysAgo = (n) => {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toLocaleDateString("en-CA");
};

const today = () => new Date().toLocaleDateString("en-CA");

const TradeHistoryPage = () => {
  const { user } = useAuth();
  const [fromDate, setFromDate] = useState(daysAgo(30)); // Default: last 30 days
  const [toDate, setToDate] = useState(today());
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sortConfig, setSortConfig] = useState({ key: "placed_at", direction: "desc" });
  const [selectedTradeId, setSelectedTradeId] = useState(null);
  const [isMobile, setIsMobile] = useState(() => window.innerWidth <= 900);

  useEffect(() => {
    const onResize = () => setIsMobile(window.innerWidth <= 900);
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  // Fetch trades on mount and when dates change
  const fetchTrades = useCallback(async () => {
    setLoading(true);
    try {
      const params = {
        from_date: fromDate,
        to_date: toDate,
        // No user_id parameter - API will use current user from auth context
      };
      
      const res = await apiService.get('/trading/orders/executed', params);
      const filledOrders = res?.data || [];
      setTrades(filledOrders);
    } catch (err) {
      console.error('Error fetching trade history:', err);
      setTrades([]);
    } finally {
      setLoading(false);
    }
  }, [fromDate, toDate]);

  useEffect(() => {
    fetchTrades();
  }, [fetchTrades]);

  const sortedTrades = useMemo(() => {
    const data = [...trades];
    if (!sortConfig.key) return data;
    
    data.sort((a, b) => {
      let av = a[sortConfig.key];
      let bv = b[sortConfig.key];
      
      if (av < bv) return sortConfig.direction === "asc" ? -1 : 1;
      if (av > bv) return sortConfig.direction === "asc" ? 1 : -1;
      return 0;
    });
    return data;
  }, [trades, sortConfig]);

  const onHeaderClick = (key) => {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key ? (prev.direction === "asc" ? "desc" : "asc") : "asc",
    }));
  };

  const handleRowClick = (id) => setSelectedTradeId((prev) => (prev === id ? null : id));
  const selectedTrade = sortedTrades.find((t) => t.id === selectedTradeId) || null;

  const formatDateTime = (isoString) => {
    if (!isoString) return "—";
    const date = new Date(isoString);
    return date.toLocaleDateString("en-IN") + " " + date.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
  };

  const formatCurrency = (value) => {
    return (
      (Number(value) < 0 ? "-₹" : "₹") +
      Math.abs(Number(value) || 0).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    );
  };

  const s = {
    page: { padding: isMobile ? '12px' : '24px', fontFamily: 'system-ui,sans-serif', color: 'var(--text)', minHeight: '100vh' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' },
    title: { fontSize: '20px', fontWeight: 700, margin: 0 },
    filterBar: { display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' },
    input: { padding: '7px 10px', background: 'var(--control-bg)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text)', fontSize: '13px' },
    label: { fontSize: '12px', color: 'var(--muted)' },
    button: { padding: '8px 20px', borderRadius: '6px', border: 'none', background: '#2563eb', color: '#fff', fontWeight: '700', fontSize: '13px', cursor: 'pointer', opacity: loading ? 0.6 : 1 },
    card: { background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '10px', padding: isMobile ? '12px' : '20px', overflow: 'hidden' },
    table: { width: '100%', minWidth: '980px', borderCollapse: 'collapse', fontSize: '12px' },
    thead: { background: 'var(--surface2)', borderBottom: '1px solid var(--border)' },
    th: { padding: '10px 12px', textAlign: 'left', fontWeight: '600', color: 'var(--muted)', fontSize: '11px', cursor: 'pointer', whiteSpace: 'nowrap' },
    tr: { borderBottom: '1px solid var(--border)', cursor: 'pointer' },
    trSelected: { background: 'var(--surface2)' },
    td: { padding: '10px 12px', color: 'var(--text)', whiteSpace: 'nowrap' },
    details: { flex: isMobile ? '1 1 auto' : '1 0 300px', width: isMobile ? '100%' : 'auto', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '10px', padding: '16px', maxHeight: isMobile ? 'none' : '600px', overflowY: 'auto' },
    layout: { display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: '16px', marginTop: '16px' },
    tableWrapper: { flex: '2 1 0', minWidth: 0 },
  };

  const sortableHeader = (label, key) => {
    const isActive = sortConfig.key === key;
    const arrow = sortConfig.direction === "asc" ? "▲" : "▼";
    return (
      <th key={key} style={{...s.th, color: isActive ? 'var(--accent)' : 'var(--muted)'}} onClick={() => onHeaderClick(key)}>
        {label} {isActive && <span style={{ marginLeft: 4, fontSize: '10px' }}>{arrow}</span>}
      </th>
    );
  };

  return (
    <div style={s.page}>
      <div style={s.header}>
        <h1 style={s.title}>Trade History</h1>
        <div style={s.filterBar}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={s.label}>From</span>
            <input type="date" value={fromDate} onChange={e => setFromDate(e.target.value)} style={s.input} />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={s.label}>To</span>
            <input type="date" value={toDate} onChange={e => setToDate(e.target.value)} style={s.input} />
          </div>
          <button onClick={fetchTrades} disabled={loading} style={s.button}>
            {loading ? "Loading…" : "Apply"}
          </button>
        </div>
      </div>

      <div style={s.layout}>
        <div style={s.tableWrapper}>
          <div style={{...s.card, padding: '0', overflowX: 'auto', overflowY: 'hidden'}}>
            <table style={s.table}>
              <thead style={s.thead}>
                <tr>
                  {sortableHeader("Date & Time", "placed_at")}
                  {sortableHeader("Symbol", "symbol")}
                  {sortableHeader("Side", "side")}
                  {sortableHeader("Type", "order_type")}
                  {sortableHeader("Qty", "quantity")}
                  {sortableHeader("Price", "execution_price")}
                  {sortableHeader("Value", "qty")}
                </tr>
              </thead>
              <tbody>
                {sortedTrades.map((t) => {
                  const qty = Number(t.qty || t.quantity || 0);
                  const price = Number(t.execution_price || t.price || 0);
                  const value = qty * price;
                  return (
                    <tr 
                      key={t.id} 
                      style={{...s.tr, ...(selectedTradeId === t.id ? s.trSelected : {})}} 
                      onClick={() => handleRowClick(t.id)}
                    >
                      <td style={s.td}>{formatDateTime(t.placed_at || t.created_at)}</td>
                      <td style={{...s.td, fontWeight: 600}}>{t.symbol || '—'}</td>
                      <td style={s.td}><span style={{padding: '2px 8px', borderRadius: '3px', background: t.side === 'BUY' ? '#1e40af33' : '#b91c1c33', color: t.side === 'BUY' ? '#60a5fa' : '#f87171'}}>{t.side}</span></td>
                      <td style={s.td}>{t.order_type || t.orderMode || '—'}</td>
                      <td style={{...s.td, textAlign: 'right'}}>{qty.toLocaleString('en-IN')}</td>
                      <td style={{...s.td, textAlign: 'right'}}>{formatCurrency(price)}</td>
                      <td style={{...s.td, textAlign: 'right'}}>{formatCurrency(value)}</td>
                    </tr>
                  );
                })}
                {sortedTrades.length === 0 && (
                  <tr>
                    <td colSpan="7" style={{...s.td, textAlign: 'center', padding: '20px', color: 'var(--text)'}}>
                      No executed trades found for the selected period.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {selectedTrade && (
          <div style={s.details}>
            <div style={{ fontSize: '13px', fontWeight: '600', marginBottom: '12px', color: 'var(--text)' }}>Trade Details</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
              <div><span style={{ color: 'var(--muted)' }}>Order ID:</span> <code style={{ fontSize: '10px', background: 'var(--surface2)', padding: '2px 6px', borderRadius: '3px' }}>{selectedTrade.id}</code></div>
              <div><span style={{ color: 'var(--muted)' }}>Symbol:</span> {selectedTrade.symbol || '—'}</div>
              <div><span style={{ color: 'var(--muted)' }}>Side:</span> <span style={{ fontWeight: '600', color: selectedTrade.side === 'BUY' ? '#60a5fa' : '#f87171' }}>{selectedTrade.side}</span></div>
              <div><span style={{ color: 'var(--muted)' }}>Order Type:</span> {selectedTrade.order_type || selectedTrade.orderMode || '—'}</div>
              <div><span style={{ color: 'var(--muted)' }}>Quantity:</span> {Number(selectedTrade.qty || selectedTrade.quantity || 0).toLocaleString('en-IN')}</div>
              <div><span style={{ color: 'var(--muted)' }}>Execution Price:</span> {formatCurrency(selectedTrade.execution_price || selectedTrade.price || 0)}</div>
              <div><span style={{ color: 'var(--muted)' }}>Product Type:</span> {selectedTrade.product_type || selectedTrade.productType || 'MIS'}</div>
              <div><span style={{ color: 'var(--muted)' }}>Executed At:</span> {formatDateTime(selectedTrade.placed_at || selectedTrade.created_at)}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TradeHistoryPage;
