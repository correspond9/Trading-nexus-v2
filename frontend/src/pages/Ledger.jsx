import React, { useState, useEffect, useCallback } from "react";
import { apiService } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';

const today = () => new Date().toLocaleDateString("en-CA"); // YYYY-MM-DD

const LedgerPage = () => {
  const { user } = useAuth();
  const isAdmin = user?.role === "ADMIN" || user?.role === "SUPER_ADMIN" || user?.role === "SUPER_USER";
  const [isMobile, setIsMobile] = useState(() => window.innerWidth <= 900);
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fromDate, setFromDate] = useState(today());
  const [toDate, setToDate] = useState(today());
  const [targetUid, setTargetUid] = useState(""); // "" = self
  const [userList,  setUserList]  = useState([]);
  const [searchQ,   setSearchQ]   = useState("");

  // Load full user list for admin
  useEffect(() => {
    if (!isAdmin) return;
    apiService.get("/admin/users").then(res => {
      setUserList(res?.data?.data || res?.data || []);
    }).catch(() => {});
  }, [isAdmin]);

  const fetchLedger = useCallback(async () => {
    setLoading(true);
    try {
      const params = { from_date: fromDate, to_date: toDate };
      if (isAdmin && targetUid) {
        params.user_id = targetUid;
      } else if (user?.id) {
        params.user_id = String(user.id);
      }
      const res = await apiService.get('/ledger', params);
      setEntries(res?.data || []);
    } catch (err) {
      console.error('Error fetching ledger:', err);
      setEntries([]);
    } finally {
      setLoading(false);
    }
  }, [fromDate, toDate, targetUid, isAdmin, user?.id]);

  useEffect(() => {
    fetchLedger();
    // eslint-disable-next-line
  }, [user]);

  useEffect(() => {
    const onResize = () => setIsMobile(window.innerWidth <= 900);
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  // Filter user list by search query
  const filteredUsers = searchQ.trim()
    ? userList.filter(u => {
        const q = searchQ.toLowerCase();
        return (
          (u.first_name || u.name || "").toLowerCase().includes(q) ||
          (u.last_name || "").toLowerCase().includes(q) ||
          (u.mobile || "").includes(q)
        );
      })
    : userList;

  const s = {
    page: { padding: isMobile ? '12px' : '24px', fontFamily: 'system-ui,sans-serif', color: 'var(--text)' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' },
    title: { fontSize: '20px', fontWeight: 700, margin: 0, color: 'var(--text)' },
    filterBar: { display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' },
    input: { padding: '7px 10px', background: 'var(--control-bg)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text)', fontSize: '13px' },
    label: { fontSize: '12px', color: 'var(--muted)' },
    button: { padding: '8px 20px', borderRadius: '6px', border: 'none', background: '#2563eb', color: '#fff', fontWeight: '700', fontSize: '13px', cursor: 'pointer', opacity: loading ? 0.6 : 1 },
    card: { background: 'var(--surface)', borderRadius: '8px', border: '1px solid var(--border)', padding: isMobile ? '12px' : '20px' },
    th: { padding: '10px 14px', textAlign: 'left', background: 'var(--surface2)', borderBottom: '1px solid var(--border)', fontWeight: '600', color: 'var(--muted)', fontSize: '12px' },
    td: { padding: '10px 14px', borderBottom: '1px solid var(--border)', fontSize: '13px', color: 'var(--text)' }
  };

  return (
    <div style={s.page}>
      <div style={s.header}>
        <h1 style={s.title}>Ledger</h1>
        <div style={s.filterBar}>
          {/* Admin: user search + select */}
          {isAdmin && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', minWidth: isMobile ? '100%' : '200px' }}>
              <input
                type="text"
                placeholder="Search user by name / mobile…"
                value={searchQ}
                onChange={e => setSearchQ(e.target.value)}
                style={{ ...s.input, fontSize: '12px' }}
              />
              <select
                value={targetUid}
                onChange={e => { setTargetUid(e.target.value); setSearchQ(""); }}
                style={{ ...s.input, cursor: 'pointer' }}
              >
                <option value="">— My Account —</option>
                {filteredUsers.map(u => (
                  <option key={u.id} value={u.id}>
                    {u.first_name || u.name || u.mobile} {u.last_name || ""} ({u.mobile})
                  </option>
                ))}
              </select>
            </div>
          )}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={s.label}>From</span>
            <input type="date" value={fromDate} onChange={e => setFromDate(e.target.value)} style={s.input} />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={s.label}>To</span>
            <input type="date" value={toDate} onChange={e => setToDate(e.target.value)} style={s.input} />
          </div>
          <button onClick={fetchLedger} disabled={loading} style={s.button}>
            {loading ? "Loading…" : "Apply"}
          </button>
        </div>
      </div>
      <div style={s.card}>
        {loading ? <div>Loading...</div> : entries.length === 0 ? <div style={{ color: '#a1a1aa', fontSize: '13px' }}>No ledger entries found.</div> : (
          <div style={{ overflowX: 'auto', overflowY: 'hidden' }}>
            <table style={{ width: '100%', minWidth: '900px', borderCollapse: 'collapse' }}>
              <thead><tr>{['Date', 'Description', 'Type', 'Debit', 'Credit', 'Balance'].map(h => <th key={h} style={s.th}>{h}</th>)}</tr></thead>
              <tbody>{entries.map((e, i) => {
                const isTradeEntry = e.type === 'trade_pnl';
                return (
                  <tr key={i}>
                    <td style={s.td}>{e.date?.split('T')[0] || e.date}</td>
                    <td style={s.td}>{e.description}</td>
                    <td style={s.td}>
                      <span style={{
                        padding: '2px 8px',
                        borderRadius: '4px',
                        fontSize: '10px',
                        fontWeight: '600',
                        background: isTradeEntry ? '#10b981' : '#6b7280',
                        color: '#fff'
                      }}>
                        {isTradeEntry ? 'TRADE P&L' : 'WALLET'}
                      </span>
                    </td>
                    <td style={s.td}>{e.debit != null ? '₹' + Number(e.debit).toFixed(2) : '—'}</td>
                    <td style={s.td}>{e.credit != null ? '₹' + Number(e.credit).toFixed(2) : '—'}</td>
                    <td style={s.td}>{e.balance != null ? '₹' + Number(e.balance).toFixed(2) : '—'}</td>
                  </tr>
                );
              })}</tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default LedgerPage;
