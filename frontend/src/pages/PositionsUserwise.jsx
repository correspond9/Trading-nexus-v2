import React, { useState, useEffect, useCallback } from "react";
import { apiService } from '../services/apiService';

// ── helpers ───────────────────────────────────────────────────────────────
const INR = (n) =>
  (Number(n) < 0 ? "-₹" : "₹") +
  Math.abs(Number(n)).toLocaleString("en-IN", { maximumFractionDigits: 2 });

const PCT = (n) => (Number(n) >= 0 ? "" : "") + Number(n).toFixed(2) + "%";

const numColor = (n) =>
  Number(n) > 0 ? "#22c55e" : Number(n) < 0 ? "#ef4444" : "#f4f4f5";

// ── styles ────────────────────────────────────────────────────────────────
const TH = {
  padding: "9px 11px",
  background: "#1c1c1f",
  borderBottom: "1px solid #3f3f46",
  fontWeight: 700,
  fontSize: "10px",
  color: "#a1a1aa",
  textTransform: "uppercase",
  whiteSpace: "nowrap",
  cursor: "pointer",
  userSelect: "none",
};
const TD = {
  padding: "9px 11px",
  borderBottom: "1px solid #27272a",
  fontSize: "12px",
  color: "#f4f4f5",
  whiteSpace: "nowrap",
};
const SUB_TH = {
  padding: "7px 10px",
  background: "var(--surface2)",
  borderBottom: "1px solid var(--border)",
  fontWeight: 600,
  fontSize: "10px",
  color: "var(--muted)",
  textTransform: "uppercase",
  whiteSpace: "nowrap",
};
const SUB_TD = {
  padding: "7px 10px",
  borderBottom: "1px solid #27272a",
  fontSize: "12px",
  color: "#f4f4f5",
  whiteSpace: "nowrap",
};

// ── sort helpers ──────────────────────────────────────────────────────────
const SORT_FIELDS = {
  "UserId(asc)":   { key: "user_no",   dir: 1  },
  "UserId(desc)":  { key: "user_no",   dir: -1 },
  "Profit(asc)":   { key: "profit",    dir: 1  },
  "Profit(desc)":  { key: "profit",    dir: -1 },
  "PandL(asc)":    { key: "pandl",     dir: 1  },
  "PandL(desc)":   { key: "pandl",     dir: -1 },
  "Fund(asc)":     { key: "fund",      dir: 1  },
  "Fund(desc)":    { key: "fund",      dir: -1 },
};

function sortRows(rows, sortLabel) {
  const cfg = SORT_FIELDS[sortLabel] || SORT_FIELDS["UserId(asc)"];
  return [...rows].sort((a, b) => {
    const av = a[cfg.key] ?? 0;
    const bv = b[cfg.key] ?? 0;
    return cfg.dir * (Number(av) - Number(bv));
  });
}

