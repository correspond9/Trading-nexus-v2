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
        fetch(`${API_BASE}/admin/notifications`),
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
      {notifications.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
            <AlertCircle size={14} />
            Admin Alerts ({notifications.length})
          </h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {notifications.map((notif, idx) => (
              <div
                key={notif.id || idx}
                className={`flex items-start gap-2 rounded-lg p-3 text-xs border ${
                  notif.level === 'error' ? 'bg-red-900/30 border-red-700/50 text-red-300' :
                  notif.level === 'warning' ? 'bg-yellow-900/30 border-yellow-700/50 text-yellow-300' :
                  'bg-blue-900/30 border-blue-700/50 text-blue-300'
                }`}
              >
                <AlertCircle size={13} className="flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-medium">{notif.title || notif.message}</div>
                  {notif.title && notif.message && (
                    <div className="opacity-80 mt-0.5">{notif.message}</div>
                  )}
                  {notif.created_at && (
                    <div className="opacity-50 mt-1">{new Date(notif.created_at).toLocaleString()}</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SystemMonitoring;
