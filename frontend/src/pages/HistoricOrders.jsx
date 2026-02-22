import React, { useState, useCallback, useEffect, useMemo } from "react";
import { apiService } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';

const today = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
};

const HistoricOrdersPage = () => {
  const { user } = useAuth();
  const isAdmin = user?.role === "ADMIN" || user?.role === "SUPER_ADMIN";

  const [fromDate, setFromDate] = useState(today());
  const [toDate, setToDate] = useState(today());
  const [userIdOrMobile, setUserIdOrMobile] = useState("");
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sortConfig, setSortConfig] = useState({ key: "placed_at", direction: "desc" });
  const [selectedOrderId, setSelectedOrderId] = useState(null);

  // Check admin access
  if (!isAdmin) {
    return (
      <div style={{ padding: '24px', color: 'var(--text)', fontFamily: 'system-ui,sans-serif' }}>
        <div style={{ background: '#7f1d1d33', border: '1px solid #ef4444', padding: '12px 16px', borderRadius: '8px', color: '#fca5a5' }}>
          Access denied. Only admins can view historic orders.
        </div>
      </div>
    );
  }

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    try {
      const params = {
        from_date: fromDate,
        to_date: toDate,
      };
      
      // Determine if input is UUID or mobile
      if (userIdOrMobile) {
        if (userIdOrMobile.includes('-') || userIdOrMobile.length === 36) {
          params.user_id = userIdOrMobile;
        } else {
          params.mobile = userIdOrMobile;
        }
      }
      
      const res = await apiService.get('/trading/orders/historic/orders', params);
      setOrders(res?.data?.data || []);
    } catch (err) {
      console.error('Error fetching historic orders:', err);
      setOrders([]);
    } finally {
      setLoading(false);
    }
  }, [fromDate, toDate, userIdOrMobile]);

  const sortedOrders = useMemo(() => {
    const data = [...orders];
    if (!sortConfig.key) return data;
    
    data.sort((a, b) => {
      let av = a[sortConfig.key];
      let bv = b[sortConfig.key];
      
      if (av < bv) return sortConfig.direction === "asc" ? -1 : 1;
      if (av > bv) return sortConfig.direction === "asc" ? 1 : -1;
      return 0;
    });
    return data;
  }, [orders, sortConfig]);

  const onHeaderClick = (key) => {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key ? (prev.direction === "asc" ? "desc" : "asc") : "asc",
    }));
  };

  const handleRowClick = (id) => setSelectedOrderId((prev) => (prev === id ? null : id));
  const selectedOrder = sortedOrders.find((o) => o.order_id === selectedOrderId) || null;

  const formatDateTime = (isoString) => {
    if (!isoString) return "—";
    const date = new Date(isoString);
    return date.toLocaleDateString("en-IN") + " " + date.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
  };

  const s = {
    page: { padding: '24px', fontFamily: 'system-ui,sans-serif', color: 'var(--text)', minHeight: '100vh' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' },
    title: { fontSize: '20px', fontWeight: 700, margin: 0 },
    filterBar: { display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' },
    input: { padding: '7px 10px', background: '#09090b', border: '1px solid #3f3f46', borderRadius: '6px', color: '#f4f4f5', fontSize: '13px' },
    label: { fontSize: '12px', color: '#a1a1aa' },
    button: { padding: '8px 20px', borderRadius: '6px', border: 'none', background: '#2563eb', color: '#fff', fontWeight: '700', fontSize: '13px', cursor: 'pointer', opacity: loading ? 0.6 : 1 },
    card: { background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '10px', padding: '20px', overflow: 'hidden' },
    table: { width: '100%', borderCollapse: 'collapse', fontSize: '12px' },
    thead: { background: 'var(--surface2)', borderBottom: '1px solid var(--border)' },
    th: { padding: '10px 12px', textAlign: 'left', fontWeight: '600', color: 'var(--muted)', fontSize: '11px', cursor: 'pointer', whiteSpace: 'nowrap' },
    tr: { borderBottom: '1px solid var(--border)', cursor: 'pointer' },
    trSelected: { background: 'var(--surface2)' },
    td: { padding: '10px 12px', color: 'var(--text)', whiteSpace: 'nowrap' },
    details: { flex: '1 0 300px', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '10px', padding: '16px', maxHeight: '600px', overflowY: 'auto' },
    layout: { display: 'flex', gap: '16px', marginTop: '16px' },
    tableWrapper: { flex: '2 1 0' },
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
        <h1 style={s.title}>Historic Orders</h1>
        <div style={s.filterBar}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={s.label}>From</span>
            <input type="date" value={fromDate} onChange={e => setFromDate(e.target.value)} style={s.input} />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={s.label}>To</span>
            <input type="date" value={toDate} onChange={e => setToDate(e.target.value)} style={s.input} />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={s.label}>User ID / Mobile</span>
            <input 
              type="text" 
              placeholder="User ID or Mobile" 
              value={userIdOrMobile} 
              onChange={e => setUserIdOrMobile(e.target.value)} 
              style={{...s.input, minWidth: '150px'}} 
            />
          </div>
          <button onClick={fetchOrders} disabled={loading} style={s.button}>
            {loading ? "Loading…" : "Apply"}
          </button>
        </div>
      </div>

      <div style={s.layout}>
        <div style={s.tableWrapper}>
          <div style={{...s.card, padding: '0', overflow: 'visible'}}>
            <table style={s.table}>
              <thead style={s.thead}>
                <tr>
                  {sortableHeader("Placed At", "placed_at")}
                  {sortableHeader("User ID", "user_id")}
                  {sortableHeader("Symbol", "symbol")}
                  {sortableHeader("Side", "side")}
                  {sortableHeader("Type", "order_type")}
                  {sortableHeader("Qty", "quantity")}
                  {sortableHeader("Price", "fill_price")}
                  {sortableHeader("Status", "status")}
                </tr>
              </thead>
              <tbody>
                {sortedOrders.map((o) => (
                  <tr 
                    key={o.order_id} 
                    style={{...s.tr, ...(selectedOrderId === o.order_id ? s.trSelected : {})}} 
                    onClick={() => handleRowClick(o.order_id)}
                  >
                    <td style={s.td}>{formatDateTime(o.placed_at)}</td>
                    <td style={{...s.td, fontSize: '10px', maxWidth: '100px', overflow: 'hidden', textOverflow: 'ellipsis'}} title={o.user_id}>{o.user_id}</td>
                    <td style={s.td}>{o.symbol || '—'}</td>
                    <td style={s.td}><span style={{padding: '2px 8px', borderRadius: '3px', background: o.side === 'BUY' ? '#1e40af33' : '#b91c1c33', color: o.side === 'BUY' ? '#60a5fa' : '#f87171'}}>{o.side}</span></td>
                    <td style={s.td}>{o.order_type || '—'}</td>
                    <td style={{...s.td, textAlign: 'right'}}>{o.quantity || 0}</td>
                    <td style={{...s.td, textAlign: 'right'}}>₹{Number(o.fill_price || 0).toFixed(2)}</td>
                    <td style={{...s.td, color: o.status === 'FILLED' ? '#22c55e' : o.status === 'REJECTED' ? '#ef4444' : '#a1a1aa'}}>{o.status}</td>
                  </tr>
                ))}
                {sortedOrders.length === 0 && (
                  <tr>
                    <td colSpan="8" style={{...s.td, textAlign: 'center', padding: '20px', color: '#a1a1aa'}}>
                      No orders found for the selected criteria.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {selectedOrder && (
          <div style={s.details}>
            <div style={{ fontSize: '13px', fontWeight: '600', marginBottom: '12px', color: 'var(--text)' }}>Order Details</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
              <div><span style={{ color: 'var(--muted)' }}>Order ID:</span> <code style={{ fontSize: '10px', background: 'var(--surface2)', padding: '2px 6px', borderRadius: '3px' }}>{selectedOrder.order_id}</code></div>
              <div><span style={{ color: 'var(--muted)' }}>User ID:</span> <code style={{ fontSize: '10px', background: 'var(--surface2)', padding: '2px 6px', borderRadius: '3px' }}>{selectedOrder.user_id}</code></div>
              <div><span style={{ color: 'var(--muted)' }}>Symbol:</span> {selectedOrder.symbol || '—'}</div>
              <div><span style={{ color: 'var(--muted)' }}>Side:</span> <span style={{ fontWeight: '600', color: selectedOrder.side === 'BUY' ? '#60a5fa' : '#f87171' }}>{selectedOrder.side}</span></div>
              <div><span style={{ color: 'var(--muted)' }}>Order Type:</span> {selectedOrder.order_type}</div>
              <div><span style={{ color: 'var(--muted)' }}>Quantity:</span> {selectedOrder.quantity}</div>
              <div><span style={{ color: 'var(--muted)' }}>Limit Price:</span> ₹{Number(selectedOrder.limit_price || 0).toFixed(2)}</div>
              <div><span style={{ color: 'var(--muted)' }}>Fill Price:</span> ₹{Number(selectedOrder.fill_price || 0).toFixed(2)}</div>
              <div><span style={{ color: 'var(--muted)' }}>Filled Qty:</span> {selectedOrder.filled_qty || 0}</div>
              <div><span style={{ color: 'var(--muted)' }}>Status:</span> <span style={{ fontWeight: '600', color: selectedOrder.status === 'FILLED' ? '#22c55e' : '#ef4444' }}>{selectedOrder.status}</span></div>
              <div><span style={{ color: 'var(--muted)' }}>Placed At:</span> {formatDateTime(selectedOrder.placed_at)}</div>
              <div><span style={{ color: 'var(--muted)' }}>Filled At:</span> {selectedOrder.filled_at ? formatDateTime(selectedOrder.filled_at) : '—'}</div>
              <div><span style={{ color: 'var(--muted)' }}>Archived At:</span> {selectedOrder.archived_at ? formatDateTime(selectedOrder.archived_at) : '—'}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default HistoricOrdersPage;
