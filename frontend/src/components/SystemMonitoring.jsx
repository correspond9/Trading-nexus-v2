import React, { useState, useEffect, useCallback } from 'react';
import { Activity, Database, Server, Wifi, WifiOff, AlertCircle, RefreshCw, Play, Square } from 'lucide-react';
import LiveQuotes from './LiveQuotes';

const API_BASE = '/api/v2';

const authFetch = (path, opts = {}) => {
  const token = localStorage.getItem('authToken');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'X-AUTH': token, Authorization: `Bearer ${token}` } : {}),
    ...(opts.headers || {}),
  };
  return fetch(`${API_BASE}${path}`, {
    ...opts,
    headers,
    credentials: 'include',
  });
};

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
  <div className="rounded-xl p-4 flex flex-col gap-1 sa-card border">
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
    error:    "sa-severity-error",
    critical: "sa-severity-error",
    warning:  "sa-severity-warning",
    warn:     "sa-severity-warning",
    info:     "sa-severity-info",
  }[lvl] || "sa-severity-info";
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

const Sparkline = ({ title, values, colorClass, suffix = '' }) => {
  const safeValues = (values || []).slice(-40);
  const width = 220;
  const height = 60;
  const min = 0;
  const max = Math.max(1, ...safeValues, min);

  const points = safeValues
    .map((v, i) => {
      const x = (i / Math.max(1, safeValues.length - 1)) * width;
      const y = height - ((Math.max(min, v) - min) / (max - min || 1)) * height;
      return `${x},${y}`;
    })
    .join(' ');

  const latest = safeValues.length ? safeValues[safeValues.length - 1] : 0;

  return (
    <div className="rounded-xl p-3 sa-card border">
      <div className="flex items-center justify-between mb-1">
        <div className="text-xs tn-muted">{title}</div>
        <div className="text-xs font-semibold">{latest.toFixed(1)}{suffix}</div>
      </div>
      {safeValues.length > 1 ? (
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-16">
          <polyline
            fill="none"
            strokeWidth="2"
            points={points}
            className={colorClass}
          />
        </svg>
      ) : (
        <div className="h-16 flex items-center text-xs text-zinc-500">No samples yet</div>
      )}
    </div>
  );
};

