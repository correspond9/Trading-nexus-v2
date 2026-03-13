import React, { useEffect, useMemo, useState } from 'react';

type MetaResponse = {
  brand_name: string;
  message_preview: string;
  sms_test_live_enabled?: boolean;
  defaults: {
    customer_id: string;
    otp_expiry_seconds: number;
    otp_resend_cooldown_seconds: number;
    otp_max_attempts: number;
  };
  response_codes: Record<string, string>;
};

const defaultMeta: MetaResponse = {
  brand_name: 'Message Central',
  message_preview: '**** is your one time password (OTP) for user authentication from Message Central - Powered by U2OPIA',
  sms_test_live_enabled: false,
  defaults: {
    customer_id: 'C-44071166CC38423',
    otp_expiry_seconds: 60,
    otp_resend_cooldown_seconds: 120,
    otp_max_attempts: 7,
  },
  response_codes: {
    '200': 'SUCCESS',
    '400': 'BAD_REQUEST',
    '409': 'DUPLICATE_RESOURCE',
    '500': 'SERVER_ERROR',
    '501': 'INVALID_CUSTOMER_ID',
    '505': 'INVALID_VERIFICATION_ID',
    '506': 'REQUEST_ALREADY_EXISTS',
    '511': 'INVALID_COUNTRY_CODE',
    '700': 'VERIFICATION_FAILED',
    '702': 'WRONG_OTP_PROVIDED',
    '703': 'ALREADY_VERIFIED',
    '705': 'VERIFICATION_EXPIRED',
    '800': 'MAXIMUM_LIMIT_REACHED',
  },
};

