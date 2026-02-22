import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './styles.css'
import {
  applyThemeConfig,
  applyThemeFromStorage,
  getStoredThemeDefinitions,
  storeThemeDefinitions,
  storeThemeMode,
} from './utils/themeManager'

// Apply cached theme immediately, then hydrate from API.
async function initTheme() {
  applyThemeFromStorage();

  try {
    const defsRes = await fetch('/api/v2/theme/definitions');
    if (defsRes.ok) {
      const defs = await defsRes.json();
      const stored = storeThemeDefinitions(defs);
      const mode = localStorage.getItem('tn_theme_mode') || 'dark';
      applyThemeConfig(stored[mode === 'light' ? 'light' : 'dark'], mode);
    }
  } catch {
    // Keep cached theme if API fails.
  }

  try {
    const token = localStorage.getItem('authToken');
    if (token) {
      const meRes = await fetch('/api/v2/theme/me', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (meRes.ok) {
        const data = await meRes.json();
        const mode = storeThemeMode(data?.theme_mode || 'dark');
        const defs = getStoredThemeDefinitions();
        applyThemeConfig(defs[mode], mode);
      }
    }
  } catch {
    // Ignore profile fetch errors.
  }
}

initTheme();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