// ── Position sub-table for one user ───────────────────────────────────────
function UserPositions({ row, onExitDone }) {
  const [checked,  setChecked]  = useState({});  // instrument_token -> bool
  const [exitQty,  setExitQty]  = useState({});  // instrument_token -> qty string
  const [exiting,  setExiting]  = useState(false);

  const openPositions = (row.positions || []).filter(p => p.status === "OPEN");
  const allOpen       = openPositions.map(p => p.instrument_token);
  const anyChecked    = allOpen.some(t => checked[t]);

  const toggleAll = (e) => {
    const val = e.target.checked;
    const next = {};
    allOpen.forEach(t => { next[t] = val; });
    setChecked(next);
  };

  const toggle = (token) =>
    setChecked(prev => ({ ...prev, [token]: !prev[token] }));

  const handleExitSelected = async () => {
    const targets = allOpen.filter(t => checked[t]);
    if (!targets.length) return;
    setExiting(true);
    try {
      await Promise.all(
        targets.map(token =>
          apiService.post(`/portfolio/positions/${token}/close?user_id=${row.user_id}`, {})
        )
      );
      setChecked({});
      if (onExitDone) onExitDone();
    } catch (err) {
      alert(err?.response?.data?.detail || "Failed to exit position(s).");
    } finally {
      setExiting(false);
    }
  };

  return (
    <div style={{ padding: "14px 18px", background: "var(--surface)" }}>
      {/* Panel header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
        <span style={{ fontSize: "13px", fontWeight: 700, color: "var(--text)" }}>
          Positions for{" "}
          <span style={{ color: "#60a5fa" }}>{row.display_name}</span>
          {" "}(User ID: {row.user_no || row.user_id?.slice(0, 8)})
        </span>
        <button
          disabled={!anyChecked || exiting}
          onClick={handleExitSelected}
          style={{
            padding: "7px 18px",
            borderRadius: "6px",
            border: "none",
            background: anyChecked ? "#dc2626" : "#3f3f46",
            color: "#fff",
            fontWeight: 700,
            fontSize: "12px",
            cursor: anyChecked ? "pointer" : "not-allowed",
            opacity: exiting ? 0.6 : 1,
          }}
        >
          {exiting ? "Exiting…" : "EXIT Selected"}
        </button>
      </div>

      {/* Sub-table */}
      <div style={{ overflowX: "auto", borderRadius: "6px", border: "1px solid #3f3f46" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={SUB_TH}>
                <input
                  type="checkbox"
                  onChange={toggleAll}
                  checked={allOpen.length > 0 && allOpen.every(t => checked[t])}
                  style={{ accentColor: "#2563eb" }}
                />
              </th>
              {["Symbol","Exchange","Product","Quantity","Avg Price","LTP","P&L","Exit Qty","Type"].map(h => (
                <th key={h} style={SUB_TH}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(row.positions || []).length === 0 ? (
              <tr>
                <td colSpan={10} style={{ ...SUB_TD, textAlign: "center", color: "#a1a1aa", padding: "20px" }}>
                  No positions today.
                </td>
              </tr>
            ) : (row.positions || []).map(p => {
              const isOpen  = p.status === "OPEN";
              const token   = p.instrument_token;
              const curQty  = exitQty[token] ?? String(Math.abs(p.quantity));
              return (
                <tr key={token} style={{ background: checked[token] ? "#1e3a5f22" : "transparent" }}>
                  <td style={SUB_TD}>
                    {isOpen ? (
                      <input
                        type="checkbox"
                        checked={!!checked[token]}
                        onChange={() => toggle(token)}
                        style={{ accentColor: "#2563eb" }}
                      />
                    ) : null}
                  </td>
                  <td style={{ ...SUB_TD, fontWeight: 700 }}>{p.symbol || "—"}</td>
                  <td style={{ ...SUB_TD, color: "#a1a1aa" }}>{p.exchange || "—"}</td>
                  <td style={SUB_TD}>
                    <span style={{
                      padding: "2px 8px", borderRadius: "999px", fontSize: "10px",
                      fontWeight: 700, color: "#fff",
                      background: p.product_type === "NORMAL" ? "#1d4ed8" : "#7c3aed",
                    }}>
                      {p.product_type || "MIS"}
                    </span>
                  </td>
                  <td style={{ ...SUB_TD, fontVariantNumeric: "tabular-nums" }}>{p.quantity}</td>
                  <td style={{ ...SUB_TD, fontVariantNumeric: "tabular-nums" }}>{INR(p.avg_price)}</td>
                  <td style={{ ...SUB_TD, fontVariantNumeric: "tabular-nums" }}>{INR(p.ltp)}</td>
                  <td style={{ ...SUB_TD, fontVariantNumeric: "tabular-nums", color: numColor(p.pnl) }}>
                    {INR(p.pnl)}
                  </td>
                  <td style={SUB_TD}>
                    {isOpen ? (
                      <input
                        type="number"
                        min={1}
                        max={Math.abs(p.quantity)}
                        value={curQty}
                        onChange={e => setExitQty(prev => ({ ...prev, [token]: e.target.value }))}
                        style={{
                          width: "72px", padding: "4px 6px",
                          background: "#09090b", border: "1px solid #3f3f46",
                          borderRadius: "4px", color: "#f4f4f5", fontSize: "12px",
                        }}
                      />
                    ) : (
                      <span style={{ color: "#a1a1aa" }}>—</span>
                    )}
                  </td>
                  <td style={SUB_TD}>
                    <span style={{
                      padding: "2px 8px", borderRadius: "999px", fontSize: "10px", fontWeight: 700,
                      color:       isOpen ? "#22c55e"  : "#a1a1aa",
                      background:  isOpen ? "#14532d33" : "#3f3f4622",
                      border: `1px solid ${isOpen ? "#22c55e44" : "#a1a1aa44"}`,
                    }}>
                      {p.status}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ── Main component ─────────────────────────────────────────────────────────
const PositionsUserwise = () => {
  const [rows,       setRows]       = useState([]);
  const [loading,    setLoading]    = useState(true);
  const [sortLabel,  setSortLabel]  = useState("UserId(asc)");
  const [expandedId, setExpandedId] = useState(null); // user_id or null

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiService.get('/admin/positions/userwise');
      setRows(res?.data?.data || res?.data || []);
    } catch { setRows([]); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const sorted      = sortRows(rows, sortLabel);
  const toggleExpand = (uid) => setExpandedId(prev => prev === uid ? null : uid);

  const SortTH = ({ children, field }) => (
    <th style={TH} title={`Sort by ${field}`}>
      {children}
    </th>
  );

  return (
    <div style={{ padding: "24px", fontFamily: "system-ui,sans-serif", color: "#f4f4f5", minHeight: "100vh" }}>

      {/* Top bar */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <h1 style={{ fontSize: "20px", fontWeight: 700, margin: 0, color: "#f4f4f5" }}>
          All Positions Userwise
        </h1>
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          {/* Refresh */}
          <button
            onClick={load}
            title="Refresh"
            style={{
              width: "36px", height: "36px", borderRadius: "50%", border: "none",
              background: "#2563eb", color: "#fff", fontSize: "16px", cursor: "pointer",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}
          >
            ↺
          </button>
          {/* Sort */}
          <select
            value={sortLabel}
            onChange={e => setSortLabel(e.target.value)}
            style={{
              padding: "7px 10px", background: "var(--surface2)", border: "1px solid var(--border)",
              borderRadius: "6px", color: "var(--text)", fontSize: "13px", cursor: "pointer",
            }}
          >
            {Object.keys(SORT_FIELDS).map(l => <option key={l}>{l}</option>)}
          </select>
        </div>
      </div>

      {/* Main table */}
      <div style={{ background: "var(--surface)", borderRadius: "10px", border: "1px solid var(--border)", overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={TH}>User ID</th>
              <th style={TH}>Profit</th>
              <th style={TH}>S/L</th>
              <th style={TH}>Trial By</th>
              <th style={TH}>Trial After</th>
              <th style={TH}>Fund</th>
              <th style={TH}>Margin Allotted</th>
              <th style={TH}>Current Margin Usage</th>
              <th style={TH}>PandL</th>
              <th style={TH}>PandL %</th>
              <th style={{ ...TH, cursor: "default" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={11} style={{ ...TD, textAlign: "center", color: "#a1a1aa", padding: "40px" }}>Loading…</td></tr>
            ) : sorted.length === 0 ? (
              <tr><td colSpan={11} style={{ ...TD, textAlign: "center", color: "#a1a1aa", padding: "40px" }}>No data.</td></tr>
            ) : sorted.map(r => {
              const isExpanded = expandedId === r.user_id;
              return (
                <React.Fragment key={r.user_id}>
                  {/* Summary row */}
                  <tr style={{ background: isExpanded ? "#1e2a3a" : "transparent" }}>
                    <td style={{ ...TD, fontWeight: 700, color: "#60a5fa" }}>
                      {r.user_no || r.user_id?.slice(0, 8)}
                    </td>
                    <td style={{ ...TD, color: numColor(r.profit) }}>
                      {INR(r.profit)}
                    </td>
                    <td style={{ ...TD, color: "#a1a1aa" }}>
                      {INR(r.stop_loss)}
                    </td>
                    <td style={{ ...TD, color: numColor(r.trial_by), fontVariantNumeric: "tabular-nums" }}>
                      {INR(r.trial_by)}
                    </td>
                    <td style={{ ...TD, color: numColor(r.trial_after), fontVariantNumeric: "tabular-nums" }}>
                      {INR(r.trial_after)}
                    </td>
                    <td style={{ ...TD, color: numColor(r.fund), fontVariantNumeric: "tabular-nums" }}>
                      {INR(r.fund)}
                    </td>
                    <td style={{ ...TD, color: numColor(r.margin_allotted), fontVariantNumeric: "tabular-nums" }}>
                      {INR(r.margin_allotted)}
                    </td>
                    <td style={{ ...TD, fontVariantNumeric: "tabular-nums" }}>
                      {INR(r.current_margin_usage)}
                    </td>
                    <td style={{ ...TD, color: numColor(r.pandl), fontVariantNumeric: "tabular-nums" }}>
                      {INR(r.pandl)}
                    </td>
                    <td style={{ ...TD, color: numColor(r.pandl_pct), fontVariantNumeric: "tabular-nums" }}>
                      {PCT(r.pandl_pct)}
                    </td>
                    <td style={TD}>
                      <button
                        onClick={() => toggleExpand(r.user_id)}
                        style={{
                          padding: "5px 16px", borderRadius: "999px", border: "none",
                          background: isExpanded ? "#374151" : "#2563eb",
                          color: "#fff", fontWeight: 700, fontSize: "12px", cursor: "pointer",
                          minWidth: "60px",
                        }}
                      >
                        {isExpanded ? "Hide" : "View"}
                      </button>
                    </td>
                  </tr>

                  {/* Expanded positions row */}
                  {isExpanded && (
                    <tr>
                      <td
                        colSpan={11}
                        style={{ padding: 0, borderBottom: "2px solid #2563eb" }}
                      >
                        <UserPositions row={r} onExitDone={load} />
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Footer note */}
      <div style={{ marginTop: "10px", fontSize: "11px", color: "#52525b" }}>
        Closed positions shown only for today (IST). Carried-over NORMAL positions always shown.
      </div>
    </div>
  );
};

export default PositionsUserwise;
