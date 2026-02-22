import { useEffect, useMemo, useState } from 'react';
import ThemeCustomizer from './theme/ThemeCustomizer';
import { apiService } from '../services/apiService';
import { storeThemeDefinitions } from '../utils/themeManager';

type ThemeMode = 'light' | 'dark';
type ThemeConfig = Record<string, unknown>;

type ThemePreset = {
  preset_name: string;
  mode: ThemeMode;
  config: unknown;
  is_default: boolean;
};

function parseConfig(raw: unknown): ThemeConfig {
  if (raw && typeof raw === 'object' && !Array.isArray(raw)) return raw as ThemeConfig;
  if (typeof raw === 'string') {
    try {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) return parsed as ThemeConfig;
    } catch {
      return {};
    }
  }
  return {};
}

function toCssConfig(config: ThemeConfig): ThemeConfig {
  const out: ThemeConfig = {};
  for (const [key, value] of Object.entries(config || {})) {
    out[key.replace(/-/g, '_')] = value;
  }
  return out;
}

export default function ThemeManager() {
  const [presets, setPresets] = useState<ThemePreset[]>([]);
  const [selectedLight, setSelectedLight] = useState('');
  const [selectedDark, setSelectedDark] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');

  const lightPresets = useMemo(() => presets.filter((p) => p.mode === 'light'), [presets]);
  const darkPresets = useMemo(() => presets.filter((p) => p.mode === 'dark'), [presets]);

  useEffect(() => {
    loadDefs();
  }, []);

  async function loadDefs() {
    setLoading(true);
    setMsg('');
    try {
      const data = await apiService.get('/theme/definitions');
      const list = Array.isArray(data?.presets) ? (data.presets as ThemePreset[]) : [];
      setPresets(list);

      const light = list.find((p) => p.mode === 'light' && p.is_default) || list.find((p) => p.mode === 'light');
      const dark = list.find((p) => p.mode === 'dark' && p.is_default) || list.find((p) => p.mode === 'dark');
      setSelectedLight(light?.preset_name || '');
      setSelectedDark(dark?.preset_name || '');
    } catch (e) {
      setMsg((e as Error)?.message || 'Failed to load theme presets.');
    } finally {
      setLoading(false);
    }
  }

  async function saveMapping() {
    if (!selectedLight || !selectedDark) {
      setMsg('Select both light and dark preset mappings.');
      return;
    }

    setSaving(true);
    setMsg('');
    try {
      const next = presets.map((p) => {
        if (p.mode === 'light') return { ...p, is_default: p.preset_name === selectedLight };
        return { ...p, is_default: p.preset_name === selectedDark };
      });

      await apiService.put('/theme/definitions', next.map((p) => ({
        preset_name: p.preset_name,
        mode: p.mode,
        config: parseConfig(p.config),
        is_default: p.is_default,
      })));

      setPresets(next);

      const lightCfg = parseConfig(next.find((p) => p.mode === 'light' && p.is_default)?.config);
      const darkCfg = parseConfig(next.find((p) => p.mode === 'dark' && p.is_default)?.config);
      storeThemeDefinitions({ light: toCssConfig(lightCfg), dark: toCssConfig(darkCfg) });

      setMsg('Light/Dark toggle mapping saved. Trade page button will use these presets.');
    } catch (e) {
      setMsg((e as Error)?.message || 'Failed to save mapping.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={{ padding: 12 }}>
      <div style={{ border: '1px solid var(--border)', background: 'var(--surface)', borderRadius: 10, padding: 12, marginBottom: 16 }}>
        <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 8, color: 'var(--text)' }}>Trade Toggle Preset Mapping</div>
        <div style={{ color: 'var(--muted)', fontSize: 13, marginBottom: 10 }}>
          Set which presets the Trade page light/dark toggle switches between.
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto auto', gap: 8, alignItems: 'end' }}>
          <label style={{ display: 'grid', gap: 4, fontSize: 12, color: 'var(--muted)' }}>
            Light Preset
            <select value={selectedLight} onChange={(e) => setSelectedLight(e.target.value)} style={{ border: '1px solid var(--border)', background: 'var(--surface2)', color: 'var(--text)', borderRadius: 8, padding: '8px 10px' }}>
              <option value="">Select</option>
              {lightPresets.map((p) => <option key={p.preset_name} value={p.preset_name}>{p.preset_name}</option>)}
            </select>
          </label>

          <label style={{ display: 'grid', gap: 4, fontSize: 12, color: 'var(--muted)' }}>
            Dark Preset
            <select value={selectedDark} onChange={(e) => setSelectedDark(e.target.value)} style={{ border: '1px solid var(--border)', background: 'var(--surface2)', color: 'var(--text)', borderRadius: 8, padding: '8px 10px' }}>
              <option value="">Select</option>
              {darkPresets.map((p) => <option key={p.preset_name} value={p.preset_name}>{p.preset_name}</option>)}
            </select>
          </label>

          <button type="button" onClick={loadDefs} disabled={loading || saving} style={{ border: '1px solid var(--border)', background: 'var(--surface2)', color: 'var(--text)', borderRadius: 8, padding: '8px 10px', cursor: 'pointer' }}>
            {loading ? 'Loading...' : 'Refresh'}
          </button>

          <button type="button" onClick={saveMapping} disabled={loading || saving} style={{ border: '1px solid #1d4ed8', background: '#2563eb', color: '#fff', borderRadius: 8, padding: '8px 12px', cursor: 'pointer' }}>
            {saving ? 'Saving...' : 'Save Mapping'}
          </button>
        </div>

        {msg && <div style={{ marginTop: 10, fontSize: 12, color: 'var(--text)' }}>{msg}</div>}
      </div>

      <ThemeCustomizer />
    </div>
  );
}
