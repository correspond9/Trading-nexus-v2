import React, { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/apiService';
import { useAuthSettings } from '../hooks/useAuthSettings';
import SystemMonitoring from '../components/SystemMonitoring';
import HistoricOrdersPage from './HistoricOrders';

// ── helpers ──────────────────────────────────────────────────────────────────
const API = '/api/v2';
const req = (path, opts = {}) => {
  const token = localStorage.getItem('authToken');
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'X-AUTH': token }),
    ...opts.headers,
  };
  return fetch(`${API}${path}`, { ...opts, headers });
};

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
];

// ── Row components ────────────────────────────────────────────────────────────
const FormField = ({ label, children }) => (
  <div className="flex flex-col gap-1">
    <label className="text-xs font-medium text-gray-400">{label}</label>
    {children}
  </div>
);

const inputCls = 'w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 text-white rounded-lg outline-none focus:border-blue-500';
const btnCls   = (color = 'blue') => `px-4 py-2 rounded-lg font-medium transition-colors text-white text-sm ${
  color === 'blue' ? 'bg-blue-600 hover:bg-blue-500 disabled:bg-blue-900' :
  color === 'red' ? 'bg-red-600 hover:bg-red-500 disabled:bg-red-900' :
  'bg-gray-600 hover:bg-gray-500 disabled:bg-gray-900'
}`;

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
  const [symbolInputBlur, setSymbolInputBlur] = useState(false);

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

  // ── Logo upload ──
  const [logoFile, setLogoFile]         = useState(null);
  const [logoPreview, setLogoPreview]   = useState(null);
  const [logoUploading, setLogoUploading] = useState(false);
  const [logoMsg, setLogoMsg]           = useState('');
  const [currentLogo, setCurrentLogo]   = useState(null);

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
    setBackdateLoading(true); 
    setBackdateError(''); 
    setBackdateMsg(''); 
    setBackdateResult(null);
    
    try {
      // Validate required fields
      if (!backdateForm.user_id.trim()) {
        setBackdateError('User ID is required');
        setBackdateLoading(false);
        return;
      }
      if (!backdateForm.symbol.trim()) {
        setBackdateError('Symbol is required - use the dropdown to search');
        setBackdateLoading(false);
        return;
      }
      if (!backdateForm.qty) {
        setBackdateError('Quantity is required');
        setBackdateLoading(false);
        return;
      }
      if (!backdateForm.price) {
        setBackdateError('Price is required');
        setBackdateLoading(false);
        return;
      }
      if (!backdateForm.trade_date) {
        setBackdateError('Trade Date is required');
        setBackdateLoading(false);
        return;
      }
      
      // Validate symbol - must not contain spaces (indicates user didn't use search dropdown)
      if (backdateForm.symbol.includes(' ')) {
        setBackdateError('Symbol must not contain spaces. Please use the search dropdown to select an instrument.');
        setBackdateLoading(false);
        return;
      }
      
      // Convert date from YYYY-MM-DD to DD-MM-YYYY for backend
      const formData = { ...backdateForm };
      formData.symbol = formData.symbol.toUpperCase().trim();
      formData.exchange = formData.exchange.toUpperCase().trim();
      
      if (formData.trade_date) {
        const [year, month, day] = formData.trade_date.split('-');
        formData.trade_date = `${day}-${month}-${year}`;
      }
      
      const res = await req('/admin/backdate-position', { 
        method: 'POST', 
        body: JSON.stringify(formData) 
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) { 
        setBackdateMsg(data.message || 'Position created.'); 
        setBackdateResult(data); 
        // Clear form on success
        setBackdateForm({ user_id: '', symbol: '', qty: '', price: '', trade_date: '', instrument_type: 'EQ', exchange: 'NSE' });
      }
      else setBackdateError(data.detail || 'Failed');
    } catch (e) { setBackdateError(e?.message || 'Error'); } 
    finally { setBackdateLoading(false); }
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
      if (res.ok) {
        const data = await res.json();
        const results = Array.isArray(data) ? data : data.data || [];
        setInstrumentSuggestions(results);
      }
    } catch { setInstrumentSuggestions([]); }
  };

  // ── Logo handlers ──
  const fetchCurrentLogo = useCallback(async () => {
    try {
      const res = await req('/admin/logo');
      if (res.ok) {
        const data = await res.json();
        setCurrentLogo(data.logo);
      }
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { fetchCurrentLogo(); }, [fetchCurrentLogo]);

  const handleLogoFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLogoFile(file);
    const reader = new FileReader();
    reader.onload = (ev) => setLogoPreview(ev.target?.result);
    reader.readAsDataURL(file);
  };

  const handleLogoUpload = async () => {
    if (!logoFile) { setLogoMsg('Select a file first.'); return; }
    setLogoUploading(true); setLogoMsg('');
    const form = new FormData();
    form.append('file', logoFile);
    try {
      const res = await fetch(`${API}/admin/logo/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${apiService._token}` },
        body: form,
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        setLogoMsg('Logo uploaded successfully!');
        await fetchCurrentLogo();
        setLogoFile(null);
        setLogoPreview(null);
      } else {
        setLogoMsg(data.detail || 'Upload failed');
      }
    } catch (e) { setLogoMsg(e?.message || 'Error'); } finally { setLogoUploading(false); }
  };

  const handleLogoDelete = async () => {
    if (!confirm('Delete the current logo?')) return;
    setLogoUploading(true); setLogoMsg('');
    try {
      const res = await req('/admin/logo', { method: 'DELETE' });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        setLogoMsg('Logo deleted successfully.');
        await fetchCurrentLogo();
      } else {
        setLogoMsg(data.detail || 'Delete failed');
      }
    } catch (e) { setLogoMsg(e?.message || 'Error'); } finally { setLogoUploading(false); }
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
      <div className="flex gap-1 rounded-lg p-1 overflow-x-auto bg-gray-950 border border-gray-700">
        {TABS.map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id)}
            className={`flex-shrink-0 px-4 py-2 rounded text-sm font-medium transition-all ${
              activeTab === t.id 
                ? 'bg-blue-600 text-white font-semibold shadow-lg' 
                : 'text-white bg-gray-800 hover:bg-gray-700'
            }`}>
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

            {/* Logo Upload */}
            <div className="rounded-xl p-5 space-y-4 bg-zinc-800 border border-zinc-700">
              <h2 className="text-base font-semibold">Brand Logo</h2>
              <p className="text-xs text-gray-400">Upload a custom logo to replace the "TN" text in the header.</p>
              
              {currentLogo && (
                <div className="space-y-2">
                  <label className="text-xs font-medium text-gray-400">Current Logo</label>
                  <div className="flex items-center gap-3 p-3 bg-zinc-900 rounded-lg border border-zinc-700">
                    <img src={currentLogo} alt="Current logo" className="h-8 max-w-[120px] object-contain" />
                    <button onClick={handleLogoDelete} disabled={logoUploading} className="ml-auto px-3 py-1 text-xs bg-red-600 hover:bg-red-500 text-white rounded transition-colors">
                      Delete
                    </button>
                  </div>
                </div>
              )}

              <FormField label="Upload New Logo (PNG, JPG, SVG - Max 2MB)">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleLogoFileChange}
                  className="text-xs text-gray-300"
                />
              </FormField>

              {logoPreview && (
                <div className="p-3 bg-zinc-900 rounded-lg border border-zinc-700">
                  <img src={logoPreview} alt="Preview" className="h-8 max-w-[120px] object-contain" />
                </div>
              )}

              {logoMsg && <p className="text-xs text-blue-300">{logoMsg}</p>}

              <button onClick={handleLogoUpload} disabled={logoUploading || !logoFile} className={btnCls('indigo')}>
                {logoUploading ? 'Uploading…' : 'Upload Logo'}
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
          <div className="rounded-xl p-5 space-y-4 bg-gray-900 border border-gray-700">            <h2 className="text-base font-bold text-white">Backdate Position</h2>
            <h2 className="text-base font-semibold">Backdate Position</h2>
            <p className="text-xs text-gray-400">Manually add a historic trade position for any user.</p>
            
            <FormField label="User ID (Mobile or UUID)">
              <input
                className={inputCls}
                type="text"
                value={backdateForm.user_id}
                onChange={e => setBackdateForm(f => ({ ...f, user_id: e.target.value }))}
                placeholder="e.g., 9999999999 or UUID"
              />
            </FormField>
            
            <FormField label="Symbol">
              <div className="relative">
                <input
                  className={`${inputCls} ${backdateForm.symbol && !instrumentSuggestions.length && symbolInputBlur ? 'border-red-500 border-2' : ''}`}
                  type="text"
                  value={backdateForm.symbol}
                  onChange={e => {
                    const val = e.target.value;
                    searchInstrument(val);
                    setBackdateForm(f => ({ ...f, symbol: val }));
                  }}
                  onBlur={() => setTimeout(() => setSymbolInputBlur(true), 150)}
                  onFocus={() => setSymbolInputBlur(false)}
                  placeholder="Search stocks... (e.g., RELIANCE, INFY)"
                  autoComplete="off"
                  maxLength="20"
                />
                
                {backdateForm.symbol && symbolInputBlur && !instrumentSuggestions.length && (
                  <p className="text-xs text-red-400 mt-1">⚠️ Please search and select from dropdown</p>
                )}
                
                {instrumentSuggestions.length > 0 && !symbolInputBlur && (
                  <div className="absolute top-full left-0 right-0 mt-1 bg-gray-800 border border-gray-600 rounded-lg shadow-lg max-h-64 overflow-y-auto z-10">
                    {instrumentSuggestions.map((suggestion, idx) => {
                      const symbol = suggestion.trading_symbol || suggestion.symbol;
                      const exchangeSegment = suggestion.exchange_segment || suggestion.exchange || '';
                      const instType = suggestion.instrument_type || '';
                      
                      // Extract base exchange from exchange_segment (NSE_EQ -> NSE, BSE_FO -> BSE, etc.)
                      const baseExchange = (exchangeSegment.split('_')[0] || 'NSE').toUpperCase();
                      
                      return (
                        <div
                          key={idx}
                          onClick={() => {
                            setBackdateForm(f => ({ 
                              ...f, 
                              symbol: symbol,
                              exchange: baseExchange || f.exchange,
                              instrument_type: instType.startsWith('OPT') ? (instType.includes('IDX') ? 'OPTIDX' : 'OPTSTK') :
                                              instType.startsWith('FUT') ? (instType.includes('IDX') ? 'FUTIDX' : 'FUTSTK') :
                                              'EQ'
                            }));
                            setInstrumentSuggestions([]);
                            setSymbolInputBlur(true);
                          }}
                          className="px-4 py-3 hover:bg-blue-600 cursor-pointer border-b border-gray-700 last:border-b-0 transition-colors"
                        >
                          <div className="flex items-center justify-between gap-2">
                            <div>
                              <div className="font-semibold text-white">{symbol}</div>
                              <div className="text-xs text-gray-400">{instType}</div>
                            </div>
                            <div className="text-xs px-2 py-1 bg-gray-700 rounded text-gray-300">
                              {exchangeSegment}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </FormField>
            
            <FormField label="Quantity">
              <input
                className={inputCls}
                type="number"
                value={backdateForm.qty}
                onChange={e => setBackdateForm(f => ({ ...f, qty: e.target.value }))}
                placeholder="e.g., 380"
                min="1"
              />
            </FormField>
            
            <FormField label="Price">
              <input
                className={inputCls}
                type="number"
                step="0.05"
                value={backdateForm.price}
                onChange={e => setBackdateForm(f => ({ ...f, price: e.target.value }))}
                placeholder="e.g., 514.70"
                min="0"
              />
            </FormField>
            
            <FormField label="Trade Date">
              <input
                className={inputCls}
                type="date"
                value={backdateForm.trade_date}
                onChange={e => setBackdateForm(f => ({ ...f, trade_date: e.target.value }))}
              />
            </FormField>
            
            <div className="grid grid-cols-2 gap-3">
              <FormField label="Instrument Type">
                <select className={inputCls} value={backdateForm.instrument_type}
                  onChange={e => setBackdateForm(f => ({ ...f, instrument_type: e.target.value }))}>
                  <option value="EQ">Equity (EQ)</option>
                  <option value="FUTSTK">Stock Future (FUTSTK)</option>
                  <option value="OPTSTK">Stock Option (OPTSTK)</option>
                  <option value="FUTIDX">Index Future (FUTIDX)</option>
                  <option value="OPTIDX">Index Option (OPTIDX)</option>
                </select>
              </FormField>
              <FormField label="Exchange">
                <select className={inputCls} value={backdateForm.exchange}
                  onChange={e => setBackdateForm(f => ({ ...f, exchange: e.target.value }))}>
                  {EXCHANGES.map(ex => <option key={ex}>{ex}</option>)}
                </select>
              </FormField>
            </div>
            
            {backdateError && <p className="text-xs text-red-400">❌ {backdateError}</p>}
            {backdateMsg   && <p className="text-xs text-green-400">✅ {backdateMsg}</p>}
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
          <div className="rounded-xl p-5 space-y-4 bg-gray-900 border border-gray-700">            <h2 className="text-base font-bold text-white">Force Exit Position</h2>
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

    </div>
  );
};

export default SuperAdminDashboard;
