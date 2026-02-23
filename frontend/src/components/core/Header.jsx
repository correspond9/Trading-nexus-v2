import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Sun, Moon } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/apiService';
import {
  applyThemeConfig,
  getStoredThemeDefinitions,
  getStoredThemeMode,
  storeThemeMode,
} from '../../utils/themeManager';

const NAV_ITEMS = [
  { label: 'Trade',       path: '/trade',                          roles: null },
  { label: 'P.MIS',       path: '/trade/all-positions',            roles: ['ADMIN', 'SUPER_ADMIN'] },
  { label: 'P.Normal',    path: '/all-positions-normal',           roles: ['ADMIN', 'SUPER_ADMIN'] },
  { label: 'P.Userwise',  path: '/all-positions-userwise',         roles: ['ADMIN', 'SUPER_ADMIN'] },
  { label: 'Users',       path: '/users',                          roles: ['ADMIN', 'SUPER_ADMIN'] },
  { label: 'Payouts',     path: '/payouts',                        roles: ['ADMIN', 'SUPER_ADMIN'] },
  { label: 'Ledger',      path: '/ledger',                         roles: ['ADMIN', 'SUPER_ADMIN'] },
  { label: 'Trade History', path: '/trade-history',                roles: ['ADMIN', 'SUPER_ADMIN'] },
  { label: 'P&L',         path: '/pandl',                          roles: ['ADMIN', 'SUPER_ADMIN'] },
  { label: 'Dashboard',   path: '/dashboard',                      roles: ['SUPER_ADMIN'] },
];

const Header = () => {
  const { isAuthenticated, user, logout, hasRole } = useAuth();
  const location = useLocation();
  const navigate  = useNavigate();
  const [menuOpen, setMenuOpen] = React.useState(false);
  const displayFirstName = user?.first_name || (user?.name ? String(user.name).trim().split(/\s+/)[0] : '') || user?.mobile || '';
  const [themeMode, setThemeMode] = React.useState(getStoredThemeMode());
  const showThemeToggle = location.pathname.startsWith('/trade') || location.pathname === '/trade-history';

  React.useEffect(() => {
    const handler = (e) => {
      const mode = e?.detail?.mode || getStoredThemeMode();
      setThemeMode(mode === 'light' ? 'light' : 'dark');
    };
    window.addEventListener('tn-theme-change', handler);
    return () => window.removeEventListener('tn-theme-change', handler);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleThemeToggle = async () => {
    const next = themeMode === 'dark' ? 'light' : 'dark';
    setThemeMode(next);
    storeThemeMode(next);
    const defs = getStoredThemeDefinitions();
    applyThemeConfig(defs[next], next);
    window.dispatchEvent(new CustomEvent('tn-theme-change', { detail: { mode: next } }));

    try {
      await apiService.put('/theme/me', { theme_mode: next });
      const userRaw = localStorage.getItem('authUser');
      if (userRaw) {
        const nextUser = JSON.parse(userRaw);
        nextUser.theme_mode = next;
        localStorage.setItem('authUser', JSON.stringify(nextUser));
      }
    } catch (err) {
      console.warn('Could not persist theme preference:', err?.message || err);
    }
  };

  const visibleItems = NAV_ITEMS.filter(item => {
    if (!item.roles) return true;
    return item.roles.some(r => hasRole(r));
  });

  if (!isAuthenticated) return null;

  return (
    <header style={{
      background:   'var(--surface)',
      borderBottom: '1px solid var(--border)',
      position:     'sticky',
      top:           0,
      zIndex:        100,
    }}>
      <div style={{
        display:        'flex',
        alignItems:     'center',
        padding:        '0 16px',
        height:         '48px',
        gap:            '4px',
        overflowX:      'auto',
      }}>
        {/* Logo */}
        <Link to="/trade" style={{ fontWeight: 700, fontSize: '1.1rem', color: 'var(--accent)', textDecoration: 'none', marginRight: '12px', whiteSpace: 'nowrap' }}>
          TN
        </Link>

        {/* Nav links */}
        <nav style={{ display: 'flex', gap: '2px', flex: 1, overflowX: 'auto' }}>
          {visibleItems.map(item => (
            <Link
              key={item.path}
              to={item.path}
              style={{
                padding:       '4px 10px',
                borderRadius:  '5px',
                fontSize:      '0.8rem',
                fontWeight:    location.pathname === item.path ? 600 : 400,
                color:         location.pathname === item.path ? 'var(--accent)' : 'var(--muted)',
                textDecoration:'none',
                whiteSpace:    'nowrap',
                background:    location.pathname === item.path ? 'color-mix(in srgb, var(--accent) 12%, transparent)' : 'transparent',
                transition:    'all 0.15s',
              }}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        {/* User + logout */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginLeft: 'auto' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--muted)', whiteSpace: 'nowrap' }}>
            {displayFirstName}
          </span>
          {showThemeToggle && (
            <button
              onClick={handleThemeToggle}
              className="nm-protrude nm-shadow-nmshadow/25 nm-highlight-nmhighlight/70 rounded-full p-2"
              style={{ background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text)' }}
              aria-label="Toggle theme"
              title={themeMode === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {themeMode === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
            </button>
          )}
          <button
            onClick={() => navigate('/profile')}
            title="Profile"
            style={{
              padding:      '4px 8px',
              background:   'transparent',
              border:       '1px solid var(--border)',
              borderRadius: '5px',
              color:        'var(--muted)',
              fontSize:     '0.9rem',
              cursor:       'pointer',
              display:      'flex',
              alignItems:   'center',
              justifyContent: 'center',
              minWidth:     '30px',
              minHeight:    '24px',
            }}
          >
            👤
          </button>
          <button
            onClick={handleLogout}
            style={{
              padding:      '4px 10px',
              background:   'transparent',
              border:       '1px solid var(--border)',
              borderRadius: '5px',
              color:        'var(--muted)',
              fontSize:     '0.75rem',
              cursor:       'pointer',
            }}
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
