import React, { useEffect, useState } from 'react';
import { apiService } from '../../services/apiService';

// Import all theme components
import { useThemeLogic } from './ThemeLogic';
import ButtonSettings from './ButtonSettings';
import InputSettings from './InputSettings';
import GlassCardSettings from './GlassCardSettings';
import SidebarSettings from './SidebarSettings';
import BackgroundOptions from './BackgroundOptions';
import { ThemeActions, Notification } from './ThemeActions';
import { GlobalControls } from './GlobalControls';
import { GlobalColorControls } from './GlobalColorControls';

const parseConfig = (raw) => {
  if (raw && typeof raw === 'object') return raw;
  if (typeof raw === 'string') {
    try { return JSON.parse(raw); } catch { return {}; }
  }
  return {};
};

const toThemeDefinitionConfig = (themeConfig, componentSettings) => ({
  bg: themeConfig.backgroundColor,
  surface: themeConfig.glassCardColor || themeConfig.backgroundColor,
  surface2: themeConfig.sidebarColor || themeConfig.logoBackground || themeConfig.backgroundColor,
  border: componentSettings?.inputs?.borderColor || '#cbd5e1',
  text: themeConfig.textColor,
  muted: themeConfig.bodyColor || themeConfig.textColor,
  accent: componentSettings?.buttons?.backgroundColor || themeConfig.logoBackground || '#3b82f6',
  nm_shadow: themeConfig.shadowDark,
  nm_highlight: themeConfig.shadowLight,
  customizer_theme_config_json: JSON.stringify(themeConfig),
  customizer_component_settings_json: JSON.stringify(componentSettings),
});

const toCustomizerState = (config = {}) => {
  const parsed = parseConfig(config);
  let customTheme = null;
  let customComponents = null;

  if (typeof parsed.customizer_theme_config_json === 'string') {
    try { customTheme = JSON.parse(parsed.customizer_theme_config_json); } catch {}
  }
  if (typeof parsed.customizer_component_settings_json === 'string') {
    try { customComponents = JSON.parse(parsed.customizer_component_settings_json); } catch {}
  }

  if (customTheme && customComponents) {
    return { themeConfig: customTheme, componentSettings: customComponents };
  }

  return {
    themeConfig: {
      backgroundColor: parsed.bg || '#e0e0e0',
      glassCardColor: parsed.surface || '#ffffff',
      sidebarColor: parsed.surface2 || '#0f172a',
      textColor: parsed.text || '#333333',
      bodyColor: parsed.muted || '#666666',
      logoBackground: parsed.accent || '#0f172a',
      buttonTextColor: '#ffffff',
      shadowLight: parsed.nm_highlight || '#ffffff',
      shadowDark: parsed.nm_shadow || '#5a5a5a',
    },
    componentSettings: null,
  };
};

