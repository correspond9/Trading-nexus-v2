import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { AppProvider } from './contexts/AppContext';
import ErrorBoundary from './components/core/ErrorBoundary';
import ProtectedRoute from './components/core/ProtectedRoute';
import Layout from './components/core/Layout';

const Login = lazy(() => import('./pages/Login'));
const Trade = lazy(() => import('./pages/Trade'));
const PositionsMIS = lazy(() => import('./pages/PositionsMIS'));
const PositionsNormal = lazy(() => import('./pages/PositionsNormal'));
const PositionsUserwise = lazy(() => import('./pages/PositionsUserwise'));
const Portfolio = lazy(() => import('./pages/Portfolio'));
const PandL = lazy(() => import('./pages/PandL'));
const Users = lazy(() => import('./pages/Users'));
const Payouts = lazy(() => import('./pages/Payouts'));
const Ledger = lazy(() => import('./pages/Ledger'));
const TradeHistory = lazy(() => import('./pages/HistoricOrders'));
const Profile = lazy(() => import('./pages/Profile'));
const SuperAdmin = lazy(() => import('./pages/SuperAdmin'));

const LandingPage = lazy(() => import('./pages/nexus/LandingPage'));
const CourseEnrollPage = lazy(() => import('./pages/nexus/course-enroll'));
const AccountSignupPage = lazy(() => import('./pages/nexus/AccountSignupPage'));
const CrashCourse = lazy(() => import('./pages/nexus/CrashCourse'));
const AboutPage = lazy(() => import('./pages/nexus/AboutPage'));
const FundedProgram = lazy(() => import('./pages/nexus/FundedProgram'));
const Rules = lazy(() => import('./pages/nexus/Rules'));
const Background = lazy(() => import('./components/nexus/Background'));

const Loader = () => (
  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', background: '#0d1117', color: '#e6edf3', fontSize: '16px' }}>
    Loading...
  </div>
);

const NexusPortal = () => {
  const [theme, setTheme] = React.useState(localStorage.getItem('theme') || 'dark');

  React.useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === 'dark' ? 'light' : 'dark');

  return (
    <Suspense fallback={<Loader />}>
      <Background />
      <Routes>
        <Route path="/" element={<LandingPage toggleTheme={toggleTheme} theme={theme} />} />
        <Route path="/landingpage" element={<LandingPage toggleTheme={toggleTheme} theme={theme} />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/course" element={<CrashCourse />} />
        <Route path="/enroll" element={<CourseEnrollPage />} />
        <Route path="/sign-up" element={<AccountSignupPage />} />
        <Route path="/crash-course" element={<CrashCourse />} />
        <Route path="/funded" element={<FundedProgram />} />
        <Route path="/rules" element={<Rules />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
};

export default function App() {
  const isEducationalPortal = window.location.hostname.startsWith('learn.');

  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AuthProvider>
          <AppProvider>
            {isEducationalPortal ? (
              <NexusPortal />
            ) : (
              <Suspense fallback={<Loader />}>
                <Routes>
                  <Route path="/landingpage" element={<LandingPage />} />
                  <Route path="/about" element={<AboutPage />} />
                  <Route path="/course" element={<CrashCourse />} />
                  <Route path="/enroll" element={<CourseEnrollPage />} />
                  <Route path="/sign-up" element={<AccountSignupPage />} />
                  <Route path="/crash-course" element={<CrashCourse />} />
                  <Route path="/funded" element={<FundedProgram />} />
                  <Route path="/rules" element={<Rules />} />
                  <Route path="/login" element={<Login />} />
                  <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
                    <Route index element={<Navigate to="/trade" replace />} />
                    <Route path="/trade" element={<Trade />} />
                    <Route path="/trade/all-positions" element={
                      <ProtectedRoute requiredRoles={['ADMIN', 'SUPER_ADMIN']}><PositionsMIS /></ProtectedRoute>
                    } />
                    <Route path="/all-positions-normal" element={
                      <ProtectedRoute requiredRoles={['ADMIN', 'SUPER_ADMIN']}><PositionsNormal /></ProtectedRoute>
                    } />
                    <Route path="/all-positions-userwise" element={
                      <ProtectedRoute requiredRoles={['ADMIN', 'SUPER_ADMIN']}><PositionsUserwise /></ProtectedRoute>
                    } />
                    <Route path="/pandl" element={
                      <ProtectedRoute requiredRoles={['ADMIN', 'SUPER_ADMIN']}><PandL /></ProtectedRoute>
                    } />
                    <Route path="/users" element={
                      <ProtectedRoute requiredRoles={['ADMIN', 'SUPER_ADMIN']}><Users /></ProtectedRoute>
                    } />
                    <Route path="/payouts" element={
                      <ProtectedRoute requiredRoles={['ADMIN', 'SUPER_ADMIN']}><Payouts /></ProtectedRoute>
                    } />
                    <Route path="/ledger" element={
                      <ProtectedRoute requiredRoles={['ADMIN', 'SUPER_ADMIN']}><Ledger /></ProtectedRoute>
                    } />
                    <Route path="/trade-history" element={
                      <ProtectedRoute requiredRoles={['ADMIN', 'SUPER_ADMIN']}><TradeHistory /></ProtectedRoute>
                    } />
                    <Route path="/profile" element={<Profile />} />
                    <Route path="/portfolio" element={<Portfolio />} />
                    <Route path="/dashboard" element={
                      <ProtectedRoute requiredRoles={['ADMIN', 'SUPER_ADMIN']}><SuperAdmin /></ProtectedRoute>
                    } />
                  </Route>
                  <Route path="*" element={<Navigate to="/trade" replace />} />
                </Routes>
              </Suspense>
            )}
          </AppProvider>
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
