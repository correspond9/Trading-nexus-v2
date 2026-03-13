import React, { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/apiService';
import { useAuthSettings } from '../hooks/useAuthSettings';
import SystemMonitoring from '../components/SystemMonitoring';

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
  { id: 'courseEnrollments', label: 'Course Enrollments' },
  { id: 'userSignups', label: 'User Signups' },
  { id: 'schedulers', label: 'Schedulers' },
];

// ── Row components ────────────────────────────────────────────────────────────
const FormField = ({ label, children }) => (
  <div className="flex flex-col gap-1">
    <label className="text-xs font-medium text-gray-400">{label}</label>
    {children}
  </div>
);

const inputCls = 'sa-input w-full px-3 py-2 text-sm border rounded-lg outline-none focus:border-blue-500';
const btnCls   = (color = 'blue') => `px-4 py-2 rounded-lg font-medium transition-colors text-zinc-100 text-sm ${
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

  // ── Soft delete user ──
  const [deleteUserSelection, setDeleteUserSelection] = useState('');
  const [deleteUsersLoading, setDeleteUsersLoading]   = useState(false);
  const [deleteUsersError, setDeleteUsersError]       = useState('');
  const [deleteUsersMsg, setDeleteUsersMsg]           = useState('');
  const [archivedUsers, setArchivedUsers]             = useState([]);
  const [archivedUsersLoading, setArchivedUsersLoading] = useState(false);

  // ── Delete user positions ──
  const [deletePositionsUserSelection, setDeletePositionsUserSelection] = useState('');
  const [deletePositionsLoading, setDeletePositionsLoading] = useState(false);
  const [deletePositionsError, setDeletePositionsError] = useState('');
  const [deletePositionsMsg, setDeletePositionsMsg]   = useState('');
  const [userPositionsList, setUserPositionsList] = useState(null);
  const [selectedPositionIds, setSelectedPositionIds] = useState(new Set());
  const [loadingUserPositions, setLoadingUserPositions] = useState(false);

  // ── Course enrollments ──
  const [courseEnrollments, setCourseEnrollments] = useState([]);
  const [courseEnrollmentsLoading, setCourseEnrollmentsLoading] = useState(false);
  const [courseEnrollmentsError, setCourseEnrollmentsError] = useState('');
  const [courseEnrollmentsTotal, setCourseEnrollmentsTotal] = useState(0);

  // ── User signups ──
  const [portalUsers, setPortalUsers]             = useState([]);
  const [portalUsersLoading, setPortalUsersLoading] = useState(false);
  const [portalUsersError, setPortalUsersError]   = useState('');
  const [portalUsersTotal, setPortalUsersTotal]   = useState(0);
  const [selectedPortalUserIds, setSelectedPortalUserIds] = useState(new Set());
  const [portalUsersDeleteLoading, setPortalUsersDeleteLoading] = useState(false);
  const [portalUsersDeleteMsg, setPortalUsersDeleteMsg] = useState('');
  const [portalUsersStatus, setPortalUsersStatus] = useState('PENDING');
  const [portalActionBusyId, setPortalActionBusyId] = useState(null);

  // ── Backdate position ──
  const [backdateForm, setBackdateForm]     = useState({ user_id: '', symbol: '', qty: '', price: '', trade_date: '', trade_time: '09:15', instrument_type: 'EQ', exchange: 'NSE', product_type: 'MIS' });
  const [backdateLoading, setBackdateLoading] = useState(false);
  const [backdateError, setBackdateError]   = useState('');
  const [backdateMsg, setBackdateMsg]       = useState('');
  const [backdateResult, setBackdateResult] = useState(null);
  const [symbolInputBlur, setSymbolInputBlur] = useState(false);
  const [instrumentSelectedFromDropdown, setInstrumentSelectedFromDropdown] = useState(false);

  // ── Force exit ──
  const [forceExitForm, setForceExitForm]     = useState({ user_id: '', position_id: '', exit_price: '', exit_time: '15:30', exit_date: '' });
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

  // ── Option Chain Controls ──
  const [ocAtmLoading,     setOcAtmLoading]     = useState(false);
  const [ocAtmResult,      setOcAtmResult]      = useState(null);
  const [ocRebuildLoading, setOcRebuildLoading] = useState(false);
  const [ocRebuildResult,  setOcRebuildResult]  = useState(null);

  // ── Expiry Rollover ──
  const [expiryRolloverLoading, setExpiryRolloverLoading] = useState(false);
  const [expiryRolloverResult, setExpiryRolloverResult] = useState(null);

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

  const handleOcRecalibrateAtm = async () => {
    setOcAtmLoading(true);
    setOcAtmResult(null);
    try {
      const res = await req('/admin/option-chain/recalibrate-atm', { method: 'POST' });
      const data = await res.json();
      setOcAtmResult(data);
    } catch (e) {
      setOcAtmResult({ success: false, message: e?.message || 'Request failed' });
    } finally {
      setOcAtmLoading(false);
    }
  };

  const handleOcRebuildSkeleton = async () => {
    setOcRebuildLoading(true);
    setOcRebuildResult(null);
    try {
      const res = await req('/admin/option-chain/rebuild-skeleton', { method: 'POST' });
      const data = await res.json();
      setOcRebuildResult(data);
    } catch (e) {
      setOcRebuildResult({ success: false, message: e?.message || 'Request failed' });
    } finally {
      setOcRebuildLoading(false);
    }
  };

  const handleExpiryRollover = async () => {
    if (!window.confirm('⚠️ This will immediately unsubscribe all expired F&O contracts from WebSocket feeds.\n\nExpired instruments with no watchlist entries or open positions will be removed from subscriptions.\n\nContinue?')) return;
    
    setExpiryRolloverLoading(true);
    setExpiryRolloverResult(null);
    try {
      const res = await req('/admin/force-subscription-rollover', { method: 'POST' });
      const data = await res.json();
      setExpiryRolloverResult(data);
    } catch (e) {
      setExpiryRolloverResult({ status: 'error', message: e?.message || 'Request failed' });
    } finally {
      setExpiryRolloverLoading(false);
    }
  };

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

  const fetchCourseEnrollments = useCallback(async () => {
    setCourseEnrollmentsLoading(true);
    setCourseEnrollmentsError('');
    try {
      const res = await req('/auth/portal/users');
      if (res.ok) {
        const data = await res.json();
        setCourseEnrollments(data.users || []);
        setCourseEnrollmentsTotal(data.total || 0);
      } else {
        const errData = await res.json().catch(() => ({}));
        setCourseEnrollmentsError(errData.detail || 'Failed to load course enrollments');
      }
    } catch (e) {
      setCourseEnrollmentsError(e?.message || 'Error fetching course enrollments');
    } finally {
      setCourseEnrollmentsLoading(false);
    }
  }, []);

  const fetchPortalUsers = useCallback(async () => {
    setPortalUsersLoading(true);
    setPortalUsersError('');
    setPortalUsersDeleteMsg('');
    try {
      const res = await req(`/auth/portal/user-signups?status=${encodeURIComponent(portalUsersStatus)}`);
      if (res.ok) {
        const data = await res.json();
        setPortalUsers(data.users || []);
        setPortalUsersTotal(data.total || 0);
      } else {
        const errData = await res.json().catch(() => ({}));
        setPortalUsersError(errData.detail || 'Failed to load user signups');
      }
    } catch (e) {
      setPortalUsersError(e?.message || 'Error fetching user signups');
    } finally {
      setPortalUsersLoading(false);
    }
  }, [portalUsersStatus]);

  const handlePortalSignupReview = async (signupId, action) => {
    if (!signupId) return;

    let reason = '';
    if (action === 'REJECT') {
      reason = window.prompt('Optional rejection reason:', '') || '';
    }

    setPortalActionBusyId(signupId);
    setPortalUsersError('');
    setPortalUsersDeleteMsg('');
    try {
      const res = await req(`/auth/portal/user-signups/${signupId}/review`, {
        method: 'POST',
        body: JSON.stringify({ action, reason }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setPortalUsersError(data.detail || `Failed to ${action.toLowerCase()} signup`);
      } else {
        setPortalUsersDeleteMsg(data.message || `Signup ${action.toLowerCase()}d successfully`);
        await fetchPortalUsers();
      }
    } catch (e) {
      setPortalUsersError(e?.message || `Failed to ${action.toLowerCase()} signup`);
    } finally {
      setPortalActionBusyId(null);
    }
  };

  useEffect(() => {
    setSelectedPortalUserIds((prev) => {
      if (!prev.size) return prev;
      const validIds = new Set(portalUsers.map((u) => u.id));
      const filtered = new Set([...prev].filter((id) => validIds.has(id)));
      return filtered.size === prev.size ? prev : filtered;
    });
  }, [portalUsers]);

  const togglePortalUserSelection = (userId) => {
    setSelectedPortalUserIds((prev) => {
      const next = new Set(prev);
      if (next.has(userId)) next.delete(userId);
      else next.add(userId);
      return next;
    });
  };

  const toggleSelectAllPortalUsers = () => {
    if (!portalUsers.length) return;
    setSelectedPortalUserIds((prev) => {
      if (prev.size === portalUsers.length) {
        return new Set();
      }
      return new Set(portalUsers.map((u) => u.id));
    });
  };

  const handleDeleteSelectedPortalUsers = async () => {
    const ids = Array.from(selectedPortalUserIds);
    if (!ids.length) return;

    if (!window.confirm(`Delete ${ids.length} selected portal signup(s)? This cannot be undone.`)) return;

    setPortalUsersDeleteLoading(true);
    setPortalUsersError('');
    setPortalUsersDeleteMsg('');
    try {
      const res = await req('/auth/portal/users/delete', {
        method: 'POST',
        body: JSON.stringify({ user_ids: ids }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setPortalUsersError(data.detail || 'Failed to delete selected signups');
      } else {
        setPortalUsersDeleteMsg(data.message || `Deleted ${data.deleted || 0} signup(s)`);
        setSelectedPortalUserIds(new Set());
        await fetchPortalUsers();
      }
    } catch (e) {
      setPortalUsersError(e?.message || 'Failed to delete selected signups');
    } finally {
      setPortalUsersDeleteLoading(false);
    }
  };

  const escapeCsv = (value) => {
    const raw = value == null ? '' : String(value);
    return `"${raw.replace(/"/g, '""')}"`;
  };

  const handleExportCourseEnrollmentsCsv = () => {
    if (!courseEnrollments.length) return;
    const headers = [
      'name',
      'email',
      'mobile',
      'city',
      'experience_level',
      'interest',
      'learning_goal',
      'ip_details',
      'sms_verified',
      'email_verified',
      'created_at',
    ];
    const rows = courseEnrollments.map((u) => [
      u.name,
      u.email,
      u.mobile,
      u.city,
      u.experience_level,
      u.interest,
      u.learning_goal,
      u.ip_details,
      u.sms_verified,
      u.email_verified,
      u.created_at,
    ]);
    const csv = [headers, ...rows]
      .map((row) => row.map(escapeCsv).join(','))
      .join('\n');

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    const stamp = new Date().toISOString().replace(/[:.]/g, '-');
    anchor.href = url;
    anchor.download = `course-enrollments-${stamp}.csv`;
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
    URL.revokeObjectURL(url);
  };

  const handleExportPortalUsersCsv = () => {
    if (!portalUsers.length) return;
    const headers = [
      'name',
      'email',
      'mobile',
      'pan_number',
      'aadhar_number',
      'bank_account_number',
      'ifsc',
      'upi_id',
      'city',
      'ip_details',
      'sms_verified',
      'email_verified',
      'status',
      'rejection_reason',
      'created_at',
    ];
    const rows = portalUsers.map((u) => [
      u.name,
      u.email,
      u.mobile,
      u.pan_number,
      u.aadhar_number,
      u.bank_account_number,
      u.ifsc,
      u.upi_id,
      u.city,
      u.ip_details,
      u.sms_verified,
      u.email_verified,
      u.status,
      u.rejection_reason,
      u.created_at,
    ]);
    const csv = [headers, ...rows]
      .map((row) => row.map(escapeCsv).join(','))
      .join('\n');

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    const stamp = new Date().toISOString().replace(/[:.]/g, '-');
    anchor.href = url;
    anchor.download = `user-signups-${stamp}.csv`;
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
    URL.revokeObjectURL(url);
  };

  // Load admin signup tabs when active
  useEffect(() => {
    if (activeTab === 'courseEnrollments') {
      fetchCourseEnrollments();
    }
  }, [activeTab, fetchCourseEnrollments]);

  useEffect(() => {
    if (activeTab === 'userSignups') {
      fetchPortalUsers();
    }
  }, [activeTab, fetchPortalUsers]);

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

  const handleSoftDeleteUser = async () => {
    if (!deleteUserSelection) { setDeleteUsersError('Select a user.'); return; }
    if (!window.confirm(`⚠️ This will ARCHIVE the user. They cannot login again.\n\nUser: ${deleteUserSelection}\n\nContinue?`)) return;
    
    setDeleteUsersLoading(true); setDeleteUsersError(''); setDeleteUsersMsg('');
    try {
      const res = await req(`/admin/users/${deleteUserSelection}/soft-delete`, { method: 'POST' });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        setDeleteUsersMsg(data.message || 'User archived successfully');
        setDeleteUserSelection('');
        // Refresh archived list
        fetchArchivedUsers();
      } else {
        setDeleteUsersError(data.detail || 'Soft delete failed');
      }
    } catch (e) { setDeleteUsersError(e?.message || 'Error'); } finally { setDeleteUsersLoading(false); }
  };

  const fetchArchivedUsers = async () => {
    setArchivedUsersLoading(true);
    try {
      const res = await req('/admin/users/archived');
      const data = await res.json().catch(() => ({}));
      if (res.ok) setArchivedUsers(data.archived_users || []);
    } catch (e) { /* ignore */ } finally { setArchivedUsersLoading(false); }
  };

  useEffect(() => {
    if (activeTab === 'authCheck') { fetchArchivedUsers(); }
  }, [activeTab]);

  const handleDeleteUserPositions = async () => {
    if (!deletePositionsUserSelection) { setDeletePositionsError('Select a user.'); return; }
    if (!window.confirm(`⚠️ PERMANENT! All positions, orders, and ledger entries will be DELETED.\n\nUser: ${deletePositionsUserSelection}\n\nThis cannot be undone!\n\nContinue?`)) return;
    
    setDeletePositionsLoading(true); setDeletePositionsError(''); setDeletePositionsMsg('');
    try {
      const res = await req(`/admin/users/${deletePositionsUserSelection}/positions/delete-all`, { method: 'POST' });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        setDeletePositionsMsg(data.message || 'Positions deleted successfully');
        setDeletePositionsUserSelection('');
        setUserPositionsList(null);
        setSelectedPositionIds(new Set());
      } else {
        setDeletePositionsError(data.detail || 'Position deletion failed');
      }
    } catch (e) { setDeletePositionsError(e?.message || 'Error'); } finally { setDeletePositionsLoading(false); }
  };

  const handleLoadUserPositions = async () => {
    if (!deletePositionsUserSelection) { setDeletePositionsError('Select a user.'); return; }
    setLoadingUserPositions(true); setDeletePositionsError('');
    try {
      const res = await req(`/admin/users/${deletePositionsUserSelection}/positions`);
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        setUserPositionsList(data);
        setSelectedPositionIds(new Set());
      } else {
        setDeletePositionsError(data.detail || 'Failed to load positions');
      }
    } catch (e) { setDeletePositionsError(e?.message || 'Error'); } finally { setLoadingUserPositions(false); }
  };

  const handleDeleteSpecificPositions = async () => {
    if (selectedPositionIds.size === 0) { setDeletePositionsError('Select at least one position.'); return; }
    if (!window.confirm(`⚠️ PERMANENT! Delete ${selectedPositionIds.size} selected position(s)?\n\nThis cannot be undone!\n\nContinue?`)) return;
    
    setDeletePositionsLoading(true); setDeletePositionsError(''); setDeletePositionsMsg('');
    try {
      const res = await req(`/admin/users/${deletePositionsUserSelection}/positions/delete-specific`, {
        method: 'POST',
        body: JSON.stringify({ position_ids: Array.from(selectedPositionIds) })
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        setDeletePositionsMsg(data.message || 'Positions deleted successfully');
        setSelectedPositionIds(new Set());
        // Reload positions
        await handleLoadUserPositions();
      } else {
        setDeletePositionsError(data.detail || 'Position deletion failed');
      }
    } catch (e) { setDeletePositionsError(e?.message || 'Error'); } finally { setDeletePositionsLoading(false); }
  };

  const togglePositionSelection = (positionId) => {
    const newSet = new Set(selectedPositionIds);
    if (newSet.has(positionId)) {
      newSet.delete(positionId);
    } else {
      newSet.add(positionId);
    }
    setSelectedPositionIds(newSet);
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
      if (!backdateForm.trade_time) {
        setBackdateError('Trade Time is required and must be within market hours');
        setBackdateLoading(false);
        return;
      }
      
      // Convert date from YYYY-MM-DD to DD-MM-YYYY for backend
      const formData = { ...backdateForm };
      formData.symbol = formData.symbol.toUpperCase().trim();
      formData.exchange = formData.exchange.toUpperCase().trim();
      formData.product_type = formData.product_type.toUpperCase().trim();
      
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
        setBackdateForm({ user_id: '', symbol: '', qty: '', price: '', trade_date: '', trade_time: '09:15', instrument_type: 'EQ', exchange: 'NSE', product_type: 'MIS' });
        setInstrumentSelectedFromDropdown(false); // Reset selection flag
      }
      else setBackdateError(data.detail || 'Failed');
    } catch (e) { setBackdateError(e?.message || 'Error'); } 
    finally { setBackdateLoading(false); }
  };

  const handleForceExit = async () => {
    if (!forceExitForm.user_id.trim()) { setForceExitError('User ID required.'); return; }
    if (!forceExitForm.position_id) { setForceExitError('Position ID required.'); return; }
    if (!forceExitForm.exit_price) { setForceExitError('Exit Price required.'); return; }
    if (!forceExitForm.exit_date) { setForceExitError('Exit Date required.'); return; }
    if (!forceExitForm.exit_time) { setForceExitError('Exit Time required and must be within market hours.'); return; }
    
    setForceExitLoading(true); setForceExitError(''); setForceExitMsg(''); setForceExitResult(null);
    try {
      const formData = { ...forceExitForm };
      // Convert date from YYYY-MM-DD to DD-MM-YYYY for backend
      if (formData.exit_date) {
        const [year, month, day] = formData.exit_date.split('-');
        formData.exit_date = `${day}-${month}-${year}`;
      }
      const res = await req('/admin/force-exit', { method: 'POST', body: JSON.stringify(formData) });
      const data = await res.json().catch(() => ({}));
      if (res.ok) { 
        setForceExitMsg(data.message || 'Position closed.'); 
        setForceExitResult(data); 
        // Clear form on success
        setForceExitForm({ user_id: '', position_id: '', exit_price: '', exit_time: '15:30', exit_date: '' });
      }
      else setForceExitError(data.detail || 'Failed');
    } catch (e) { setForceExitError(e?.message || 'Error'); } 
    finally { setForceExitLoading(false); }
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
    <div className="space-y-6 sa-scope">
      {/* Header with Mode Badge */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold">Super Admin Dashboard</h2>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 rounded-lg p-1 overflow-x-auto sa-tabs-bar border">
        {TABS.map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id)}
            className={`flex-shrink-0 px-4 py-2 rounded text-sm font-medium transition-all ${
              activeTab === t.id 
                ? 'bg-blue-600 text-white font-semibold shadow-lg' 
                : 'sa-tab-btn border hover:bg-gray-700'
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
                        ? 'bg-blue-600 text-zinc-100'
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
                {(dhanStatus?.connected || dhanStatus?.tick_processor)
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

            {/* Option Chain Controls */}
            <div className="rounded-xl p-5 space-y-5 bg-zinc-800 border border-zinc-700">
              <h2 className="text-base font-semibold">Option Chain Controls</h2>

              {/* Button 1 — Frontend ATM Reset */}
              <div className="space-y-2">
                <p className="text-xs text-gray-400">
                  <span className="font-semibold text-blue-400">Reset ATM Cache</span> — reads current underlying LTP from the FastAPI DB and refreshes the in-memory ATM. The next Options/Straddle page load will slice strikes around the corrected ATM.
                </p>
                <button
                  onClick={handleOcRecalibrateAtm}
                  disabled={ocAtmLoading}
                  className={btnCls('blue')}
                >
                  {ocAtmLoading ? 'Resetting…' : '↺  Reset ATM Cache (DB LTP)'}
                </button>
                {ocAtmResult && (
                  <div className={`text-xs rounded p-2 mt-1 ${
                    ocAtmResult.success ? 'bg-green-900/40 text-green-300 border border-green-700' : 'bg-red-900/40 text-red-300 border border-red-700'
                  }`}>
                    <div className="font-semibold mb-1">{ocAtmResult.message}</div>
                    {(ocAtmResult.results || []).map(r => (
                      <div key={r.underlying} className="font-mono">
                        {r.underlying}: {r.status === 'updated'
                          ? `LTP=${r.ltp} | ATM ${r.old_atm} → ${r.new_atm}`
                          : r.status}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <hr className="border-zinc-700" />

              {/* Button 2 — Full Backend Rebuild */}
              <div className="space-y-2">
                <p className="text-xs text-gray-400">
                  <span className="font-semibold text-orange-400">Rebuild Skeleton from Dhan</span> — calls DhanHQ REST API for a live spot price snapshot, updates ATM cache, rebuilds the <code className="text-xs text-zinc-300">option_chain_data</code> skeleton centred on the fresh ATM, and queues an immediate Greeks poll to re-hydrate live prices from the Dhan WS.
                </p>
                <button
                  onClick={handleOcRebuildSkeleton}
                  disabled={ocRebuildLoading}
                  className={btnCls('red')}
                >
                  {ocRebuildLoading ? 'Rebuilding…' : '⟳  Rebuild Skeleton from Dhan REST'}
                </button>
                {ocRebuildResult && (
                  <div className={`text-xs rounded p-2 mt-1 ${
                    ocRebuildResult.success ? 'bg-green-900/40 text-green-300 border border-green-700' : 'bg-red-900/40 text-red-300 border border-red-700'
                  }`}>
                    <div className="font-semibold mb-1">{ocRebuildResult.message}</div>
                    {(ocRebuildResult.atm_updates || []).map(r => (
                      <div key={r.underlying} className="font-mono">
                        {r.underlying}: {r.status === 'atm_updated'
                          ? `Dhan LTP=${r.dhan_ltp} | ATM ${r.old_atm} → ${r.new_atm}`
                          : r.status}
                      </div>
                    ))}
                    {ocRebuildResult.skeleton_rebuild && (
                      <div className="mt-1">Skeleton: {ocRebuildResult.skeleton_rebuild}</div>
                    )}
                  </div>
                )}
              </div>
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

            {/* Subscription Management */}
            <div className="rounded-xl p-5 space-y-3 bg-zinc-800 border border-zinc-700">
              <h2 className="text-base font-semibold">Subscription Management</h2>
              <p className="text-xs text-gray-400">
                <span className="font-semibold text-orange-400">Force Expiry Rollover</span> — Immediately unsubscribe expired F&O contracts from WebSocket feeds. This removes expired instruments that have no watchlist entries or open positions. Normally runs automatically at 06:00 IST after scrip master refresh.
              </p>
              <button 
                onClick={handleExpiryRollover} 
                disabled={expiryRolloverLoading} 
                className={btnCls('red')}
              >
                {expiryRolloverLoading ? 'Processing…' : '⟳  Force Expiry Rollover'}
              </button>
              {expiryRolloverResult && (
                <div className={`text-xs rounded p-3 mt-2 ${
                  expiryRolloverResult.status === 'completed' 
                    ? 'bg-green-900/40 text-green-300 border border-green-700' 
                    : 'bg-red-900/40 text-red-300 border border-red-700'
                }`}>
                  <div className="font-semibold mb-2">
                    {expiryRolloverResult.status === 'completed' ? '✓ Rollover Completed' : '✗ Failed'}
                  </div>
                  <div className="space-y-1 font-mono">
                    <div>Tokens Before: <span className="text-white">{expiryRolloverResult.tokens_before || 'N/A'}</span></div>
                    <div>Tokens After: <span className="text-white">{expiryRolloverResult.tokens_after || 'N/A'}</span></div>
                    <div className="font-bold">Evicted: <span className="text-white">{expiryRolloverResult.evicted || 0}</span> expired instruments</div>
                  </div>
                  {expiryRolloverResult.message && (
                    <div className="mt-2 text-xs opacity-80">{expiryRolloverResult.message}</div>
                  )}
                </div>
              )}
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
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left column — Diagnose & Delete */}
          <div className="space-y-6">
            {/* Diagnose User Login */}
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

            {/* Soft Delete User */}
            <div className="rounded-xl p-5 space-y-4 bg-red-950/30 border border-red-700/50">
              <h2 className="text-base font-semibold text-red-300">Soft Delete User (Archive)</h2>
              <p className="text-xs text-gray-400">Archive a user — they cannot login but data is preserved. Recoverable.</p>
              <FormField label="User to Archive">
                <input className={inputCls} value={deleteUserSelection}
                  onChange={e => setDeleteUserSelection(e.target.value)} placeholder="Mobile or User ID" />
              </FormField>
              {deleteUsersError && <p className="text-xs text-red-400">❌ {deleteUsersError}</p>}
              {deleteUsersMsg && <p className="text-xs text-green-400">✓ {deleteUsersMsg}</p>}
              <button onClick={handleSoftDeleteUser} disabled={deleteUsersLoading} className={btnCls('red')}>
                {deleteUsersLoading ? 'Archiving…' : '🗑️ Archive User'}
              </button>
            </div>

            {/* Delete User Positions */}
            <div className="rounded-xl p-5 space-y-4 bg-orange-950/30 border border-orange-700/50">
              <h2 className="text-base font-semibold text-orange-300">Delete Positions</h2>
              <p className="text-xs text-gray-400">⚠️ Delete specific or all positions, orders, and ledger entries.</p>
              
              <FormField label="User ID">
                <input className={inputCls} value={deletePositionsUserSelection}
                  onChange={e => setDeletePositionsUserSelection(e.target.value)} placeholder="Mobile or User ID" />
              </FormField>
              
              <div className="flex gap-2">
                <button onClick={handleLoadUserPositions} disabled={loadingUserPositions || !deletePositionsUserSelection} className={btnCls('blue')}>
                  {loadingUserPositions ? 'Loading…' : 'View Positions'}
                </button>
                <button onClick={handleDeleteUserPositions} disabled={deletePositionsLoading || !deletePositionsUserSelection} className={btnCls('red')}>
                  {deletePositionsLoading ? 'Deleting…' : '🔥 Delete ALL'}
                </button>
              </div>

              {/* Position List */}
              {userPositionsList && (
                <div className="space-y-2 max-h-64 overflow-y-auto rounded-lg bg-zinc-900/50 p-3 border border-zinc-700">
                  <div className="text-xs font-semibold text-gray-300 mb-2">
                    Positions ({userPositionsList.positions.length})
                    {selectedPositionIds.size > 0 && (
                      <span className="ml-2 text-orange-400">
                        {selectedPositionIds.size} selected
                      </span>
                    )}
                  </div>
                  
                  {userPositionsList.positions.length === 0 ? (
                    <p className="text-xs text-gray-500">No positions</p>
                  ) : (
                    userPositionsList.positions.map((pos) => (
                      <label key={pos.position_id} className="flex items-start gap-2 p-2 hover:bg-zinc-800 rounded cursor-pointer text-xs">
                        <input
                          type="checkbox"
                          checked={selectedPositionIds.has(pos.position_id)}
                          onChange={() => togglePositionSelection(pos.position_id)}
                          className="mt-0.5"
                        />
                        <span className="flex-1">
                          <span className="font-semibold">{pos.symbol}</span>
                          <span className="text-gray-400 ml-1">
                            {pos.quantity} @ {pos.avg_price.toFixed(2)}
                          </span>
                          <span className="text-gray-500 ml-1">({pos.status})</span>
                        </span>
                      </label>
                    ))
                  )}
                  
                  {selectedPositionIds.size > 0 && (
                    <button
                      onClick={handleDeleteSpecificPositions}
                      disabled={deletePositionsLoading}
                      className={btnCls('red')}
                      style={{ width: '100%' }}
                    >
                      {deletePositionsLoading ? 'Deleting…' : `Delete ${selectedPositionIds.size} Selected`}
                    </button>
                  )}
                </div>
              )}

              {deletePositionsError && <p className="text-xs text-orange-400">❌ {deletePositionsError}</p>}
              {deletePositionsMsg && <p className="text-xs text-green-400">✓ {deletePositionsMsg}</p>}
            </div>
          </div>

          {/* Right column — Archived Users */}
          <div className="rounded-xl p-5 space-y-4 bg-zinc-800 border border-zinc-700 h-fit">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-semibold">Archived Users</h2>
              <button onClick={fetchArchivedUsers} disabled={archivedUsersLoading} 
                className={`text-xs ${archivedUsersLoading ? 'text-gray-500' : 'text-blue-400 hover:text-blue-300'}`}>
                {archivedUsersLoading ? '⟳ Loading…' : '🔄 Refresh'}
              </button>
            </div>
            <p className="text-xs text-gray-400">Users who have been archived. They cannot login.</p>
            {archivedUsers && archivedUsers.length > 0 ? (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {archivedUsers.map((u, idx) => (
                  <div key={idx} className="p-3 bg-zinc-900 rounded-lg border border-zinc-700 text-xs">
                    <div className="font-semibold text-zinc-100">{u.mobile || u.name || u.email}</div>
                    <div className="text-gray-400 text-xs mt-1">
                      Archived: {new Date(u.archived_at).toLocaleDateString()} 
                      {u.last_login && ` | Last login: ${new Date(u.last_login).toLocaleDateString()}`}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-500">No archived users yet.</p>
            )}
          </div>
        </div>
      )}

      {/* ── Historic Position ── */}
      {activeTab === 'historic' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Backdate */}
          <div className="rounded-xl p-5 space-y-4 sa-card border">
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
                  className={`${inputCls} ${backdateForm.symbol && !instrumentSuggestions.length && symbolInputBlur && !instrumentSelectedFromDropdown ? 'border-red-500 border-2' : ''}`}
                  type="text"
                  value={backdateForm.symbol}
                  onChange={e => {
                    const val = e.target.value;
                    searchInstrument(val);
                    setBackdateForm(f => ({ ...f, symbol: val }));
                    setInstrumentSelectedFromDropdown(false); // User is typing, not selecting
                  }}
                  onBlur={() => setTimeout(() => setSymbolInputBlur(true), 150)}
                  onFocus={() => setSymbolInputBlur(false)}
                  placeholder="Search stocks... (e.g., RELIANCE, INFY)"
                  autoComplete="off"
                  maxLength="20"
                />
                
                {backdateForm.symbol && symbolInputBlur && !instrumentSuggestions.length && !instrumentSelectedFromDropdown && (
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
                            setInstrumentSelectedFromDropdown(true); // Mark as selected from dropdown
                          }}
                          className="px-4 py-3 hover:bg-blue-600 cursor-pointer border-b border-gray-700 last:border-b-0 transition-colors"
                        >
                          <div className="flex items-center justify-between gap-2">
                            <div>
                              <div className="font-semibold text-zinc-100">{symbol}</div>
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
            
            <div className="grid grid-cols-2 gap-3">
              <FormField label="Trade Date">
                <input
                  className={inputCls}
                  type="date"
                  value={backdateForm.trade_date}
                  onChange={e => setBackdateForm(f => ({ ...f, trade_date: e.target.value }))}
                />
              </FormField>
              <FormField label="Trade Time (HH:MM)">
                <input
                  className={inputCls}
                  type="time"
                  value={backdateForm.trade_time}
                  onChange={e => setBackdateForm(f => ({ ...f, trade_time: e.target.value }))}
                />
              </FormField>
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              <FormField label="Instrument Type">
                <select className={inputCls} value={backdateForm.instrument_type}
                  onChange={e => setBackdateForm(f => ({ ...f, instrument_type: e.target.value }))}>
                  <optgroup label="Equity">
                    <option value="EQ">Equity (EQ)</option>
                  </optgroup>
                  <optgroup label="Index">
                    <option value="FUTIDX">Index Future (FUTIDX)</option>
                    <option value="OPTIDX">Index Option (OPTIDX)</option>
                  </optgroup>
                  <optgroup label="Stock Derivatives">
                    <option value="FUTSTK">Stock Future (FUTSTK)</option>
                    <option value="OPTSTK">Stock Option (OPTSTK)</option>
                  </optgroup>
                  <optgroup label="Commodity Derivatives">
                    <option value="FUTCOMM">Commodity Future (FUTCOMM)</option>
                    <option value="OPTCOMM">Commodity Option (OPTCOMM)</option>
                  </optgroup>
                </select>
              </FormField>
              <FormField label="Exchange">
                <select className={inputCls} value={backdateForm.exchange}
                  onChange={e => setBackdateForm(f => ({ ...f, exchange: e.target.value }))}>
                  {EXCHANGES.map(ex => <option key={ex}>{ex}</option>)}
                </select>
              </FormField>
            </div>
            
            <div className="grid grid-cols-1 gap-3">
              <FormField label="Product Type">
                <select className={inputCls} value={backdateForm.product_type}
                  onChange={e => setBackdateForm(f => ({ ...f, product_type: e.target.value }))}>
                  <option value="MIS">MIS (Intraday)</option>
                  <option value="NORMAL">NORMAL (Delivery)</option>
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
          <div className="rounded-xl p-5 space-y-4 sa-card border">
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
            <FormField label="Exit Date">
              <input className={inputCls} type="date" value={forceExitForm.exit_date}
                onChange={e => setForceExitForm(f => ({ ...f, exit_date: e.target.value }))} />
            </FormField>
            <FormField label="Exit Time (HH:MM)">
              <input className={inputCls} type="time" value={forceExitForm.exit_time}
                onChange={e => setForceExitForm(f => ({ ...f, exit_time: e.target.value }))} />
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

      {/* ── Course Enrollments ── */}
      {activeTab === 'courseEnrollments' && (
        <div className="space-y-4">
          <div className="rounded-xl p-5 bg-zinc-800 border border-zinc-700">
            <div className="flex items-center justify-between gap-3 mb-4">
              <div>
                <h2 className="text-base font-semibold">Course Enrollments</h2>
                <p className="text-xs text-zinc-400 mt-1">
                  Total enrollments: <span className="font-semibold text-zinc-100">{courseEnrollmentsTotal}</span>
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <button onClick={handleExportCourseEnrollmentsCsv} disabled={!courseEnrollments.length || courseEnrollmentsLoading} className={btnCls('green')}>
                  Export CSV
                </button>
                <button onClick={fetchCourseEnrollments} disabled={courseEnrollmentsLoading} className={btnCls('blue')}>
                  {courseEnrollmentsLoading ? 'Loading…' : 'Refresh'}
                </button>
              </div>
            </div>

            {courseEnrollmentsError && (
              <div className="mb-4 p-3 bg-red-900/20 border border-red-700/40 rounded-lg text-xs text-red-300">
                {courseEnrollmentsError}
              </div>
            )}

            {courseEnrollmentsLoading && (
              <div className="text-center py-8 text-zinc-400">
                Loading course enrollments...
              </div>
            )}

            {!courseEnrollmentsLoading && courseEnrollments.length === 0 && (
              <div className="text-center py-8 text-zinc-400">
                No records found
              </div>
            )}

            {!courseEnrollmentsLoading && courseEnrollments.length > 0 && (
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="text-xs text-zinc-400 border-b border-zinc-700">
                      <th className="text-left py-3 px-4">Name</th>
                      <th className="text-left py-3 px-4">Email</th>
                      <th className="text-left py-3 px-4">Mobile</th>
                      <th className="text-left py-3 px-4">City</th>
                      <th className="text-left py-3 px-4">IP Details</th>
                      <th className="text-left py-3 px-4">SMS Verified</th>
                      <th className="text-left py-3 px-4">Email Verified</th>
                      <th className="text-left py-3 px-4">Enrollment Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {courseEnrollments.map((user, idx) => (
                      <tr key={user.id} className={`border-b border-zinc-700 hover:bg-zinc-700/30 ${idx % 2 === 0 ? 'bg-zinc-800/50' : ''}`}>
                        <td className="py-3 px-4 font-medium text-zinc-100">{user.name}</td>
                        <td className="py-3 px-4 text-xs text-zinc-300">{user.email}</td>
                        <td className="py-3 px-4 text-xs text-zinc-300">{user.mobile || '—'}</td>
                        <td className="py-3 px-4 text-xs text-zinc-300">{user.city || '—'}</td>
                        <td className="py-3 px-4 text-xs text-zinc-300">{user.ip_details || '—'}</td>
                        <td className="py-3 px-4 text-xs text-zinc-300">{user.sms_verified ? 'Yes' : 'No'}</td>
                        <td className="py-3 px-4 text-xs text-zinc-300">{user.email_verified ? 'Yes' : 'No'}</td>
                        <td className="py-3 px-4 text-xs text-zinc-400">
                          {user.created_at ? new Date(user.created_at).toLocaleString() : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── User Signups ── */}
      {activeTab === 'userSignups' && (
        <div className="space-y-4">
          <div className="rounded-xl p-5 bg-zinc-800 border border-zinc-700">
            <div className="flex items-center justify-between gap-3 mb-4">
              <div>
                <h2 className="text-base font-semibold">User Signups</h2>
                <p className="text-xs text-zinc-400 mt-1">
                  Total {portalUsersStatus.toLowerCase()} items: <span className="font-semibold text-zinc-100">{portalUsersTotal}</span>
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <select
                  className={inputCls}
                  value={portalUsersStatus}
                  onChange={(e) => setPortalUsersStatus(e.target.value)}
                  style={{ minWidth: 140 }}
                >
                  <option value="PENDING">Pending</option>
                  <option value="APPROVED">Approved</option>
                  <option value="REJECTED">Rejected</option>
                  <option value="ALL">All</option>
                </select>
                <button onClick={handleExportPortalUsersCsv} disabled={!portalUsers.length || portalUsersLoading} className={btnCls('green')}>
                  Export CSV
                </button>
                <button onClick={fetchPortalUsers} disabled={portalUsersLoading} className={btnCls('blue')}>
                  {portalUsersLoading ? 'Loading…' : 'Refresh'}
                </button>
              </div>
            </div>

            {portalUsersDeleteMsg && (
              <div className="mb-4 p-3 bg-green-900/20 border border-green-700/40 rounded-lg text-xs text-green-300">
                {portalUsersDeleteMsg}
              </div>
            )}

            {portalUsersError && (
              <div className="mb-4 p-3 bg-red-900/20 border border-red-700/40 rounded-lg text-xs text-red-300">
                {portalUsersError}
              </div>
            )}

            {portalUsersLoading && (
              <div className="text-center py-8 text-zinc-400">
                Loading portal users...
              </div>
            )}

            {!portalUsersLoading && portalUsers.length === 0 && (
              <div className="text-center py-8 text-zinc-400">
                No records found
              </div>
            )}

            {!portalUsersLoading && portalUsers.length > 0 && (
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="text-xs text-zinc-400 border-b border-zinc-700">
                      <th className="text-left py-3 px-4">Name</th>
                      <th className="text-left py-3 px-4">Email</th>
                      <th className="text-left py-3 px-4">Mobile</th>
                      <th className="text-left py-3 px-4">IP Details</th>
                      <th className="text-left py-3 px-4">SMS Verified</th>
                      <th className="text-left py-3 px-4">Email Verified</th>
                      <th className="text-left py-3 px-4">PAN</th>
                      <th className="text-left py-3 px-4">Aadhar</th>
                      <th className="text-left py-3 px-4">Bank A/C</th>
                      <th className="text-left py-3 px-4">IFSC</th>
                      <th className="text-left py-3 px-4">City</th>
                      <th className="text-left py-3 px-4">Status</th>
                      <th className="text-left py-3 px-4">Signup Date</th>
                      <th className="text-left py-3 px-4">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {portalUsers.map((user, idx) => (
                      <tr key={user.id} className={`border-b border-zinc-700 hover:bg-zinc-700/30 ${idx % 2 === 0 ? 'bg-zinc-800/50' : ''}`}>
                        <td className="py-3 px-4 font-medium text-zinc-100">{user.name}</td>
                        <td className="py-3 px-4 text-xs text-zinc-300">{user.email}</td>
                        <td className="py-3 px-4 text-xs text-zinc-300">{user.mobile || '—'}</td>
                        <td className="py-3 px-4 text-xs text-zinc-300">{user.ip_details || '—'}</td>
                        <td className="py-3 px-4 text-xs text-zinc-300">{user.sms_verified ? 'Yes' : 'No'}</td>
                        <td className="py-3 px-4 text-xs text-zinc-300">{user.email_verified ? 'Yes' : 'No'}</td>
                        <td className="py-3 px-4 text-xs text-zinc-300">{user.pan_number || '—'}</td>
                        <td className="py-3 px-4 text-xs text-zinc-300">{user.aadhar_number || '—'}</td>
                        <td className="py-3 px-4 text-xs text-zinc-300">{user.bank_account_number || '—'}</td>
                        <td className="py-3 px-4 text-xs text-zinc-300">{user.ifsc || '—'}</td>
                        <td className="py-3 px-4 text-xs text-zinc-300">{user.city || '—'}</td>
                        <td className="py-3 px-4 text-xs text-zinc-300">{user.status || 'PENDING'}</td>
                        <td className="py-3 px-4 text-xs text-zinc-400">
                          {user.created_at ? new Date(user.created_at).toLocaleString() : '—'}
                        </td>
                        <td className="py-3 px-4 text-xs text-zinc-300">
                          {(user.status || 'PENDING') === 'PENDING' ? (
                            <div className="flex gap-2">
                              <button
                                onClick={() => handlePortalSignupReview(user.id, 'APPROVE')}
                                disabled={portalActionBusyId === user.id}
                                className={btnCls('blue')}
                              >
                                {portalActionBusyId === user.id ? 'Working...' : 'Approve'}
                              </button>
                              <button
                                onClick={() => handlePortalSignupReview(user.id, 'REJECT')}
                                disabled={portalActionBusyId === user.id}
                                className={btnCls('red')}
                              >
                                Reject
                              </button>
                            </div>
                          ) : (
                            <span className="text-zinc-400">Addressed</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
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

    </div>
  );
};

export default SuperAdminDashboard;
