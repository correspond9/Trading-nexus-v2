import React, { useState, useEffect, useCallback } from 'react';
import { Activity, Database, Server, Wifi, WifiOff, AlertCircle, RefreshCw } from 'lucide-react';
import LiveQuotes from './LiveQuotes';

const API_BASE = '/api/v2';

const StatusBadge = ({ status }) => {
  const map = {
    ok: 'bg-green-500',
    healthy: 'bg-green-500',
    connected: 'bg-green-500',
    active: 'bg-green-500',
    open: 'bg-green-500',
    error: 'bg-red-500',
    disconnected: 'bg-red-500',
    closed: 'bg-red-500',
    degraded: 'bg-yellow-500',
    unknown: 'bg-gray-400',
  };
  const color = map[(status || '').toLowerCase()] || 'bg-gray-400';
  return (
    <span className={`inline-block w-2.5 h-2.5 rounded-full ${color} flex-shrink-0`} title={status} />
  );
};

const StatusCard = ({ title, status, detail, icon: Icon }) => (
  <div className="rounded-xl p-4 flex flex-col gap-1 bg-zinc-800 border border-zinc-700">
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2 text-xs tn-muted">
        {Icon && <Icon size={13} />}
        <span>{title}</span>
      </div>
      <StatusBadge status={status} />
    </div>
    <div className="text-sm font-semibold capitalize">{status || '—'}</div>
    {detail && <div className="text-xs truncate tn-muted">{detail}</div>}
  </div>
);

const SeverityPill = ({ level }) => {
  const lvl = (level || "info").toLowerCase();
  const style = {
    error: "bg-red-500/15 text-red-200 border border-red-500/30",
    critical: "bg-red-500/20 text-red-100 border border-red-500/40",
    warning: "bg-yellow-500/15 text-yellow-200 border border-yellow-500/30",
    warn: "bg-yellow-500/15 text-yellow-200 border border-yellow-500/30",
    info: "bg-blue-500/10 text-blue-200 border border-blue-500/25",
  }[lvl] || "bg-zinc-700/30 text-zinc-100 border border-zinc-600/40";
  return (
    <span className={`text-[11px] font-semibold px-2 py-1 rounded-md uppercase tracking-wide ${style}`}>
      {lvl.toUpperCase()}
    </span>
  );
};

const formatWhen = (ts) => {
  if (!ts) return "";
  try {
    return new Date(ts).toLocaleString();
  } catch (err) {
    return ts;
  }
};

