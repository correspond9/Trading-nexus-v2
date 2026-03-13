// src/pages/Login.jsx

import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/apiService';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    mobile: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showForgot, setShowForgot] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);
  const [resetMsg, setResetMsg] = useState('');
  const [forgotData, setForgotData] = useState({
    mobile: '',
    otp: '',
    newPassword: '',
    confirmPassword: '',
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const mobileTrimmed = (formData.mobile || '').toString().trim();
    const result = await login({ mobile: mobileTrimmed, password: formData.password });

    if (result.success) {
      navigate('/trade');
    } else {
      setError(result.error || 'Login failed');
    }

    setLoading(false);
  };

  const sendResetOtp = async () => {
    setError('');
    setResetMsg('');
    if (!forgotData.mobile.trim()) {
      setResetMsg('Enter your registered mobile number first.');
      return;
    }

    setResetLoading(true);
    try {
      await apiService.post('/auth/password/forgot/send-otp', { mobile: forgotData.mobile.trim() });
      setResetMsg('OTP sent to your registered mobile number.');
    } catch (err) {
      setResetMsg(err?.message || 'Could not send OTP.');
    } finally {
      setResetLoading(false);
    }
  };

  const resetPassword = async () => {
    setError('');
    setResetMsg('');
    if (!forgotData.mobile.trim() || !forgotData.otp.trim() || !forgotData.newPassword.trim()) {
      setResetMsg('Fill mobile, OTP, and new password.');
      return;
    }
    if (forgotData.newPassword !== forgotData.confirmPassword) {
      setResetMsg('Password and confirm password do not match.');
      return;
    }

    setResetLoading(true);
    try {
      await apiService.post('/auth/password/forgot/reset', {
        mobile: forgotData.mobile.trim(),
        otp: forgotData.otp.trim(),
        new_password: forgotData.newPassword,
      });
      setResetMsg('Password reset successful. You can now sign in with the new password.');
      setShowForgot(false);
      setForgotData({ mobile: '', otp: '', newPassword: '', confirmPassword: '' });
    } catch (err) {
      setResetMsg(err?.message || 'Password reset failed.');
    } finally {
      setResetLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Trading Terminal Login
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Sign in to access your trading account
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div style={{ backgroundColor: '#fee2e2', border: '1px solid #fca5a5', borderRadius: '0.375rem', padding: '1rem' }}>
                <div style={{ fontSize: '0.875rem', color: '#dc2626', fontWeight: 600 }}>{error}</div>
              </div>
            )}

            <div>
              <label htmlFor="mobile" style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#000' }}>
                Mobile Number
              </label>
              <div style={{ marginTop: '0.25rem' }}>
                <input
                  className="tn-login-input"
                  id="mobile"
                  name="mobile"
                  type="tel"
                  required
                  value={formData.mobile}
                  onChange={handleChange}
                  style={{
                    width: '100%',
                    padding: '0.5rem 0.75rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '0.375rem',
                    fontSize: '0.875rem',
                    color: '#000',
                    backgroundColor: '#fff',
                    boxSizing: 'border-box'
                  }}
                  placeholder="Enter your mobile number"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#000' }}>
                Password
              </label>
              <div style={{ marginTop: '0.25rem' }}>
                <input
                  className="tn-login-input"
                  id="password"
                  name="password"
                  type="password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  style={{
                    width: '100%',
                    padding: '0.5rem 0.75rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '0.375rem',
                    fontSize: '0.875rem',
                    color: '#000',
                    backgroundColor: '#fff',
                    boxSizing: 'border-box'
                  }}
                  placeholder="Enter your password"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                style={{
                  width: '100%',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  padding: '0.75rem 1rem',
                  border: 'none',
                  borderRadius: '0.375rem',
                  fontSize: '0.875rem',
                  fontWeight: 700,
                  color: '#fff',
                  backgroundColor: loading ? '#1e40af' : '#2563eb',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.7 : 1,
                  transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => {
                  if (!loading) e.target.style.backgroundColor = '#1d4ed8';
                }}
                onMouseLeave={(e) => {
                  if (!loading) e.target.style.backgroundColor = '#2563eb';
                }}
              >
                {loading ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span style={{ color: '#fff' }}>Signing in...</span>
                  </div>
                ) : (
                  <span style={{ color: '#fff' }}>Sign in</span>
                )}
              </button>
            </div>

            <div className="text-center">
              <button
                type="button"
                onClick={() => {
                  setShowForgot((prev) => !prev);
                  setResetMsg('');
                }}
                style={{ color: '#2563eb', background: 'none', border: 'none', fontSize: '0.875rem', cursor: 'pointer' }}
              >
                {showForgot ? 'Close Forgot Password' : 'Forgot Password?'}
              </button>
            </div>

            {showForgot && (
              <div style={{ border: '1px solid #d1d5db', borderRadius: '0.5rem', padding: '1rem', background: '#f8fafc' }}>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#111827', marginBottom: '0.75rem' }}>
                  Reset Password (User Accounts Only)
                </h3>
                <div style={{ display: 'grid', gap: '0.5rem' }}>
                  <input
                    className="tn-login-input"
                    type="tel"
                    placeholder="Registered mobile"
                    value={forgotData.mobile}
                    onChange={(e) => setForgotData((prev) => ({ ...prev, mobile: e.target.value }))}
                    style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
                  />
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '0.5rem' }}>
                    <input
                      className="tn-login-input"
                      placeholder="OTP"
                      value={forgotData.otp}
                      onChange={(e) => setForgotData((prev) => ({ ...prev, otp: e.target.value }))}
                      style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
                    />
                    <button type="button" onClick={sendResetOtp} disabled={resetLoading} style={{ ...{ padding: '0.5rem 0.75rem', border: 'none', borderRadius: '0.375rem', color: '#fff', background: '#2563eb', fontWeight: 600 } }}>
                      {resetLoading ? 'Sending...' : 'Send OTP'}
                    </button>
                  </div>
                  <input
                    className="tn-login-input"
                    type="password"
                    placeholder="New password"
                    value={forgotData.newPassword}
                    onChange={(e) => setForgotData((prev) => ({ ...prev, newPassword: e.target.value }))}
                    style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
                  />
                  <input
                    className="tn-login-input"
                    type="password"
                    placeholder="Confirm new password"
                    value={forgotData.confirmPassword}
                    onChange={(e) => setForgotData((prev) => ({ ...prev, confirmPassword: e.target.value }))}
                    style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
                  />
                  <button
                    type="button"
                    onClick={resetPassword}
                    disabled={resetLoading}
                    style={{ padding: '0.6rem 0.75rem', border: 'none', borderRadius: '0.375rem', color: '#fff', background: '#0f766e', fontWeight: 700 }}
                  >
                    {resetLoading ? 'Resetting...' : 'Reset Password'}
                  </button>
                  {resetMsg && <p style={{ fontSize: '0.8rem', color: '#334155' }}>{resetMsg}</p>}
                </div>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
