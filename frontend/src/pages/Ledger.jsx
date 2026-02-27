import React, { useState, useEffect } from "react";
import { apiService } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';

const today = () => new Date().toLocaleDateString("en-CA"); // YYYY-MM-DD

const LedgerPage = () => {
  const { user } = useAuth();
  const [isMobile, setIsMobile] = useState(() => window.innerWidth <= 900);
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fromDate, setFromDate] = useState(today());
  const [toDate, setToDate] = useState(today());

  const fetchLedger = async () => {
    setLoading(true);
    try {
      const params = user?.id ? { user_id: String(user.id), from_date: fromDate, to_date: toDate } : {};
      const res = await apiService.get('/ledger', params);
      setEntries(res?.data || []);
    } catch (err) {
      console.error('Error fetching ledger:', err);
      setEntries([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLedger();
    // eslint-disable-next-line
  }, [user]);

  useEffect(() => {
    const onResize = () => setIsMobile(window.innerWidth <= 900);
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  const s = {
    page: { padding: isMobile ? '12px' : '24px', fontFamily: 'system-ui,sans-serif', color: 'var(--text)' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' },
    title: { fontSize: '20px', fontWeight: 700, margin: 0, color: 'var(--text)' },
    filterBar: { display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' },
    input: { padding: '7px 10px', background: '#09090b', border: '1px solid #3f3f46', borderRadius: '6px', color: '#f4f4f5', fontSize: '13px' },
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
            <table style={{ width: '100%', minWidth: '720px', borderCollapse: 'collapse' }}>
              <thead><tr>{['Date', 'Description', 'Debit', 'Credit', 'Balance'].map(h => <th key={h} style={s.th}>{h}</th>)}</tr></thead>
              <tbody>{entries.map((e, i) => <tr key={i}>{[e.date, e.description, e.debit != null ? '₹' + Number(e.debit).toFixed(2) : '—', e.credit != null ? '₹' + Number(e.credit).toFixed(2) : '—', e.balance != null ? '₹' + Number(e.balance).toFixed(2) : '—'].map((v, j) => <td key={j} style={s.td}>{v}</td>)}</tr>)}</tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default LedgerPage;
