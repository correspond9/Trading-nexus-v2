import React, { useState, useEffect, useRef } from 'react';
import normalizeUnderlying from '../utils/underlying';
import { apiService } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';
import { getLotSize as getConfiguredLotSize } from '../config/tradingConfig';
import OrdersTab from './Orders';
import BasketsTab from './BASKETS';
import WatchlistComponent from './WATCHLIST';
import OptionMatrixComponent from './OPTIONS';
import StraddleMatrix from './STRADDLE';
import PositionsTab from './POSITIONS';
import OrderModal from '../components/OrderModal';

const expiryCache = new Map();
const EXPIRY_CACHE_TTL_MS = 2 * 60 * 1000;

const formatExpiry = (dateStr) => {
  const date = new Date(dateStr);
  const day = date.getDate();
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  return `${day} ${months[date.getMonth()]}`;
};

const parseExpiryDate = (value) => {
  const raw = String(value || '').trim();
  if (!raw) return null;
  const isoMatch = raw.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (isoMatch) {
    const dt = new Date(`${raw}T00:00:00`);
    return Number.isNaN(dt.getTime()) ? null : dt;
  }
  const alt = new Date(raw);
  if (!Number.isNaN(alt.getTime())) return alt;
  const compact = raw.toUpperCase().match(/^(\d{1,2})([A-Z]{3})(\d{2}|\d{4})$/);
  if (compact) {
    const day = Number(compact[1]);
    const monthMap = { JAN: 0, FEB: 1, MAR: 2, APR: 3, MAY: 4, JUN: 5, JUL: 6, AUG: 7, SEP: 8, OCT: 9, NOV: 10, DEC: 11 };
    const month = monthMap[compact[2]];
    const yearNum = Number(compact[3]);
    const year = yearNum < 100 ? (2000 + yearNum) : yearNum;
    if (!Number.isFinite(day) || month === undefined || !Number.isFinite(year)) return null;
    const dt = new Date(year, month, day);
    return Number.isNaN(dt.getTime()) ? null : dt;
  }
  return null;
};

