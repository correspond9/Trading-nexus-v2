export type ThemeMode = 'light' | 'dark';

export type ThemeConfig = Record<string, unknown>;

export type ThemeDefinitions = {
  light: ThemeConfig;
  dark: ThemeConfig;
};

type ThemePresetRow = {
  preset_name?: string;
  mode?: string;
  config?: ThemeConfig;
  is_default?: boolean;
};

type ThemeDefinitionsApiResponse = {
  presets?: ThemePresetRow[];
};

const THEME_DEFS_KEY = 'tn_theme_definitions';
const THEME_MODE_KEY = 'tn_theme_mode';

function normalizeMode(value: unknown): ThemeMode {
  const mode = String(value || '').trim().toLowerCase();
  return mode === 'light' ? 'light' : 'dark';
}

function asThemeDefinitions(input: unknown): ThemeDefinitions {
  const parseConfigValue = (raw: unknown): ThemeConfig => {
    if (raw && typeof raw === 'object') return raw as ThemeConfig;
    if (typeof raw === 'string') {
      try {
        const parsed = JSON.parse(raw);
        if (parsed && typeof parsed === 'object') return parsed as ThemeConfig;
      } catch {
        // ignore invalid JSON
      }
    }
    return {};
  };

  if (input && typeof input === 'object') {
    const maybe = input as Partial<ThemeDefinitions> & ThemeDefinitionsApiResponse;

    if (maybe.light && maybe.dark && typeof maybe.light === 'object' && typeof maybe.dark === 'object') {
      return { light: maybe.light as ThemeConfig, dark: maybe.dark as ThemeConfig };
    }

    if (Array.isArray(maybe.presets)) {
      const lightPresets = maybe.presets.filter(p => (p?.mode || '').toLowerCase() === 'light');
      const darkPresets = maybe.presets.filter(p => (p?.mode || '').toLowerCase() === 'dark');

      const pick = (rows: ThemePresetRow[]) => {
        const preferred = rows.find(r => r?.is_default);
        if (preferred) return parseConfigValue(preferred.config);
        return parseConfigValue(rows[0]?.config);
      };

      return {
        light: pick(lightPresets),
        dark: pick(darkPresets),
      };
    }
  }

  return { light: {}, dark: {} };
}

function toCssVarName(key: string): string {
  const trimmed = key.trim();
  if (!trimmed) return '';

  if (trimmed.startsWith('--')) return trimmed;

  // Backend theme JSON uses keys like nm_shadow; CSS uses --nm-shadow.
  const kebab = trimmed.replace(/_/g, '-');
  return `--${kebab}`;
}

function hexToRgbTriplet(hex: string): string | null {
  const raw = hex.trim().replace(/^#/, '');
  if (!/^[0-9a-fA-F]{6}$/.test(raw)) return null;
  const r = parseInt(raw.slice(0, 2), 16);
  const g = parseInt(raw.slice(2, 4), 16);
  const b = parseInt(raw.slice(4, 6), 16);
  return `${r} ${g} ${b}`;
}

export function storeThemeDefinitions(defs: unknown): ThemeDefinitions {
  const normalized = asThemeDefinitions(defs);
  try {
    localStorage.setItem(THEME_DEFS_KEY, JSON.stringify(normalized));
  } catch {
    // ignore quota/disabled storage
  }
  return normalized;
}

export function getStoredThemeDefinitions(): ThemeDefinitions {
  try {
    const raw = localStorage.getItem(THEME_DEFS_KEY);
    if (!raw) return { light: {}, dark: {} };
    return asThemeDefinitions(JSON.parse(raw));
  } catch {
    return { light: {}, dark: {} };
  }
}

export function storeThemeMode(mode: unknown): ThemeMode {
  const normalized = normalizeMode(mode);
  try {
    localStorage.setItem(THEME_MODE_KEY, normalized);
  } catch {
    // ignore
  }
  return normalized;
}

export function getStoredThemeMode(): ThemeMode {
  try {
    return normalizeMode(localStorage.getItem(THEME_MODE_KEY));
  } catch {
    return 'dark';
  }
}

export function applyThemeConfig(config: ThemeConfig, mode: unknown = 'dark'): void {
  const normalizedMode = normalizeMode(mode);

  // Enable theme-aware Tailwind overrides in styles.css
  document.documentElement.setAttribute('data-theme', normalizedMode);

  if (!config || typeof config !== 'object') return;

  for (const [key, value] of Object.entries(config)) {
    if (value === undefined || value === null) continue;

    const cssVar = toCssVarName(key);
    if (!cssVar) continue;

    // Most values are strings (colors) or numbers.
    const cssValue = typeof value === 'number' ? String(value) : String(value);
    document.documentElement.style.setProperty(cssVar, cssValue);

    // Keep the rgb variants in sync for neumorphic shadows.
    if (cssVar === '--nm-shadow') {
      const rgb = hexToRgbTriplet(cssValue);
      if (rgb) document.documentElement.style.setProperty('--nm-shadow-rgb', rgb);
    }
    if (cssVar === '--nm-highlight') {
      const rgb = hexToRgbTriplet(cssValue);
      if (rgb) document.documentElement.style.setProperty('--nm-highlight-rgb', rgb);
    }
  }
}

export function applyThemeFromStorage(): void {
  const defs = getStoredThemeDefinitions();
  const mode = getStoredThemeMode();
  const cfg = mode === 'light' ? defs.light : defs.dark;
  applyThemeConfig(cfg, mode);
}
