import React, { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/apiService';
import { useAuthSettings } from '../hooks/useAuthSettings';
import SystemMonitoring from '../components/SystemMonitoring';
import ThemeManager from '../components/ThemeManager';
import HistoricOrdersPage from './HistoricOrders';

// ── helpers ──────────────────────────────────────────────────────────────────
const API = '/api/v2';
const req = (path, opts = {}) =>
  fetch(`${API}${path}`, { headers: { 'Content-Type': 'application/json' }, ...opts });

const DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const EXCHANGES    = ['NSE', 'BSE', 'MCX'];

const defaultMarketConfig = () => ({
  NSE: { open: '09:15', close: '15:30', days: [0, 1, 2, 3, 4] },
  BSE: { open: '09:15', close: '15:30', days: [0, 1, 2, 3, 4] },
  MCX: { open: '09:00', close: '23:55', days: [0, 1, 2, 3, 4] },
});

const TABS = [
  { id: 'settings',  label: 'Settings & Monitoring' },
  { id: 'authCheck', label: 'User Auth Check' },
  { id: 'historic',  label: 'Historic Position' },
  { id: 'orders', label: 'Historic Orders' },
  { id: 'schedulers', label: 'Schedulers' },
  { id: 'themes', label: '🎨 Theme Manager' },
];

// ── Row components ────────────────────────────────────────────────────────────
const FormField = ({ label, children }) => (
  <div className="flex flex-col gap-1">
    <label className="text-xs font-medium text-gray-400">{label}</label>
    {children}
  </div>
);

const inputCls = 'w-full px-3 py-2 text-sm bg-zinc-800 border border-zinc-700 text-zinc-100 rounded-lg outline-none focus:border-blue-500';
const btnCls   = (color = 'blue') =>
  `px-4 py-2 rounded-lg bg-${color}-600 hover:bg-${color}-500 text-white text-sm font-medium transition-colors disabled:opacity-50`;

// ── Main component ─────────────────────────────────────────────────────────────
const SuperAdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('settings');

  // ── Auth settings ──
  const { localSettings, setLocalSettings, saved, loading: authLoading, isSaving, saveSettings } = useAuthSettings();

  // ── Master loading ──
  const [masterLoading, setMasterLoading] = useState(false);
  const [masterMsg, setMasterMsg]         = useState('');

  // ── NSE file upload ──
  const [uploadMsg, setUploadMsg]              = useState('');
  const [exposureFile, setExposureFile]        = useState(null);
  const [equitySpanFile, setEquitySpanFile]    = useState(null);
  const [commoditySpanFile, setCommoditySpanFile] = useState(null);

  // ── Market config ──
  const [marketConfig, setMarketConfig] = useState(defaultMarketConfig());
  const [mcError, setMcError]           = useState('');

  // ── User auth check ──
  const [authCheckIdentifier, setAuthCheckIdentifier] = useState('');
  const [authCheckPassword, setAuthCheckPassword]     = useState('');
  const [authCheckLoading, setAuthCheckLoading]       = useState(false);
  const [authCheckResult, setAuthCheckResult]         = useState(null);
  const [authCheckError, setAuthCheckError]           = useState('');

  // ── Backdate position ──
  const [backdateForm, setBackdateForm]     = useState({ user_id: '', symbol: '', qty: '', price: '', trade_date: '', instrument_type: 'EQ', exchange: 'NSE' });
  const [backdateLoading, setBackdateLoading] = useState(false);
  const [backdateError, setBackdateError]   = useState('');
  const [backdateMsg, setBackdateMsg]       = useState('');
  const [backdateResult, setBackdateResult] = useState(null);

  // ── Force exit ──
  const [forceExitForm, setForceExitForm]     = useState({ user_id: '', position_id: '', exit_price: '' });
  const [forceExitLoading, setForceExitLoading] = useState(false);
  const [forceExitError, setForceExitError]   = useState('');
  const [forceExitMsg, setForceExitMsg]       = useState('');
  const [forceExitResult, setForceExitResult] = useState(null);

  // ── Instrument autocomplete ──
  const [instrumentSuggestions, setInstrumentSuggestions] = useState([]);

  // ── Dhan connection ──
  const [dhanStatus,    setDhanStatus]    = useState(null);
  const [isConnecting,  setIsConnecting]  = useState(false);
  const [connectMsg,    setConnectMsg]    = useState({ text: '', type: '' });

  // ── Scheduler dashboard ──
  const [schedSnapshot, setSchedSnapshot] = useState(null);
  const [schedLoading, setSchedLoading]   = useState(false);
  const [schedError, setSchedError]       = useState('');
  const [schedWorking, setSchedWorking]   = useState(null);

  // ── Save error ──
  const [saveError, setSaveError] = useState('');

  // ── Fetch Dhan connection status ──
  const fetchDhanStatus = useCallback(async () => {
    try {
      const res = await req('/admin/dhan/status');
      if (res.ok) setDhanStatus(await res.json());
    } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    fetchDhanStatus();
    const id = setInterval(fetchDhanStatus, 5000);
    return () => clearInterval(id);
  }, [fetchDhanStatus]);

  // ── Load market config on mount ──
  const fetchMarketConfig = useCallback(async () => {
    try {
      const res = await req('/admin/market-config');
      if (res.ok) { const data = await res.json(); setMarketConfig(data); }
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { fetchMarketConfig(); }, [fetchMarketConfig]);

  const fetchSchedulers = useCallback(async () => {
    setSchedLoading(true);
    setSchedError('');
    try {
      const res = await apiService.get('/admin/schedulers');
      setSchedSnapshot(res);
    } catch (e) {
      setSchedSnapshot(null);
      setSchedError(e?.message || 'Failed to load schedulers');
    } finally {
      setSchedLoading(false);
    }
  }, []);

  useEffect(() => {
    if (activeTab !== 'schedulers') return;
    fetchSchedulers();
    const id = setInterval(fetchSchedulers, 10000);
    return () => clearInterval(id);
  }, [activeTab, fetchSchedulers]);

  const schedulerAction = async (name, action) => {
    setSchedWorking(`${name}:${action}`);
    setSchedError('');
    try {
      await apiService.post(`/admin/schedulers/${encodeURIComponent(name)}/${encodeURIComponent(action)}`, {});
      await fetchSchedulers();
    } catch (e) {
      setSchedError(e?.message || 'Action failed');
    } finally {
      setSchedWorking(null);
    }
  };

  // ── Handlers ──
  const handleSave = async () => {
    setSaveError('');
    try { await saveSettings(); } catch (e) { setSaveError(e?.message || 'Save failed'); }
  };

  const handleConnect = async () => {
    setIsConnecting(true);
    setConnectMsg({ text: '', type: '' });
    try {
      const res = await req('/admin/dhan/connect', { method: 'POST' });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        setConnectMsg({ text: data.message || 'Connect initiated.', type: 'success' });
      } else {
        setConnectMsg({ text: data.detail || data.message || 'Connect failed.', type: 'error' });
      }
    } catch (e) {
      setConnectMsg({ text: e?.message || 'Connect failed.', type: 'error' });
    } finally {
      setIsConnecting(false);
      fetchDhanStatus();
    }
  };

  const handleDisconnect = async () => {
    setIsConnecting(true);
    setConnectMsg({ text: '', type: '' });
    try {
      const res = await req('/admin/dhan/disconnect', { method: 'POST' });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        setConnectMsg({ text: data.message || 'Disconnected.', type: 'success' });
      } else {
        setConnectMsg({ text: data.detail || data.message || 'Disconnect failed.', type: 'error' });
      }
    } catch (e) {
      setConnectMsg({ text: e?.message || 'Disconnect failed.', type: 'error' });
    } finally {
      setIsConnecting(false);
      fetchDhanStatus();
    }
  };

  const handleLoadInstrumentMaster = async () => {
    setMasterLoading(true); setMasterMsg('');
    try {
      const res = await req('/admin/scrip-master/refresh', { method: 'POST' });
      const data = await res.json().catch(() => ({}));
      setMasterMsg(res.ok ? (data.message || 'Instrument master reloaded.') : (data.detail || 'Failed.'));
    } catch (e) { setMasterMsg(e?.message || 'Error'); } finally { setMasterLoading(false); }
  };

  const handleUploadNseFiles = async () => {
    if (!exposureFile && !equitySpanFile && !commoditySpanFile) { setUploadMsg('Select at least one file.'); return; }
    setUploadMsg('Uploading...');
    const form = new FormData();
    if (exposureFile)      form.append('exposure_csv', exposureFile);
    if (equitySpanFile)    form.append('equity_span', equitySpanFile);
    if (commoditySpanFile) form.append('commodity_span', commoditySpanFile);
    try {
      const res = await fetch(`${API}/admin/upload-nse-files`, { method: 'POST', body: form });
      const data = await res.json().catch(() => ({}));
      setUploadMsg(res.ok ? (data.message || 'Files uploaded.') : (data.detail || 'Upload failed.'));
    } catch (e) { setUploadMsg(e?.message || 'Error'); }
  };

  const saveMarketConfig = async () => {
    setMcError('');
    try {
      const res = await req('/admin/market-config', { method: 'POST', body: JSON.stringify(marketConfig) });
      if (!res.ok) { const d = await res.json().catch(() => ({})); setMcError(d.detail || 'Save failed'); }
    } catch (e) { setMcError(e?.message || 'Error'); }
  };

  const handleUserAuthCheck = async () => {
    if (!authCheckIdentifier) { setAuthCheckError('Enter identifier.'); return; }
    setAuthCheckLoading(true); setAuthCheckResult(null); setAuthCheckError('');
    try {
      const res = await req('/admin/diagnose-login', { method: 'POST', body: JSON.stringify({ identifier: authCheckIdentifier, password: authCheckPassword }) });
      const data = await res.json().catch(() => ({}));
      if (res.ok) setAuthCheckResult(data); else setAuthCheckError(data.detail || 'Check failed');
    } catch (e) { setAuthCheckError(e?.message || 'Error'); } finally { setAuthCheckLoading(false); }
  };

  const handleBackdatePosition = async () => {
    setBackdateLoading(true); setBackdateError(''); setBackdateMsg(''); setBackdateResult(null);
    try {
      const res = await req('/admin/backdate-position', { method: 'POST', body: JSON.stringify(backdateForm) });
      const data = await res.json().catch(() => ({}));
      if (res.ok) { setBackdateMsg(data.message || 'Position created.'); setBackdateResult(data); }
      else setBackdateError(data.detail || 'Failed');
    } catch (e) { setBackdateError(e?.message || 'Error'); } finally { setBackdateLoading(false); }
  };

  const handleForceExit = async () => {
    if (!forceExitForm.position_id) { setForceExitError('Position ID required.'); return; }
    setForceExitLoading(true); setForceExitError(''); setForceExitMsg(''); setForceExitResult(null);
    try {
      const res = await req('/admin/force-exit', { method: 'POST', body: JSON.stringify(forceExitForm) });
      const data = await res.json().catch(() => ({}));
      if (res.ok) { setForceExitMsg(data.message || 'Force exit done.'); setForceExitResult(data); }
      else setForceExitError(data.detail || 'Failed');
    } catch (e) { setForceExitError(e?.message || 'Error'); } finally { setForceExitLoading(false); }
  };

  const searchInstrument = async (q) => {
    if (!q || q.length < 2) { setInstrumentSuggestions([]); return; }
    try {
      const res = await req(`/instruments/search?q=${encodeURIComponent(q)}&limit=8`);
      if (res.ok) setInstrumentSuggestions(await res.json());
    } catch { setInstrumentSuggestions([]); }
  };

  return (
    <div className="space-y-6">
      {/* Header with Mode Badge */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold">Super Admin Dashboard</h2>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 rounded-lg p-1 overflow-x-auto bg-zinc-900 border border-zinc-700">
        {TABS.map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id)}
            className={`flex-shrink-0 px-4 py-2 rounded text-sm font-medium transition-all ${activeTab === t.id ? 'bg-blue-600 text-white' : 'text-zinc-400 hover:text-white'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* ── Settings & Monitoring ── */}
      {activeTab === 'settings' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left column */}
          <div className="space-y-6">
            {/* DhanHQ Auth */}
            <div className="rounded-xl p-5 space-y-4 bg-zinc-800 border border-zinc-700">
              <h2 className="text-base font-semibold">DhanHQ Authentication</h2>
              <div className="flex gap-2">
                {['DAILY_TOKEN', 'STATIC_IP'].map(mode => (
                  <button key={mode} onClick={() => setLocalSettings(s => ({ ...s, authMode: mode }))}
                    className={`flex-1 py-2 rounded-lg text-xs font-semibold transition-all ${
                      localSettings.authMode === mode
                        ? 'bg-blue-600 text-white'
                        : 'bg-zinc-800 text-zinc-400 border border-zinc-700'
                    }`}>
                    {mode}
                  </button>
                ))}
              </div>

              <FormField label="Client ID">
                <input className={inputCls} value={localSettings.clientId || ''}
                  onChange={e => setLocalSettings(s => ({ ...s, clientId: e.target.value }))} placeholder="DhanHQ client ID" />
              </FormField>
              <FormField label="Access Token">
                <input className={inputCls} value={localSettings.accessToken || ''}
                  onChange={e => setLocalSettings(s => ({ ...s, accessToken: e.target.value }))} placeholder="Access token" type="password" />
              </FormField>
              {localSettings.authMode === 'STATIC_IP' && (
                <>
                  <FormField label="API Key">
                    <input className={inputCls} value={localSettings.apiKey || ''}
                      onChange={e => setLocalSettings(s => ({ ...s, apiKey: e.target.value }))} placeholder="API key" />
                  </FormField>
                  <FormField label="Client Secret">
                    <input className={inputCls} value={localSettings.clientSecret || ''}
                      onChange={e => setLocalSettings(s => ({ ...s, clientSecret: e.target.value }))} placeholder="Client secret" type="password" />
                  </FormField>
                </>
              )}
              {saveError && <p className="text-xs text-red-400">{saveError}</p>}
              {saved && <p className="text-xs text-green-400">Saved successfully</p>}

              <div className="flex gap-2">
                <button onClick={handleSave} disabled={isSaving || authLoading} className={btnCls('blue')}>
                  {isSaving ? 'Saving…' : 'Save Credentials'}
                </button>
                {dhanStatus?.tick_processor
                  ? <button onClick={handleDisconnect} disabled={isConnecting} className={btnCls('red')}>
                      {isConnecting ? 'Working…' : 'Disconnect'}
                    </button>
                  : <button onClick={handleConnect} disabled={isConnecting} className={btnCls('green')}>
                      {isConnecting ? 'Connecting…' : 'Connect to Dhan'}
                    </button>
                }
              </div>

              {/* Connection status indicator */}
              <div className="flex items-center gap-2 text-xs">
                <span className={`w-2 h-2 rounded-full flex-shrink-0 ${
                  dhanStatus === null              ? 'bg-gray-500' :
                  dhanStatus.connected             ? 'bg-green-500 animate-pulse' :
                  dhanStatus.tick_processor        ? 'bg-yellow-400 animate-pulse' :
                                                     'bg-red-500'
                }`} />
                <span className="text-zinc-400">
                  {dhanStatus === null ? 'Checking status…'
                    : dhanStatus.connected     ? `Connected — ${dhanStatus.slots?.filter(s => s.connected).length ?? 0}/5 WS slots active`
                    : dhanStatus.tick_processor ? 'Services started — waiting for WS connection…'
                    : dhanStatus.has_credentials ? 'Credentials saved — not connected'
                    : 'No credentials saved'
                  }
                </span>
              </div>

              {connectMsg.text && (
                <p className={`text-xs ${
                  connectMsg.type === 'success' ? 'text-green-400' :
                  connectMsg.type === 'warn'    ? 'text-yellow-400' : 'text-red-400'
                }`}>{connectMsg.text}</p>
              )}
            </div>

            {/* Market Hours */}
            <div className="rounded-xl p-5 space-y-4 bg-zinc-800 border border-zinc-700">
              <h2 className="text-base font-semibold">Market Hours</h2>
              {EXCHANGES.map(ex => (
                <div key={ex} className="space-y-2">
                  <div className="text-xs font-semibold text-blue-400">{ex}</div>
                  <div className="grid grid-cols-2 gap-3">
                    <FormField label="Open">
                      <input type="time" className={inputCls}
                        value={marketConfig[ex]?.open || ''}
                        onChange={e => setMarketConfig(c => ({ ...c, [ex]: { ...c[ex], open: e.target.value } }))} />
                    </FormField>
                    <FormField label="Close">
                      <input type="time" className={inputCls}
                        value={marketConfig[ex]?.close || ''}
                        onChange={e => setMarketConfig(c => ({ ...c, [ex]: { ...c[ex], close: e.target.value } }))} />
                    </FormField>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {DAYS_OF_WEEK.map((day, idx) => (
                      <label key={day} className="flex items-center gap-1 text-xs cursor-pointer">
                        <input type="checkbox"
                          checked={(marketConfig[ex]?.days || []).includes(idx)}
                          onChange={e => {
                            const days = [...(marketConfig[ex]?.days || [])];
                            if (e.target.checked) days.push(idx); else days.splice(days.indexOf(idx), 1);
                            setMarketConfig(c => ({ ...c, [ex]: { ...c[ex], days } }));
                          }} />
                        {day.slice(0, 3)}
                      </label>
                    ))}
                  </div>
                </div>
              ))}
              {mcError && <p className="text-xs text-red-400">{mcError}</p>}
              <button onClick={saveMarketConfig} className={btnCls('green')}>Save Market Hours</button>
            </div>

            {/* NSE Files */}
            <div className="rounded-xl p-5 space-y-4 bg-zinc-800 border border-zinc-700">
              <h2 className="text-base font-semibold">NSE File Upload</h2>
              <FormField label="Equity Exposure CSV">
                <input type="file" accept=".csv" onChange={e => setExposureFile(e.target.files?.[0] || null)} className="text-xs text-gray-300" />
              </FormField>
              <FormField label="Equity SPAN ZIP">
                <input type="file" accept=".zip" onChange={e => setEquitySpanFile(e.target.files?.[0] || null)} className="text-xs text-gray-300" />
              </FormField>
              <FormField label="Commodity SPAN ZIP">
                <input type="file" accept=".zip" onChange={e => setCommoditySpanFile(e.target.files?.[0] || null)} className="text-xs text-gray-300" />
              </FormField>
              {uploadMsg && <p className="text-xs text-blue-300">{uploadMsg}</p>}
              <button onClick={handleUploadNseFiles} className={btnCls('indigo')}>Upload Files</button>
            </div>

            {/* Instrument Master */}
            <div className="rounded-xl p-5 space-y-3 bg-zinc-800 border border-zinc-700">
              <h2 className="text-base font-semibold">Instrument Master</h2>
              <p className="text-xs text-gray-400">Reload the scrip master from DhanHQ / NSE files.</p>
              {masterMsg && <p className="text-xs text-blue-300">{masterMsg}</p>}
              <button onClick={handleLoadInstrumentMaster} disabled={masterLoading} className={btnCls('purple')}>
                {masterLoading ? 'Reloading…' : 'Reload Instrument Master'}
              </button>
            </div>
          </div>

          {/* Right column — System Monitoring */}
          <div className="rounded-xl p-5 bg-zinc-800 border border-zinc-700">
            <h2 className="text-base font-semibold mb-4">System Monitoring</h2>
            <SystemMonitoring />
          </div>
        </div>
      )}

      {/* ── User Auth Check ── */}
      {activeTab === 'authCheck' && (
        <div className="max-w-lg space-y-4">
          <div className="rounded-xl p-5 space-y-4 bg-zinc-800 border border-zinc-700">
            <h2 className="text-base font-semibold">Diagnose User Login</h2>
            <p className="text-xs text-gray-400">Check why a user cannot log in. Enter their mobile or username.</p>
            <FormField label="Mobile / Username">
              <input className={inputCls} value={authCheckIdentifier}
                onChange={e => setAuthCheckIdentifier(e.target.value)} placeholder="9876543210" />
            </FormField>
            <FormField label="Password (optional — verifies hash)">
              <input className={inputCls} type="password" value={authCheckPassword}
                onChange={e => setAuthCheckPassword(e.target.value)} placeholder="Leave blank to skip" />
            </FormField>
            {authCheckError && <p className="text-xs text-red-400">{authCheckError}</p>}
            <button onClick={handleUserAuthCheck} disabled={authCheckLoading} className={btnCls('blue')}>
              {authCheckLoading ? 'Checking…' : 'Run Diagnosis'}
            </button>
            {authCheckResult && (
              <pre className="rounded-lg p-3 text-xs overflow-auto max-h-72 bg-zinc-950 text-zinc-100">
                {JSON.stringify(authCheckResult, null, 2)}
              </pre>
            )}
          </div>
        </div>
      )}

      {/* ── Historic Position ── */}
      {activeTab === 'historic' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Backdate */}
          <div className="rounded-xl p-5 space-y-4 bg-zinc-800 border border-zinc-700">
            <h2 className="text-base font-semibold">Backdate Position</h2>
            <p className="text-xs text-gray-400">Manually add a historic trade position for any user.</p>
            {['user_id', 'symbol', 'qty', 'price', 'trade_date'].map(field => (
              <FormField key={field} label={field.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}>
                <input
                  className={inputCls}
                  type={field === 'trade_date' ? 'date' : field === 'qty' || field === 'price' ? 'number' : 'text'}
                  value={backdateForm[field]}
                  onChange={e => {
                    if (field === 'symbol') { searchInstrument(e.target.value); }
                    setBackdateForm(f => ({ ...f, [field]: e.target.value }));
                  }}
                  list={field === 'symbol' ? 'symbolSuggestions' : undefined}
                />
              </FormField>
            ))}
            {instrumentSuggestions.length > 0 && (
              <datalist id="symbolSuggestions">
                {instrumentSuggestions.map((s, i) => <option key={i} value={s.trading_symbol || s.symbol} />)}
              </datalist>
            )}
            <div className="grid grid-cols-2 gap-3">
              <FormField label="Instrument Type">
                <select className={inputCls} value={backdateForm.instrument_type}
                  onChange={e => setBackdateForm(f => ({ ...f, instrument_type: e.target.value }))}>
                  {['EQ', 'FUT', 'CE', 'PE'].map(t => <option key={t}>{t}</option>)}
                </select>
              </FormField>
              <FormField label="Exchange">
                <select className={inputCls} value={backdateForm.exchange}
                  onChange={e => setBackdateForm(f => ({ ...f, exchange: e.target.value }))}>
                  {EXCHANGES.map(ex => <option key={ex}>{ex}</option>)}
                </select>
              </FormField>
            </div>
            {backdateError && <p className="text-xs text-red-400">{backdateError}</p>}
            {backdateMsg   && <p className="text-xs text-green-400">{backdateMsg}</p>}
            {backdateResult && (
              <pre className="rounded-lg p-3 text-xs overflow-auto max-h-40 bg-zinc-950 text-zinc-100">
                {JSON.stringify(backdateResult, null, 2)}
              </pre>
            )}
            <button onClick={handleBackdatePosition} disabled={backdateLoading} className={btnCls('blue')}>
              {backdateLoading ? 'Adding…' : 'Add Historic Position'}
            </button>
          </div>

          {/* Force Exit */}
          <div className="rounded-xl p-5 space-y-4 bg-zinc-800 border border-zinc-700">
            <h2 className="text-base font-semibold">Force Exit Position</h2>
            <p className="text-xs text-gray-400">Manually close an open position at a specified price.</p>
            <FormField label="User ID">
              <input className={inputCls} value={forceExitForm.user_id}
                onChange={e => setForceExitForm(f => ({ ...f, user_id: e.target.value }))} placeholder="User ID" />
            </FormField>
            <FormField label="Position ID">
              <input className={inputCls} value={forceExitForm.position_id}
                onChange={e => setForceExitForm(f => ({ ...f, position_id: e.target.value }))} placeholder="Position ID" />
            </FormField>
            <FormField label="Exit Price">
              <input className={inputCls} type="number" step="0.05" value={forceExitForm.exit_price}
                onChange={e => setForceExitForm(f => ({ ...f, exit_price: e.target.value }))} placeholder="e.g. 450.50" />
            </FormField>
            {forceExitError && <p className="text-xs text-red-400">{forceExitError}</p>}
            {forceExitMsg   && <p className="text-xs text-green-400">{forceExitMsg}</p>}
            {forceExitResult && (
              <pre className="rounded-lg p-3 text-xs overflow-auto max-h-40 bg-zinc-950 text-zinc-100">
                {JSON.stringify(forceExitResult, null, 2)}
              </pre>
            )}
            <button onClick={handleForceExit} disabled={forceExitLoading} className={`${btnCls('red')} mt-2`}>
              {forceExitLoading ? 'Exiting…' : 'Force Exit Position'}
            </button>
          </div>
        </div>
      )}

      {/* ── Schedulers ── */}
      {activeTab === 'schedulers' && (
        <div className="space-y-4">
          <div className="rounded-xl p-5 bg-zinc-800 border border-zinc-700">
            <div className="flex items-center justify-between gap-3">
              <div>
                <h2 className="text-base font-semibold">Schedulers</h2>
                <p className="text-xs text-zinc-400 mt-1">
                  Server time (IST): {schedSnapshot?.server_time_ist || '—'}
                </p>
                <p className="text-xs text-zinc-400">
                  Equity window: {schedSnapshot?.equity_window_active ? 'ACTIVE' : 'INACTIVE'} · Commodity window: {schedSnapshot?.commodity_window_active ? 'ACTIVE' : 'INACTIVE'}
                </p>
              </div>
              <button onClick={fetchSchedulers} disabled={schedLoading} className={btnCls('blue')}>
                {schedLoading ? 'Refreshing…' : 'Refresh'}
              </button>
            </div>

            {schedError && <p className="text-xs text-red-400 mt-3">{schedError}</p>}

            <div className="mt-4 overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="text-xs text-zinc-400">
                    <th className="text-left py-2 pr-4">Name</th>
                    <th className="text-left py-2 pr-4">Type</th>
                    <th className="text-left py-2 pr-4">Window</th>
                    <th className="text-left py-2 pr-4">Status</th>
                    <th className="text-left py-2 pr-4">Override</th>
                    <th className="text-left py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {(schedSnapshot?.items || []).map((it) => {
                    const working = schedWorking && schedWorking.startsWith(it.id + ':');
                    return (
                      <tr key={it.id} className="border-t border-zinc-700">
                        <td className="py-3 pr-4 font-semibold text-zinc-100">{it.label}</td>
                        <td className="py-3 pr-4 text-zinc-300">{it.kind}</td>
                        <td className="py-3 pr-4 text-zinc-300">{it.window}</td>
                        <td className="py-3 pr-4">
                          <span className={`text-xs font-semibold px-2 py-1 rounded-full ${it.running ? 'bg-green-900/40 text-green-300 border border-green-700/40' : 'bg-zinc-900/40 text-zinc-300 border border-zinc-700/40'}`}>
                            {it.running ? 'RUNNING' : 'STOPPED'}
                          </span>
                        </td>
                        <td className="py-3 pr-4 text-zinc-300">{it.override}</td>
                        <td className="py-3">
                          <div className="flex flex-wrap gap-2">
                            {(it.actions || []).includes('start') && (
                              <button disabled={working || schedLoading} onClick={() => schedulerAction(it.id, 'start')} className={btnCls('green')}>Start</button>
                            )}
                            {(it.actions || []).includes('stop') && (
                              <button disabled={working || schedLoading} onClick={() => schedulerAction(it.id, 'stop')} className={btnCls('red')}>Stop</button>
                            )}
                            {(it.actions || []).includes('refresh') && (
                              <button disabled={working || schedLoading} onClick={() => schedulerAction(it.id, 'refresh')} className={btnCls('indigo')}>Refresh</button>
                            )}
                            {(it.actions || []).includes('auto') && (
                              <button disabled={working || schedLoading} onClick={() => schedulerAction(it.id, 'auto')} className={btnCls('blue')}>Auto</button>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <div className="mt-4 text-xs text-zinc-400">
              Holidays loaded: NSE {schedSnapshot?.holidays?.NSE?.count ?? 0}, BSE {schedSnapshot?.holidays?.BSE?.count ?? 0}, MCX {schedSnapshot?.holidays?.MCX?.count ?? 0}
            </div>
          </div>
        </div>
      )}

      {/* ── Historic Orders ── */}
      {activeTab === 'orders' && (
        <HistoricOrdersPage />
      )}

      {/* ── Themes ── */}
      {activeTab === 'themes' && (
        <ThemeManager />
      )}

    </div>
  );
};

export default SuperAdminDashboard;