const SystemMonitoring = () => {
  const [health, setHealth] = useState(null);
  const [streamStatus, setStreamStatus] = useState(null);
  const [etfStatus, setEtfStatus] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reconnecting, setReconnecting] = useState(false);
  const [rollingOver, setRollingOver] = useState(false);
  const [rolloverResult, setRolloverResult] = useState(null);
  const [lastRefreshed, setLastRefreshed] = useState(null);
  const [monitorStatus, setMonitorStatus] = useState(null);
  const [monitorSamples, setMonitorSamples] = useState([]);
  const [monitorBusy, setMonitorBusy] = useState(false);
  const [monitorError, setMonitorError] = useState('');

  const fetchMonitor = useCallback(async () => {
    try {
      const [statusRes, samplesRes] = await Promise.all([
        authFetch('/admin/vps-monitor/status'),
        authFetch('/admin/vps-monitor/samples?limit=120'),
      ]);

      if (statusRes.ok) {
        setMonitorStatus(await statusRes.json());
        setMonitorError('');
      } else {
        setMonitorStatus(null);
        setMonitorError(`Monitor status failed (HTTP ${statusRes.status})`);
      }

      if (samplesRes.ok) {
        const data = await samplesRes.json();
        setMonitorSamples(Array.isArray(data?.samples) ? data.samples : []);
      } else {
        setMonitorSamples([]);
        setMonitorError(`Monitor samples failed (HTTP ${samplesRes.status})`);
      }
    } catch (err) {
      console.error('VPS monitor fetch error:', err);
      setMonitorError(err?.message || 'Failed to fetch monitor data');
    }
  }, []);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [healthRes, streamRes, etfRes, notifRes, monitorStatusRes, monitorSamplesRes] = await Promise.allSettled([
        fetch(`${API_BASE}/health`),
        authFetch('/market/stream-status'),
        authFetch('/market/etf-tierb-status'),
        authFetch('/admin/notifications?limit=100'),
        authFetch('/admin/vps-monitor/status'),
        authFetch('/admin/vps-monitor/samples?limit=120'),
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

      if (monitorStatusRes.status === 'fulfilled' && monitorStatusRes.value.ok)
        setMonitorStatus(await monitorStatusRes.value.json());
      else {
        setMonitorStatus(null);
        if (monitorStatusRes.status === 'fulfilled') {
          setMonitorError(`Monitor status failed (HTTP ${monitorStatusRes.value.status})`);
        }
      }

      if (monitorSamplesRes.status === 'fulfilled' && monitorSamplesRes.value.ok) {
        const data = await monitorSamplesRes.value.json();
        setMonitorSamples(Array.isArray(data?.samples) ? data.samples : []);
      } else {
        setMonitorSamples([]);
        if (monitorSamplesRes.status === 'fulfilled') {
          setMonitorError(`Monitor samples failed (HTTP ${monitorSamplesRes.value.status})`);
        }
      }

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

  useEffect(() => {
    if (!monitorStatus?.running) return undefined;
    const interval = setInterval(fetchMonitor, 5000);
    return () => clearInterval(interval);
  }, [monitorStatus?.running, fetchMonitor]);

  const handleReconnect = async () => {
    setReconnecting(true);
    try {
      const res = await authFetch('/market/stream-reconnect', { method: 'POST' });
      if (res.ok) {
        setTimeout(fetchAll, 2000);
      }
    } catch (err) {
      console.error('Reconnect error:', err);
    } finally {
      setReconnecting(false);
    }
  };

  const handleRollover = async () => {
    setRollingOver(true);
    setRolloverResult(null);
    try {
      const res = await authFetch('/admin/subscriptions/rollover', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setRolloverResult(data);
        setTimeout(fetchAll, 1000);
      } else {
        setRolloverResult({ error: `HTTP ${res.status}` });
      }
    } catch (err) {
      setRolloverResult({ error: err.message });
    } finally {
      setRollingOver(false);
    }
  };

  const handleStartMonitor = async () => {
    setMonitorBusy(true);
    try {
      const res = await authFetch('/admin/vps-monitor/start', {
        method: 'POST',
        body: JSON.stringify({ interval_seconds: 5 }),
      });
      if (res.ok) {
        setMonitorError('');
        await fetchMonitor();
      } else {
        setMonitorError(`Monitor start failed (HTTP ${res.status})`);
      }
    } catch (err) {
      console.error('Start monitor error:', err);
      setMonitorError(err?.message || 'Failed to start monitor');
    } finally {
      setMonitorBusy(false);
    }
  };

  const handleStopMonitor = async () => {
    setMonitorBusy(true);
    try {
      const res = await authFetch('/admin/vps-monitor/stop', { method: 'POST' });
      if (res.ok) {
        setMonitorError('');
        await fetchMonitor();
      } else {
        setMonitorError(`Monitor stop failed (HTTP ${res.status})`);
      }
    } catch (err) {
      console.error('Stop monitor error:', err);
      setMonitorError(err?.message || 'Failed to stop monitor');
    } finally {
      setMonitorBusy(false);
    }
  };

  const dbStatus = health?.database || health?.db || 'unknown';
  const apiStatus = health?.status || 'unknown';
  const dhanStatus = health?.dhan_api || health?.dhan || 'unknown';
  const equityWsStatus = streamStatus?.equity?.status || streamStatus?.nse_ws || 'unknown';
  const mcxWsStatus = streamStatus?.mcx?.status || streamStatus?.mcx_ws || 'unknown';
  const etfTierbStatus = etfStatus?.status || 'unknown';
  const marketSession = streamStatus?.market_session || health?.market_session || 'unknown';
  const latestSample = monitorSamples.length ? monitorSamples[monitorSamples.length - 1] : null;

  const cpuSeries = monitorSamples.map((s) => Number(s.system_cpu_percent || 0));
  const appCpuSeries = monitorSamples.map((s) => Number(s.app_cpu_percent || 0));
  const memSeries = monitorSamples.map((s) => Number(s.memory_used_percent || 0));
  const loadSeries = monitorSamples.map((s) => Number(s.load_1m || 0));

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
            className="p-1.5 rounded transition-colors disabled:opacity-50 sa-nested border"
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

      {/* Admin Actions */}
      <div className="flex flex-wrap items-center gap-2">
        <button
          onClick={handleRollover}
          disabled={rollingOver}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium border transition-colors disabled:opacity-50 sa-input hover:opacity-80"
          title="Unsubscribe expired contracts from Dhan WS and clean up the active subscription map"
        >
          <RefreshCw size={11} className={rollingOver ? 'animate-spin' : ''} />
          {rollingOver ? 'Purging...' : 'Purge Expired Subs'}
        </button>
        {rolloverResult && !rolloverResult.error && (
          <span className="text-xs text-green-400">
            ✓ {rolloverResult.evicted} evicted &nbsp;·&nbsp; {rolloverResult.tokens_before} → {rolloverResult.tokens_after} subs
          </span>
        )}
        {rolloverResult?.error && (
          <span className="text-xs text-red-400">✗ {rolloverResult.error}</span>
        )}
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
      <div className="rounded-xl p-4 border sa-card">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          <div>
            <h3 className="text-sm font-semibold flex items-center gap-2">
              <Activity size={14} />
              VPS Live Monitor
            </h3>
            <div className="text-[11px] text-zinc-400">Manual only. Starts and stops on demand from this panel.</div>
          </div>
          <div className="flex items-center gap-2">
            <span className={`text-xs ${monitorStatus?.running ? 'text-green-400' : 'text-zinc-400'}`}>
              {monitorStatus?.running ? 'Running' : 'Stopped'}
            </span>
            <button
              onClick={handleStartMonitor}
              disabled={monitorBusy || monitorStatus?.running}
              className="flex items-center gap-1 px-3 py-1.5 rounded text-xs font-medium border border-green-700 bg-green-600/20 hover:bg-green-600/30 transition-colors disabled:opacity-50"
            >
              <Play size={11} /> Start
            </button>
            <button
              onClick={handleStopMonitor}
              disabled={monitorBusy || !monitorStatus?.running}
              className="flex items-center gap-1 px-3 py-1.5 rounded text-xs font-medium border border-red-700 bg-red-600/20 hover:bg-red-600/30 transition-colors disabled:opacity-50"
            >
              <Square size={11} /> Stop
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
          <div className="rounded-lg p-3 sa-nested border">
            <div className="text-[11px] text-zinc-400">CPU</div>
            <div className="text-sm font-semibold">{Number(latestSample?.system_cpu_percent || 0).toFixed(1)}%</div>
          </div>
          <div className="rounded-lg p-3 sa-nested border">
            <div className="text-[11px] text-zinc-400">App CPU</div>
            <div className="text-sm font-semibold">{Number(latestSample?.app_cpu_percent || 0).toFixed(1)}%</div>
          </div>
          <div className="rounded-lg p-3 sa-nested border">
            <div className="text-[11px] text-zinc-400">Memory</div>
            <div className="text-sm font-semibold">{Number(latestSample?.memory_used_percent || 0).toFixed(1)}%</div>
          </div>
          <div className="rounded-lg p-3 sa-nested border">
            <div className="text-[11px] text-zinc-400">Load (1m)</div>
            <div className="text-sm font-semibold">{Number(latestSample?.load_1m || 0).toFixed(2)}</div>
          </div>
        </div>

        {monitorError && (
          <div className="text-xs text-red-400 mb-2">{monitorError}</div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <Sparkline title="System CPU" values={cpuSeries} colorClass="stroke-red-400" suffix="%" />
          <Sparkline title="App CPU" values={appCpuSeries} colorClass="stroke-orange-400" suffix="%" />
          <Sparkline title="Memory Used" values={memSeries} colorClass="stroke-blue-400" suffix="%" />
          <Sparkline title="Load 1m" values={loadSeries} colorClass="stroke-emerald-400" />
        </div>
      </div>

      <div className="rounded-xl p-4 border sa-card">
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
              className="flex items-start gap-3 rounded-lg p-3 text-xs sa-nested border"
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