const SystemMonitoring = () => {
  const [health, setHealth] = useState(null);
  const [streamStatus, setStreamStatus] = useState(null);
  const [etfStatus, setEtfStatus] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reconnecting, setReconnecting] = useState(false);
  const [lastRefreshed, setLastRefreshed] = useState(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [healthRes, streamRes, etfRes, notifRes] = await Promise.allSettled([
        fetch(`${API_BASE}/health`),
        fetch(`${API_BASE}/market/stream-status`),
        fetch(`${API_BASE}/market/etf-tierb-status`),
        fetch(`${API_BASE}/admin/notifications?limit=20`),
      ]);

      if (healthRes.status === 'fulfilled' && healthRes.value.ok)
        setHealth(await healthRes.value.json());
      else
        setHealth(null);

      if (streamRes.status === 'fulfilled' && streamRes.value.ok)
        setStreamStatus(await streamRes.value.json());
      else
        setStreamStatus(null);

      if (etfRes.status === 'fulfilled' && etfRes.value.ok)
        setEtfStatus(await etfRes.value.json());
      else
        setEtfStatus(null);

      if (notifRes.status === 'fulfilled' && notifRes.value.ok)
        setNotifications(await notifRes.value.json());
      else
        setNotifications([]);

      setLastRefreshed(new Date());
    } catch (err) {
      console.error('SystemMonitoring fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 30000);
    return () => clearInterval(interval);
  }, [fetchAll]);

  const handleReconnect = async () => {
    setReconnecting(true);
    try {
      const res = await fetch(`${API_BASE}/market/stream-reconnect`, { method: 'POST' });
      if (res.ok) {
        setTimeout(fetchAll, 2000);
      }
    } catch (err) {
      console.error('Reconnect error:', err);
    } finally {
      setReconnecting(false);
    }
  };

  const dbStatus = health?.database || health?.db || 'unknown';
  const apiStatus = health?.status || 'unknown';
  const dhanStatus = health?.dhan_api || health?.dhan || 'unknown';
  const equityWsStatus = streamStatus?.equity?.status || streamStatus?.nse_ws || 'unknown';
  const mcxWsStatus = streamStatus?.mcx?.status || streamStatus?.mcx_ws || 'unknown';
  const etfTierbStatus = etfStatus?.status || 'unknown';
  const marketSession = streamStatus?.market_session || health?.market_session || 'unknown';

  const statusCards = [
    { title: 'Database', status: dbStatus, icon: Database },
    { title: 'API Server', status: apiStatus, detail: health?.version, icon: Server },
    { title: 'Dhan API', status: dhanStatus, icon: Activity },
    { title: 'Equity WS', status: equityWsStatus, detail: streamStatus?.equity?.subscriptions ? `${streamStatus.equity.subscriptions} subs` : undefined, icon: Wifi },
    { title: 'MCX WS', status: mcxWsStatus, icon: Wifi },
    { title: 'ETF Tier-B', status: etfTierbStatus, icon: Activity },
    { title: 'Market Session', status: marketSession, icon: Activity },
  ];

  return (
    <div className="space-y-4">
      {/* Live Quotes */}
      <LiveQuotes />

      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          <Activity size={15} />
          System Status
        </h3>
        <div className="flex items-center gap-2">
          {lastRefreshed && (
            <span className="text-xs tn-muted">
              Updated {lastRefreshed.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={fetchAll}
            disabled={loading}
            className="p-1.5 rounded transition-colors disabled:opacity-50 bg-zinc-900 border border-zinc-700"
            title="Refresh"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {statusCards.map((card) => (
          <StatusCard key={card.title} {...card} />
        ))}
      </div>

      {/* Reconnect */}
      {(equityWsStatus === 'disconnected' || mcxWsStatus === 'disconnected') && (
        <div className="flex items-center gap-3 bg-yellow-900/30 border border-yellow-700/50 rounded-lg p-3">
          <WifiOff size={16} className="text-yellow-400 flex-shrink-0" />
          <span className="text-xs text-yellow-300 flex-1">WebSocket disconnected. Streams may be stale.</span>
          <button
            onClick={handleReconnect}
            disabled={reconnecting}
            className="flex items-center gap-1 px-3 py-1.5 bg-yellow-500 text-black rounded text-xs font-medium hover:bg-yellow-400 transition-colors disabled:opacity-50"
          >
            <RefreshCw size={11} className={reconnecting ? 'animate-spin' : ''} />
            {reconnecting ? 'Reconnecting...' : 'Reconnect'}
          </button>
        </div>
      )}

      {/* Admin Alerts */}
      <div className="rounded-xl p-4 border border-zinc-700 bg-zinc-800">
        <div className="flex items-center justify-between gap-2 mb-2">
          <h3 className="text-sm font-semibold flex items-center gap-2">
            <AlertCircle size={14} />
            Admin Alerts
          </h3>
          <span className="text-[11px] text-zinc-400">
            {notifications.length ? `Last ${notifications.length}` : "No recent alerts"}
          </span>
        </div>

        <div className="space-y-2 max-h-72 overflow-y-auto">
          {notifications.length === 0 && (
            <div className="text-xs text-zinc-500">No alerts yet. Background tasks look clean.</div>
          )}

          {notifications.map((notif, idx) => (
            <div
              key={notif.id || idx}
              className="flex items-start gap-3 rounded-lg p-3 text-xs bg-zinc-900/60 border border-zinc-700"
            >
              <SeverityPill level={notif.severity || notif.level} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-3">
                  <div className="font-semibold text-zinc-100 truncate">{notif.title || notif.message}</div>
                  {notif.created_at && (
                    <span className="text-[11px] text-zinc-500 whitespace-nowrap">{formatWhen(notif.created_at)}</span>
                  )}
                </div>
                {notif.title && notif.message && (
                  <div className="text-[12px] text-zinc-200 mt-1 leading-relaxed">
                    {notif.message}
                  </div>
                )}
                {notif.category && (
                  <div className="text-[10px] text-zinc-500 mt-1 uppercase tracking-wide">{notif.category}</div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SystemMonitoring;