const toIsoDate = (dateObj) => {
  const year = dateObj.getFullYear();
  const month = String(dateObj.getMonth() + 1).padStart(2, '0');
  const day = String(dateObj.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const fetchExpiryDates = async (selectedIndex = 'NIFTY 50') => {
  try {
    const symbol = normalizeUnderlying(selectedIndex);
    const cached = expiryCache.get(symbol);
    if (cached && (Date.now() - cached.ts) < EXPIRY_CACHE_TTL_MS) return cached.value;

    const data = await apiService.get('/options/available/expiries', { underlying: symbol });
    const expiries = Array.isArray(data?.data) ? data.data : [];

    if (!expiries.length) return { displayExpiries: [], isoExpiries: [] };

    const normalized = Array.from(new Set(
      expiries.map((exp) => parseExpiryDate(exp)).filter(Boolean).map((dateObj) => toIsoDate(dateObj))
    )).sort();

    const now = new Date();
    const today = toIsoDate(new Date(now.getFullYear(), now.getMonth(), now.getDate()));
    let currentIndex = normalized.findIndex(exp => exp >= today);
    if (currentIndex === -1) currentIndex = 0;

    const selected = normalized.slice(currentIndex, currentIndex + 2);
    const value = { displayExpiries: selected.map(formatExpiry), isoExpiries: selected };
    expiryCache.set(symbol, { ts: Date.now(), value });
    return value;
  } catch (error) {
    console.error('[TRADE] Error fetching expiries:', error);
    return { displayExpiries: [], isoExpiries: [] };
  }
};

const Trade = () => {
  const { user } = useAuth();
  const isAdmin = user?.role === 'ADMIN' || user?.role === 'SUPER_ADMIN';
  const [leftTab, setLeftTab] = useState('straddle');
  const [rightTab, setRightTab] = useState('orders');
  const [selectedIndex, setSelectedIndex] = useState('NIFTY 50');
  const [expiries, setExpiries] = useState([]);
  const [isoExpiries, setIsoExpiries] = useState([]);
  const [expiry, setExpiry] = useState(null);
  const [isoExpiry, setIsoExpiry] = useState(null);
  const [sortBy, setSortBy] = useState('A-Z');
  const [modalOpen, setModalOpen] = useState(false);
  const [modalOrderData, setModalOrderData] = useState(null);
  const [modalOrderType, setModalOrderType] = useState('BUY');
  const pageRef = useRef(null);

  useEffect(() => {
    try { window.scrollTo({ top: 0, behavior: 'auto' }); } catch { window.scrollTo(0, 0); }
  }, []);

  useEffect(() => {
    const loadExpiries = async () => {
      const expiryData = await fetchExpiryDates(selectedIndex);
      if (Array.isArray(expiryData)) {
        setExpiries(expiryData);
        setIsoExpiries(expiryData);
        if (expiryData.length > 0) { setExpiry(expiryData[0]); setIsoExpiry(expiryData[0]); }
      } else {
        setExpiries(expiryData.displayExpiries);
        setIsoExpiries(expiryData.isoExpiries);
        if (expiryData.displayExpiries.length > 0) {
          setExpiry(expiryData.displayExpiries[0]);
          setIsoExpiry(expiryData.isoExpiries[0]);
        } else {
          setExpiry(null);
          setIsoExpiry(null);
        }
      }
    };
    loadExpiries();
  }, [selectedIndex]);

  const leftTabs = [{ id: 'straddle', name: 'Straddle' }, { id: 'options', name: 'Options' }, { id: 'watchlist', name: 'Watchlist' }];
  const rightTabs = [
    { id: 'orders', name: 'Orders' },
    { id: 'positions', name: 'Positions' },
    { id: 'baskets', name: 'Baskets' },
  ];
  const indices = ['NIFTY 50', 'NIFTY BANK', 'SENSEX'];
  const sortOptions = ['A-Z', '%', 'LTP'];

  const handleOpenOrderModal = (legs) => {
    if (Array.isArray(legs) && legs.length > 0) {
      const firstLeg = legs[0];
      const expiryIso = isoExpiry || expiry;
      const underlyingFromLeg = String(firstLeg?.underlying || '').trim() || normalizeUnderlying(selectedIndex);
      const fallbackLot = getConfiguredLotSize(underlyingFromLeg);
      const resolvedLot = Number(firstLeg?.lotSize || fallbackLot || 1);

      const resolvedSecurityId = firstLeg?.security_id || firstLeg?.securityId || firstLeg?.instrument_token || firstLeg?.instrumentToken || firstLeg?.token || null;
      const resolvedExchangeSegment = firstLeg?.exchange_segment || firstLeg?.exchangeSegment || firstLeg?.exchange || '';

      const normalizedLegs = legs.map((leg) => ({
        ...leg,
        security_id: leg?.security_id || leg?.securityId || leg?.instrument_token || leg?.instrumentToken || leg?.token || null,
        exchange_segment: leg?.exchange_segment || leg?.exchangeSegment || leg?.exchange || '',
        lotSize: leg?.lotSize || resolvedLot,
      }));

      setModalOrderData({
        symbol: firstLeg.symbol,
        action: firstLeg.action,
        ltp: firstLeg.ltp,
        lotSize: resolvedLot,
        lot_size: resolvedLot,
        underlying: underlyingFromLeg,
        expiry: expiryIso,
        expiry_display: expiry,
        security_id: resolvedSecurityId,
        exchange_segment: resolvedExchangeSegment,
        exchange: resolvedExchangeSegment,
        legs: normalizedLegs
      });
      setModalOrderType(firstLeg.action || 'BUY');
      setModalOpen(true);
    }
  };

  const handleOpenOrderModalFromWatchlist = (instrument, side) => {
    if (!instrument) return;
    const resolvedUnderlying = String(instrument?.underlying || '').trim() || normalizeUnderlying(selectedIndex);
    const fallbackLot = getConfiguredLotSize(resolvedUnderlying);
    handleOpenOrderModal([
      {
        symbol: instrument.symbol,
        token: instrument.token,
        exchange_segment: instrument.exchange,
        exchange: instrument.exchange,
        underlying: resolvedUnderlying,
        lotSize: instrument.lotSize || fallbackLot || 1,
        action: side || 'BUY',
      },
    ]);
  };

  const handleCloseModal = () => { setModalOpen(false); setModalOrderData(null); };

  const handleExpiryChange = (newExpiry) => {
    setExpiry(newExpiry);
    const index = expiries.indexOf(newExpiry);
    if (index !== -1 && index < isoExpiries.length) setIsoExpiry(isoExpiries[index]);
  };

  return (
    <div className="w-full min-h-screen" style={{ background: 'var(--bg)', color: 'var(--text)' }} ref={pageRef}>
      <div className="w-full max-w-full mx-auto">
        <div className="flex flex-col lg:flex-row">
          {/* Left Panel */}
          <div className="lg:w-1/3 w-full">
            <div className="flex gap-1 rounded-t-lg p-1" style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>
              {leftTabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setLeftTab(tab.id)}
                  className={`flex-1 px-[1em] py-[0.6em] min-h-[2.4em] leading-tight font-semibold rounded-md transition-colors ${leftTab === tab.id ? 'bg-blue-600 !text-white' : ''}`}
                  style={leftTab !== tab.id ? { background: 'var(--surface2)', color: 'var(--text)', border: '1px solid var(--border)' } : {}}
                >
                  {tab.name}
                </button>
              ))}
            </div>

            {leftTab !== 'watchlist' && (
              <div className="p-2" style={{ background: 'var(--surface)', borderLeft: '1px solid var(--border)', borderRight: '1px solid var(--border)', borderBottom: '1px solid var(--border)' }}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex gap-1">
                    {expiries && expiries.length > 0 ? (
                      expiries.map((exp) => (
                        <button
                          key={exp}
                          onClick={() => handleExpiryChange(exp)}
                          className={`px-2 py-1 text-xs font-medium rounded transition-colors ${expiry === exp ? 'bg-blue-600 !text-white' : ''}`}
                          style={expiry !== exp ? { background: 'var(--surface2)', color: 'var(--text)' } : {}}
                        >
                          {exp}
                        </button>
                      ))
                    ) : (
                      <span className="text-xs px-2 py-1" style={{ color: 'var(--muted)' }}>Loading expiries...</span>
                    )}
                  </div>
                  <div className="flex items-center">
                    <span className="text-xs font-medium mr-2" style={{ color: 'var(--muted)' }}>Sort:</span>
                    <div className="flex gap-1">
                      {sortOptions.map((option) => (
                        <button
                          key={option}
                          onClick={() => setSortBy(option)}
                          className={`px-2 py-1 text-xs font-medium rounded transition-colors ${sortBy === option ? 'bg-blue-600 !text-white' : ''}`}
                          style={sortBy !== option ? { background: 'var(--surface2)', color: 'var(--text)' } : {}}
                        >
                          {option}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="flex items-center">
                  {indices.map((index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedIndex(index)}
                      className={`flex-1 px-2 py-1 text-xs font-medium rounded transition-colors ${selectedIndex === index ? 'bg-blue-600 !text-white' : ''}`}
                      style={selectedIndex !== index ? { background: 'var(--surface2)', color: 'var(--text)' } : {}}
                    >
                      {index}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div
              className={leftTab === 'watchlist' ? 'rounded-b-lg p-0 min-h-[600px]' : 'rounded-b-lg p-2 min-h-[400px]'}
              style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}
            >
              {leftTab === 'straddle' && <StraddleMatrix handleOpenOrderModal={handleOpenOrderModal} selectedIndex={selectedIndex} expiry={isoExpiry} />}
              {leftTab === 'watchlist' && (
                <WatchlistComponent onOpenOrderModal={handleOpenOrderModalFromWatchlist} compact />
              )}
              {leftTab === 'options' && <OptionMatrixComponent handleOpenOrderModal={handleOpenOrderModal} selectedIndex={selectedIndex} expiry={isoExpiry} />}
            </div>
          </div>

          {/* Right Panel */}
          <div className="lg:w-2/3 w-full">
            <div className="rounded-t-lg overflow-hidden" style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>
              <div className="flex gap-1 p-1" style={{ background: 'var(--surface)' }}>
                {rightTabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setRightTab(tab.id)}
                    className={`flex-1 px-[1em] py-[0.6em] min-h-[2.4em] leading-tight font-semibold rounded-md transition-colors ${rightTab === tab.id ? 'bg-blue-600 !text-white' : ''}`}
                    style={rightTab !== tab.id ? { background: 'var(--surface2)', color: 'var(--text)', border: '1px solid var(--border)' } : {}}
                  >
                    {tab.name}
                  </button>
                ))}
              </div>
            </div>
            <div className="rounded-b-lg p-2 min-h-[600px]" style={{ background: 'var(--surface)', borderLeft: '1px solid var(--border)', borderRight: '1px solid var(--border)', borderBottom: '1px solid var(--border)' }}>
              {rightTab === 'positions' && <PositionsTab />}
              {rightTab === 'orders' && <OrdersTab />}
              {rightTab === 'baskets' && <BasketsTab />}
            </div>
          </div>
        </div>
      </div>

      <OrderModal
        isOpen={modalOpen}
        onClose={handleCloseModal}
        orderData={modalOrderData}
        orderType={modalOrderType}
      />
    </div>
  );
};

export default Trade;
