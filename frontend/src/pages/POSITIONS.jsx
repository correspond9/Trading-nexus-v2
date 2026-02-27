import React, { useState, useEffect, useCallback } from "react";
import { apiService } from '../services/apiService';
import { useMarketPulse } from '../hooks/useMarketPulse';

const isDerivativePosition = (position = {}) => {
  const exchange = String(position.exchange || '').toUpperCase();
  const symbol = String(position.symbol || '').toUpperCase();

  const isExplicitEquity =
    exchange === 'NSE_EQ' ||
    exchange === 'BSE_EQ' ||
    (exchange === 'NSE' && !symbol.endsWith('CE') && !symbol.endsWith('PE') && !symbol.includes('FUT')) ||
    (exchange === 'BSE' && !symbol.endsWith('CE') && !symbol.endsWith('PE') && !symbol.includes('FUT'));

  if (isExplicitEquity) return false;

  return (
    exchange.includes('FNO') ||
    exchange.includes('FO') ||
    exchange.includes('OPT') ||
    exchange.includes('FUT') ||
    exchange.includes('COMM') ||
    symbol.endsWith('CE') ||
    symbol.endsWith('PE') ||
    symbol.includes('FUT')
  );
};

const PositionsTab = ({ productFilter = "MIS" }) => {
  const { pulse, marketActive } = useMarketPulse();
  const [positions, setPositions] = useState([]);
  const [selectedOpenIds, setSelectedOpenIds] = useState(new Set());

  const fetchPositions = useCallback(async () => {
    try {
      const res = await apiService.get('/admin/positions/userwise');
      const users = res?.data?.data || res?.data || [];

      const normalizedFilter = String(productFilter || 'MIS').toUpperCase();
      const mapped = [];

      users.forEach((userRow) => {
        const userId = String(userRow.user_id || '');
        const userNo = userRow.user_no;
        const userName = userRow.display_name || userRow.mobile || userId;

        (userRow.positions || []).forEach((position, index) => {
          const positionProduct = String(position.product_type || 'MIS').toUpperCase();
          if (positionProduct !== normalizedFilter) return;
          if (!isDerivativePosition(position)) return;

          const status = String(position.status || 'OPEN').toUpperCase();
          if (status !== 'OPEN' && status !== 'CLOSED') return;

          const qty = Number(position.quantity || 0);
          const avgEntry = Number(position.avg_price || 0);
          const currentLtp = Number(position.ltp || avgEntry);
          const pnl = Number(position.pnl || 0);
          const token = Number(position.instrument_token || 0);

          mapped.push({
            id: `${userId}:${token}:${position.opened_at || index}:${status}`,
            positionToken: token,
            userId,
            userNo,
            userName,
            productType: positionProduct,
            symbol: position.symbol || '—',
            qty,
            avgEntry: avgEntry.toFixed ? avgEntry.toFixed(2) : avgEntry,
            currentLtp: currentLtp.toFixed ? currentLtp.toFixed(2) : currentLtp,
            mtm: status === 'OPEN' ? pnl : 0,
            realizedPnl: status === 'CLOSED' ? pnl : 0,
            status,
          });
        });
      });

        setPositions(mapped);
    } catch (err) { console.error('Error fetching positions:', err); }
  }, [productFilter]);

  useEffect(() => { fetchPositions(); }, [fetchPositions]);

  useEffect(() => {
    const handlePositionsUpdated = () => fetchPositions();
    window.addEventListener('positions:updated', handlePositionsUpdated);
    return () => window.removeEventListener('positions:updated', handlePositionsUpdated);
  }, [fetchPositions]);

  useEffect(() => {
    if (!marketActive || !pulse?.timestamp) return;
    fetchPositions();
  }, [pulse?.timestamp, marketActive, fetchPositions]);

  const openPositions = positions.filter((p) => p.status === "OPEN");
  const closedPositions = positions.filter((p) => p.status === "CLOSED");
  const totalMtm = openPositions.reduce((sum, p) => sum + parseFloat(p.mtm), 0);
  const totalClosed = closedPositions.reduce((sum, p) => sum + p.realizedPnl, 0);

  const toggleSelectOne = (id) => {
    setSelectedOpenIds((prev) => { const next = new Set(prev); if (next.has(id)) next.delete(id); else next.add(id); return next; });
  };
  const toggleSelectAllOpen = () => {
    setSelectedOpenIds((prev) => prev.size === openPositions.length ? new Set() : new Set(openPositions.map((p) => p.id)));
  };
  const handleExitOne = (id) => exitPositions(new Set([id]));
  const handleExitSelected = () => { if (!selectedOpenIds.size) return; exitPositions(selectedOpenIds); };

  const exitPositions = async (idsSet) => {
    try {
      const selectedRows = openPositions.filter((p) => idsSet.has(p.id));
      for (const id of idsSet) {
        const row = selectedRows.find((p) => p.id === id);
        if (!row?.positionToken || !row?.userId) continue;
        await apiService.post(`/portfolio/positions/${row.positionToken}/close?user_id=${row.userId}`, {});
      }
      await new Promise(resolve => setTimeout(resolve, 1000));
      await fetchPositions();
      setSelectedOpenIds(new Set());
    } catch (err) {
      console.error('Error exiting positions:', err);
      const errorMsg = err?.data?.detail || err?.message || 'Failed to close position';
      alert(`❌ Position Exit Failed\n\n${errorMsg}\n\nPlease try again or contact support if the issue persists.`);
      await fetchPositions(); // Refresh to show actual state
      setSelectedOpenIds(new Set());
    }
  };

  // styles
  const pageStyle = { minHeight: "100vh", margin: 0, padding: "24px", fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", background: "transparent" };
  const mainCardStyle = { maxWidth: "1200px", margin: "0 auto", background: "var(--surface)", borderRadius: "12px", boxShadow: "0 10px 30px rgba(0,0,0,0.3)", padding: "24px 24px 32px 24px", border: "1px solid var(--border)" };
  const sectionHeaderRowStyle = { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px", marginTop: "8px" };
  const sectionTitleStyle = { fontSize: "14px", fontWeight: 600, color: "var(--text)" };
  const totalTextStyle = { fontSize: "13px", fontWeight: 600, color: "var(--text)" };
  const totalValueStyle = { fontWeight: 700 };
  const tableOuterStyle = { borderRadius: "8px", border: "1px solid var(--border)", overflow: "hidden", background: "var(--surface)" };
  const tableStyle = { width: "100%", borderCollapse: "collapse", fontSize: "12px" };
  const theadStyle = { background: "var(--surface2)", borderBottom: "1px solid var(--border)" };
  const thStyle = { padding: "10px 12px", textAlign: "left", fontWeight: 600, color: "var(--muted)", whiteSpace: "nowrap" };
  const thRight = { ...thStyle, textAlign: "right" };
  const rowStyle = { borderBottom: "1px solid var(--border)", background: "var(--surface)" };
  const tdStyle = { padding: "10px 12px", color: "var(--text)", verticalAlign: "middle", whiteSpace: "nowrap" };
  const tdRight = { ...tdStyle, textAlign: "right" };
  const checkboxStyle = { width: 14, height: 14 };
  const exitButtonStyle = { border: "1px solid var(--border)", borderRadius: "6px", padding: "4px 12px", fontSize: "12px", background: "var(--surface2)", color: "var(--text)", cursor: "pointer" };
  const exitSelectedButtonStyle = { border: "1px solid var(--border)", borderRadius: "6px", padding: "4px 12px", fontSize: "12px", background: selectedOpenIds.size ? "#f97316" : "var(--surface2)", color: selectedOpenIds.size ? "#ffffff" : "var(--muted)", cursor: selectedOpenIds.size ? "pointer" : "default" };
  const qtyTextStyle = { fontVariantNumeric: "tabular-nums" };
  const plPositive = { color: "#22c55e" };
  const plNegative = { color: "#ef4444" };
  const totalRowStyle = { ...rowStyle, background: "var(--surface2)", fontWeight: 600 };

  const formatMoney = (v) => "₹" + Math.abs(v).toLocaleString("en-IN", { maximumFractionDigits: 2 });

  return (
    <div style={pageStyle}>
      <div style={mainCardStyle}>
        <div style={sectionHeaderRowStyle}>
          <div style={{ ...sectionTitleStyle, display: 'flex', alignItems: 'center', gap: '8px' }}>
            Open {productFilter} Derivatives Positions ({openPositions.length})
            <button onClick={fetchPositions} style={{ background: 'none', border: '1px solid #d1d5db', borderRadius: '4px', padding: '4px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }} title="Refresh positions">
              <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
            </button>
          </div>
          <div style={totalTextStyle}>
            Total MTM:{" "}
            <span style={{ ...totalValueStyle, ...(totalMtm >= 0 ? plPositive : plNegative) }}>
              {formatMoney(totalMtm)}
            </span>
          </div>
        </div>

        <div style={tableOuterStyle}>
          <table style={tableStyle}>
            <thead style={theadStyle}>
              <tr>
                <th style={thStyle}><input type="checkbox" style={checkboxStyle} checked={openPositions.length > 0 && selectedOpenIds.size === openPositions.length} onChange={toggleSelectAllOpen} /></th>
                <th style={thStyle}>Product</th>
                <th style={thStyle}>User</th>
                <th style={thStyle}>Instrument</th>
                <th style={thRight}>Qty.</th>
                <th style={thRight}>Avg.</th>
                <th style={thRight}>LTP</th>
                <th style={thRight}>P&L</th>
                <th style={{ ...thRight }}><button style={exitSelectedButtonStyle} onClick={handleExitSelected}>Exit Selected</button></th>
              </tr>
            </thead>
            <tbody>
              {openPositions.length === 0 ? (
                <tr><td style={tdStyle} colSpan={9}>No open positions.</td></tr>
              ) : (
                <>
                  {openPositions.map((p) => (
                    <tr key={p.id} style={rowStyle}>
                      <td style={tdStyle}><input type="checkbox" style={checkboxStyle} checked={selectedOpenIds.has(p.id)} onChange={() => toggleSelectOne(p.id)} /></td>
                      <td style={tdStyle}>{p.productType}</td>
                      <td style={tdStyle}>{p.userName} ({p.userNo || '—'})</td>
                      <td style={tdStyle}>{p.symbol}</td>
                      <td style={{ ...tdRight, ...qtyTextStyle }}>{p.qty.toLocaleString("en-IN")}</td>
                      <td style={tdRight}>{p.avgEntry}</td>
                      <td style={tdRight}>{p.currentLtp}</td>
                      <td style={{ ...tdRight, ...(parseFloat(p.mtm) >= 0 ? plPositive : plNegative) }}>{formatMoney(parseFloat(p.mtm))}</td>
                      <td style={{ ...tdStyle }}><button style={exitButtonStyle} onClick={() => handleExitOne(p.id)}>Exit</button></td>
                    </tr>
                  ))}
                  <tr style={totalRowStyle}>
                    <td style={tdStyle}></td><td style={tdStyle}></td><td style={tdStyle}></td><td style={tdStyle}></td>
                    <td style={tdRight}></td><td style={tdRight}></td>
                    <td style={{ ...tdRight, color: "#111827" }}>Total</td>
                    <td style={{ ...tdRight, ...(totalMtm >= 0 ? plPositive : plNegative) }}>{formatMoney(totalMtm)}</td>
                    <td style={tdStyle}></td>
                  </tr>
                </>
              )}
            </tbody>
          </table>
        </div>

        <div style={{ ...sectionHeaderRowStyle, marginTop: "24px" }}>
          <div style={sectionTitleStyle}>Intraday Closed {productFilter} Derivatives Positions ({closedPositions.length})</div>
        </div>

        <div style={tableOuterStyle}>
          <table style={tableStyle}>
            <thead style={theadStyle}>
              <tr>
                <th style={thStyle}><input type="checkbox" style={checkboxStyle} disabled /></th>
                <th style={thStyle}>Product</th>
                <th style={thStyle}>User</th>
                <th style={thStyle}>Instrument</th>
                <th style={thRight}>Qty.</th>
                <th style={thRight}>Avg.</th>
                <th style={thRight}>LTP</th>
                <th style={thRight}>P&L</th>
              </tr>
            </thead>
            <tbody>
              {closedPositions.length === 0 ? (
                <tr><td style={tdStyle} colSpan={8}>No intraday closed positions yet.</td></tr>
              ) : (
                <>
                  {closedPositions.map((p) => (
                    <tr key={p.id} style={rowStyle}>
                      <td style={tdStyle}><input type="checkbox" style={checkboxStyle} disabled /></td>
                      <td style={tdStyle}>{p.productType}</td>
                      <td style={tdStyle}>{p.userName} ({p.userNo || '—'})</td>
                      <td style={tdStyle}>{p.symbol}</td>
                      <td style={{ ...tdRight, ...qtyTextStyle }}>{p.qty.toLocaleString("en-IN")}</td>
                      <td style={tdRight}>{p.avgEntry}</td>
                      <td style={tdRight}>{p.exitPrice || "0.00"}</td>
                      <td style={{ ...tdRight, ...(p.realizedPnl >= 0 ? plPositive : plNegative) }}>{formatMoney(p.realizedPnl)}</td>
                    </tr>
                  ))}
                  <tr style={totalRowStyle}>
                    <td style={tdStyle}></td><td style={tdStyle}></td><td style={tdStyle}></td>
                    <td style={{ ...tdStyle, color: "#111827" }}>Total</td>
                    <td style={tdRight}></td><td style={tdRight}></td><td style={tdRight}></td>
                    <td style={{ ...tdRight, ...(totalClosed >= 0 ? plPositive : plNegative) }}>{formatMoney(totalClosed)}</td>
                  </tr>
                </>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default PositionsTab;