const SmsApiTestPage: React.FC = () => {
  const [phone, setPhone] = useState('+91');
  const [otp, setOtp] = useState('');
  const [meta, setMeta] = useState<MetaResponse | null>(null);
  const [sendResponse, setSendResponse] = useState<any>(null);
  const [verifyResponse, setVerifyResponse] = useState<any>(null);
  const [error, setError] = useState('');
  const [sendLoading, setSendLoading] = useState(false);
  const [verifyLoading, setVerifyLoading] = useState(false);
  const [modeLoading, setModeLoading] = useState(false);

  const apiBaseRaw = (import.meta.env.VITE_API_URL as string | undefined) || '/api/v2';
  const apiBase = apiBaseRaw.endsWith('/') ? apiBaseRaw.slice(0, -1) : apiBaseRaw;
  const resolvedMeta: MetaResponse = {
    ...defaultMeta,
    ...meta,
    defaults: {
      ...defaultMeta.defaults,
      ...(meta?.defaults || {}),
    },
    response_codes: meta?.response_codes || defaultMeta.response_codes,
  };

  useEffect(() => {
    let ignore = false;
    const load = async () => {
      try {
        const res = await fetch(`${apiBase}/auth/otp/test/meta`);
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          if (!ignore) {
            setMeta(defaultMeta);
            setError(data?.detail || 'Could not load SMS test metadata. Using fallback values.');
          }
          return;
        }
        if (!ignore) setMeta(data);
      } catch {
        if (!ignore) {
          setMeta(defaultMeta);
          setError('Could not load SMS test metadata. Using fallback values.');
        }
      }
    };
    void load();
    return () => {
      ignore = true;
    };
  }, [apiBase]);

  const responseRows = useMemo(() => {
    return Object.entries(resolvedMeta.response_codes).sort((a, b) => Number(a[0]) - Number(b[0]));
  }, [resolvedMeta]);

  const sendOtp = async () => {
    setError('');
    setSendResponse(null);
    setVerifyResponse(null);
    setSendLoading(true);
    try {
      const res = await fetch(`${apiBase}/auth/otp/test/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone }),
      });
      const data = await res.json().catch(() => ({}));
      setSendResponse({ status: res.status, body: data });
      if (!res.ok) {
        setError(data?.detail || 'Failed to send OTP.');
      }
    } catch {
      setError('Network issue while sending OTP.');
    } finally {
      setSendLoading(false);
    }
  };

  const verifyOtp = async () => {
    setError('');
    setVerifyResponse(null);
    setVerifyLoading(true);
    try {
      const res = await fetch(`${apiBase}/auth/otp/test/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, otp }),
      });
      const data = await res.json().catch(() => ({}));
      setVerifyResponse({ status: res.status, body: data });
      if (!res.ok) {
        setError(data?.detail || 'Failed to verify OTP.');
      }
    } catch {
      setError('Network issue while verifying OTP.');
    } finally {
      setVerifyLoading(false);
    }
  };

  const toggleMode = async (liveEnabled: boolean) => {
    setError('');
    setModeLoading(true);
    try {
      const res = await fetch(`${apiBase}/auth/otp/test/mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ live_enabled: liveEnabled }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data?.detail || 'Failed to update SMS mode.');
        return;
      }
      setMeta((prev) => ({
        ...(prev || defaultMeta),
        sms_test_live_enabled: !!data?.sms_test_live_enabled,
      }));
    } catch {
      setError('Network issue while updating SMS mode.');
    } finally {
      setModeLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-10">
      <div className="mx-auto max-w-5xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm md:p-10">
        <h1 className="text-3xl font-bold text-slate-900">SMS API Testing</h1>
        <p className="mt-2 text-sm text-slate-600">
          This page is isolated from user signup flows and is intended only for Message Central OTP testing.
        </p>
        <div className={`mt-4 rounded-xl border px-4 py-3 text-sm ${resolvedMeta.sms_test_live_enabled ? 'border-amber-200 bg-amber-50 text-amber-900' : 'border-emerald-200 bg-emerald-50 text-emerald-900'}`}>
          {resolvedMeta.sms_test_live_enabled
            ? 'Live SMS mode is ON. Each test OTP may incur cost.'
            : 'Safe mode is ON. No SMS is sent. Use OTP 123456 to test verification.'}
        </div>
        <div className="mt-3 flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
          <div>
            <p className="text-sm font-semibold text-slate-900">SMS Mode</p>
            <p className="text-xs text-slate-600">Toggle between paid live SMS and free safe-mode mock OTP.</p>
          </div>
          <button
            type="button"
            disabled={modeLoading}
            onClick={() => toggleMode(!resolvedMeta.sms_test_live_enabled)}
            className={`relative inline-flex h-7 w-14 items-center rounded-full transition ${resolvedMeta.sms_test_live_enabled ? 'bg-amber-500' : 'bg-emerald-600'} ${modeLoading ? 'opacity-60' : ''}`}
            aria-pressed={resolvedMeta.sms_test_live_enabled}
            aria-label="Toggle SMS mode"
          >
            <span className={`inline-block h-5 w-5 transform rounded-full bg-white transition ${resolvedMeta.sms_test_live_enabled ? 'translate-x-8' : 'translate-x-1'}`} />
          </button>
        </div>

        <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
          <section className="rounded-2xl border border-slate-200 p-5">
            <h2 className="text-lg font-semibold text-slate-900">Send OTP</h2>
            <div className="mt-4 space-y-4">
              <Field label="Recipient Number">
                <input className="input" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+91XXXXXXXXXX" />
              </Field>
              <Field label="Message Preview">
                <textarea className="input min-h-[96px] py-3" value={resolvedMeta.message_preview} readOnly />
              </Field>
              <Field label="Brand Name">
                <input className="input" value={resolvedMeta.brand_name} readOnly />
              </Field>
              <Field label="Customer ID">
                <input className="input" value={resolvedMeta.defaults.customer_id} readOnly />
              </Field>
              <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
                <Field label="OTP Expiry">
                  <input className="input" value={`${resolvedMeta.defaults.otp_expiry_seconds} seconds`} readOnly />
                </Field>
                <Field label="Resend Cooldown">
                  <input className="input" value={`${resolvedMeta.defaults.otp_resend_cooldown_seconds} seconds`} readOnly />
                </Field>
                <Field label="Max Attempts">
                  <input className="input" value={`${resolvedMeta.defaults.otp_max_attempts} attempts`} readOnly />
                </Field>
              </div>
              <button type="button" onClick={sendOtp} disabled={sendLoading} className="btn-primary w-full">
                {sendLoading ? 'Sending...' : 'Send Test OTP'}
              </button>
            </div>
          </section>

          <section className="rounded-2xl border border-slate-200 p-5">
            <h2 className="text-lg font-semibold text-slate-900">Verify OTP</h2>
            <div className="mt-4 space-y-4">
              <Field label="OTP Code">
                <input className="input" value={otp} onChange={(e) => setOtp(e.target.value)} placeholder="Enter received OTP" />
              </Field>
              <button type="button" onClick={verifyOtp} disabled={verifyLoading} className="btn-secondary w-full">
                {verifyLoading ? 'Verifying...' : 'Verify Test OTP'}
              </button>
              {error && <p className="text-sm text-red-600">{error}</p>}

              <div>
                <h3 className="text-sm font-semibold text-slate-900">Send Response</h3>
                <pre className="response-box mt-2">{JSON.stringify(sendResponse, null, 2) || 'No send response yet.'}</pre>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-slate-900">Verify Response</h3>
                <pre className="response-box mt-2">{JSON.stringify(verifyResponse, null, 2) || 'No verify response yet.'}</pre>
              </div>
            </div>
          </section>
        </div>

        <section className="mt-8 rounded-2xl border border-slate-200 p-5">
          <h2 className="text-lg font-semibold text-slate-900">Available Response Codes</h2>
          <p className="mt-1 text-sm text-slate-600">These are the Message Central response codes currently surfaced by the testing flow.</p>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-left text-slate-500">
                  <th className="px-3 py-2">Code</th>
                  <th className="px-3 py-2">Meaning</th>
                </tr>
              </thead>
              <tbody>
                {responseRows.map(([code, label]) => (
                  <tr key={code} className="border-b border-slate-100">
                    <td className="px-3 py-2 font-semibold text-slate-900">{code}</td>
                    <td className="px-3 py-2 text-slate-700">{label}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>

      <style>{`
        .input {
          width: 100%;
          border: 1px solid #cbd5e1;
          border-radius: 10px;
          min-height: 42px;
          padding: 0 12px;
          font-size: 14px;
          color: #0f172a;
          background: #ffffff;
        }
        .btn-primary {
          border: none;
          border-radius: 12px;
          min-height: 46px;
          font-size: 15px;
          font-weight: 700;
          color: #ffffff;
          background: #0f766e;
        }
        .btn-secondary {
          border: 1px solid #94a3b8;
          border-radius: 12px;
          min-height: 46px;
          font-size: 15px;
          font-weight: 700;
          color: #0f172a;
          background: #f8fafc;
        }
        .response-box {
          min-height: 160px;
          overflow: auto;
          border-radius: 12px;
          background: #0f172a;
          color: #e2e8f0;
          padding: 12px;
          font-size: 12px;
          line-height: 1.45;
        }
      `}</style>
    </main>
  );
};

const Field: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
  <label className="block">
    <span className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-600">{label}</span>
    {children}
  </label>
);

export default SmsApiTestPage;