export default function ThemeCustomizer() {
  const [notification, setNotification] = useState(null);
  const [activeTab, setActiveTab] = useState('buttons');
  const [selectedTheme, setSelectedTheme] = useState('Custom Theme');
  const [themeName, setThemeName] = useState('Custom Theme');
  const [savedThemes, setSavedThemes] = useState([]);
  const [persistMode, setPersistMode] = useState('light');
  const [definitions, setDefinitions] = useState([]);

  const {
    themeConfig,
    setThemeConfig,
    componentSettings,
    setComponentSettings,
    themes,
    applyThemeGlobally,
    getThemePreset
  } = useThemeLogic();

  const fontOptions = [
    'Inter, system-ui, sans-serif',
    'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
    'Arial, Helvetica, sans-serif',
    'Helvetica Neue, Helvetica, Arial, sans-serif',
    'Roboto, Arial, sans-serif',
    'Work Sans, Arial, sans-serif',
    'Open Sans, Arial, sans-serif',
    'Lato, Arial, sans-serif',
    'Poppins, Arial, sans-serif',
    'Montserrat, Arial, sans-serif',
    'Nunito, Arial, sans-serif',
    'Raleway, Arial, sans-serif',
    'Rubik, Arial, sans-serif',
    'Manrope, Arial, sans-serif',
    'DM Sans, Arial, sans-serif',
    'Ubuntu, Arial, sans-serif',
    'Noto Sans, Arial, sans-serif',
    'Source Sans Pro, Arial, sans-serif',
    'PT Sans, Arial, sans-serif',
    'Merriweather, Georgia, serif',
    'Playfair Display, Georgia, serif',
    'Lora, Georgia, serif',
    'Libre Baskerville, Georgia, serif',
    'Cormorant Garamond, Georgia, serif',
    'Crimson Text, Georgia, serif',
    'Georgia, Times New Roman, serif',
    'Times New Roman, Times, serif',
    'Trebuchet MS, Verdana, sans-serif',
    'Verdana, Geneva, sans-serif',
    'Tahoma, Arial, sans-serif',
    'Bebas Neue, Impact, sans-serif',
    'Oswald, Arial, sans-serif',
    'Cabin, Arial, sans-serif',
    'Quicksand, Arial, sans-serif',
    'Josefin Sans, Arial, sans-serif',
    'Alegreya Sans, Arial, sans-serif',
    'Fjalla One, Arial, sans-serif',
    'Dancing Script, cursive',
    'Satisfy, cursive',
    'Great Vibes, cursive',
    'Courier New, Courier, monospace',
    'Fira Code, Consolas, monospace',
    'JetBrains Mono, Consolas, monospace',
    'Source Code Pro, Consolas, monospace',
    'IBM Plex Mono, Consolas, monospace',
    'Space Mono, Consolas, monospace',
    'Pacifico, cursive'
  ];

  const fontWeightOptions = ['300', '400', '500', '600', '700', '800'];

  const showNotification = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  useEffect(() => {
    const loadDefinitions = async () => {
      try {
        const res = await apiService.get('/theme/definitions');
        const presets = Array.isArray(res?.presets) ? res.presets : [];
        setDefinitions(presets);
        setSavedThemes(presets.map((p) => ({
          name: `${p.preset_name} (${p.mode})`,
          preset_name: p.preset_name,
          mode: p.mode,
          config: parseConfig(p.config),
        })));
      } catch (_e) {
        try {
          const parsed = JSON.parse(localStorage.getItem('savedThemes') || '[]');
          setSavedThemes(Array.isArray(parsed) ? parsed : []);
        } catch (_fallbackError) {
          setSavedThemes([]);
        }
      }
    };

    loadDefinitions();
  }, []);

  const applyTheme = (themeName) => {
    const preset = getThemePreset ? getThemePreset(themeName) : null;
    if (preset?.config) {
      setThemeConfig(preset.config);
      if (preset.componentSettings) {
        setComponentSettings(preset.componentSettings);
      }
      setSelectedTheme(themeName);
      setThemeName(themeName);
      showNotification(`${themeName} theme applied successfully!`);
    }
  };

  const handleSaveNamedTheme = async () => {
    const normalizedName = (themeName || '').trim();
    if (!normalizedName) {
      showNotification('Please enter a theme name before saving.', 'error');
      return;
    }

    const payload = [{
      preset_name: normalizedName,
      mode: persistMode,
      config: toThemeDefinitionConfig(themeConfig, componentSettings),
      is_default: false,
    }];

    try {
      await apiService.put('/theme/definitions', payload);

      const res = await apiService.get('/theme/definitions');
      const presets = Array.isArray(res?.presets) ? res.presets : [];
      setDefinitions(presets);
      setSavedThemes(presets.map((p) => ({
        name: `${p.preset_name} (${p.mode})`,
        preset_name: p.preset_name,
        mode: p.mode,
        config: parseConfig(p.config),
      })));

      setSelectedTheme(normalizedName);
      showNotification(`Theme "${normalizedName}" saved to backend (${persistMode}).`, 'success');
    } catch (_err) {
      showNotification('Failed to save theme to backend.', 'error');
    }
  };

  const handleLoadSavedTheme = (nameToLoad) => {
    const target = savedThemes.find((item) => item?.name === nameToLoad);
    if (!target) {
      showNotification('Saved theme not found.', 'error');
      return;
    }

    const next = toCustomizerState(target.config);
    if (next.themeConfig) {
      setThemeConfig((prev) => ({ ...prev, ...next.themeConfig }));
    }
    if (next.componentSettings) {
      setComponentSettings(next.componentSettings);
    }
    setPersistMode(target.mode || 'light');
    setSelectedTheme(target.preset_name || target.name);
    setThemeName(target.preset_name || target.name);
    showNotification(`Theme "${target.name}" loaded.`, 'success');
  };

  const handleDeleteSavedTheme = (nameToDelete) => {
    showNotification('Delete is not supported by current backend theme API.', 'error');
  };

  const handleApplyThemeGlobally = async () => {
    try {
      await applyThemeGlobally();
      showNotification('Theme applied to the whole website.', 'success');
    } catch (_error) {
      showNotification('Failed to apply theme globally.', 'error');
    }
  };

  const renderComponentSettings = () => {
    switch(activeTab) {
      case 'buttons':
        return (
          <ButtonSettings
            settings={componentSettings.buttons}
            onChange={(newSettings) => setComponentSettings({...componentSettings, buttons: newSettings})}
            fontOptions={fontOptions}
            fontWeightOptions={fontWeightOptions}
          />
        );
      case 'inputs':
        return (
          <InputSettings
            settings={componentSettings.inputs}
            onChange={(newSettings) => setComponentSettings({...componentSettings, inputs: newSettings})}
            fontOptions={fontOptions}
            fontWeightOptions={fontWeightOptions}
          />
        );
      case 'glassCards':
        return (
          <GlassCardSettings
            settings={componentSettings.glassCards}
            onChange={(newSettings) => setComponentSettings({...componentSettings, glassCards: newSettings})}
            fontOptions={fontOptions}
            fontWeightOptions={fontWeightOptions}
          />
        );
      case 'sidebar':
        return (
          <SidebarSettings
            settings={componentSettings.sidebar}
            onChange={(newSettings) => setComponentSettings({...componentSettings, sidebar: newSettings})}
            fontOptions={fontOptions}
            fontWeightOptions={fontWeightOptions}
          />
        );
      default:
        return null;
    }
  };

  const renderPreview = () => {
    switch(activeTab) {
      case 'buttons':
        return (
          <>
            <button className="w-full px-3 py-2 rounded-lg text-sm font-medium">
              Sample Button
            </button>
            <button className="w-full px-3 py-2 rounded-lg text-sm font-medium">
              Another Button
            </button>
          </>
        );
      case 'inputs':
        return (
          <>
            <input 
              type="text" 
              placeholder="Text input..." 
              className="w-full px-3 py-2 rounded-lg text-sm"
            />
            <select className="w-full px-3 py-2 rounded-lg text-sm">
              <option>Select option</option>
              <option>Option 1</option>
              <option>Option 2</option>
            </select>
          </>
        );
      case 'glassCards':
        return (
          <>
            <div className="p-3 rounded-lg text-center text-sm glass-card">
              <div className="font-medium">Glass Card 1</div>
              <div className="text-xs opacity-75">Sample content</div>
            </div>
            <div className="p-3 rounded-lg text-center text-sm glass-card">
              <div className="font-medium">Glass Card 2</div>
              <div className="text-xs opacity-75">Another sample</div>
            </div>
          </>
        );
      case 'sidebar':
        return (
          <div className="p-3 rounded-lg text-sm">
            <div className="font-medium mb-2">Sidebar Menu</div>
            <div className="space-y-1 text-xs">
              <div className="p-1 rounded hover:bg-white/10 cursor-pointer">Menu Item 1</div>
              <div className="p-1 rounded hover:bg-white/10 cursor-pointer">Menu Item 2</div>
              <div className="p-1 rounded hover:bg-white/10 cursor-pointer">Menu Item 3</div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Theme Customization</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column */}
          <div className="space-y-6">
            <div className="bg-white/10 backdrop-blur-xl border border-white/10 rounded-2xl p-4 glass-card">
              <h2 className="text-lg font-semibold mb-3">Theme Selection</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {Object.keys(themes).map(theme => (
                  <button
                    key={theme}
                    onClick={() => applyTheme(theme)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      selectedTheme === theme 
                        ? 'bg-blue-500 text-white' 
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {theme}
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-xl border border-white/10 rounded-2xl p-4 glass-card">
              <h2 className="text-lg font-semibold mb-3">Component Settings</h2>
              <div className="flex gap-2 mb-4">
                {['buttons', 'inputs', 'glassCards', 'sidebar'].map(tab => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-3 py-1 rounded-lg text-sm font-medium transition-all duration-200 ${
                      activeTab === tab 
                        ? 'bg-blue-500 text-white' 
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}
                  </button>
                ))}
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div>{renderComponentSettings()}</div>
                <div className="bg-white/5 rounded-xl p-3 border border-white/10">
                  <h4 className="text-sm font-medium mb-2 text-gray-600">Live Preview</h4>
                  <div className="space-y-2">{renderPreview()}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            <BackgroundOptions themeConfig={themeConfig} setThemeConfig={setThemeConfig} />
            <GlobalControls themeConfig={themeConfig} onThemeConfigChange={setThemeConfig} />
            <GlobalColorControls themeConfig={themeConfig} onThemeConfigChange={setThemeConfig} />
            <ThemeActions 
              themeConfig={themeConfig} 
              componentSettings={componentSettings} 
              onNotification={showNotification}
              themeName={themeName}
              onThemeNameChange={setThemeName}
              savedThemes={savedThemes}
              onSaveTheme={handleSaveNamedTheme}
              onLoadTheme={handleLoadSavedTheme}
              onDeleteTheme={handleDeleteSavedTheme}
              onApplyTheme={handleApplyThemeGlobally}
              persistMode={persistMode}
              onPersistModeChange={setPersistMode}
              disableDeleteReason="Current backend has no delete endpoint for theme definitions"
            />
          </div>
        </div>
      </div>

      <Notification notification={notification} />
    </div>
  );
}
