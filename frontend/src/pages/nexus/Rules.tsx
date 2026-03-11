import React from 'react';
import '../../styles/nexus/NeoTheme.css';

const FUNDED_URL = '/funded';

const Rules: React.FC = () => {
  return (
    <div className="rules-page">
      <div className="rules-container">

        <nav className="rules-nav">
          <div className="rules-logo-wrap">
            <img src="/logo.png" alt="TradingNexus" className="rules-logo-img" />
            <div className="rules-logo">TradingNexus</div>
          </div>
          <div className="rules-nav-links">
            <a href="/">Home</a>
            <a href="/funded">Funded Program</a>
            <a href="/rules">Trading Rules</a>
          </div>
        </nav>

        <section className="rules-hero">
          <h1>Trading Rules &amp; <span className="rules-gradient">Risk Framework</span></h1>
          <p>
            TradingNexus provides additional trading capital to traders while maintaining
            strict risk controls to ensure stability of the system. The following framework
            governs how funded trading accounts operate.
          </p>
        </section>

        <div className="rules-sections">

          <section className="rules-card">
            <h2>Capital Allocation Model</h2>
            <p className="rules-muted">
              TradingNexus enables traders to trade with higher capital by allocating
              additional funds to their account.
            </p>
            <div className="rules-allocation-grid">
              <div className="rules-alloc-box">
                <h4>Trader Deposit</h4>
                <p className="rules-amount">₹1,00,000</p>
              </div>
              <div className="rules-alloc-box">
                <h4>TradingNexus Capital</h4>
                <p className="rules-amount">₹4,00,000</p>
              </div>
              <div className="rules-alloc-box rules-alloc-highlight">
                <h4>Total Trading Capital</h4>
                <p className="rules-amount rules-gradient">₹5,00,000</p>
              </div>
            </div>
          </section>

          <section className="rules-card">
            <h2>Risk Monitoring (RMS)</h2>
            <p className="rules-muted">
              TradingNexus maintains a dedicated Risk Management System (RMS) team that
              continuously monitors trading activity. The objective of RMS monitoring is
              to maintain trading discipline and ensure that risk exposure remains within
              acceptable limits.
            </p>
          </section>

          <section className="rules-card">
            <h2>Maximum Loss Protection</h2>
            <p className="rules-muted">
              A strict system-level stop loss is enforced to protect trading capital. If
              the mark-to-market (MTM) loss on live positions reaches{' '}
              <strong>50% of the trader's base capital</strong>, positions may be
              automatically squared off by the system.
            </p>
          </section>

          <section className="rules-card">
            <h2>Capital Stability During the Month</h2>
            <p className="rules-muted">
              Once capital allocation is provided at the beginning of the month, it will
              not be reduced during the same month even if losses occur. Adjustments, if
              any, are applied only during the settlement cycle.
            </p>
          </section>

          <section className="rules-card">
            <h2>Monthly Settlement</h2>
            <p className="rules-muted">
              Final settlement of profits and losses for funded trading accounts is
              calculated on the <strong>last Thursday of every month.</strong>{' '}
              Withdrawals between settlement cycles are not permitted.
            </p>
          </section>

          <section className="rules-card">
            <h2>Profit Policy</h2>
            <p className="rules-muted">
              TradingNexus does not operate on a profit sharing model. Traders retain
              the profits generated through their trading activities.
            </p>
          </section>

          <section className="rules-card">
            <h2>Platform Charges</h2>
            <p className="rules-muted">
              TradingNexus charges a platform fee of{' '}
              <strong>0.005 × turnover</strong> for facilitating trading on the system.
            </p>
            <p className="rules-muted" style={{ marginTop: '16px' }}>
              If no trading activity occurs during a month, no platform charges are applied.
            </p>
          </section>

        </div>

        <section className="rules-cta-section">
          <h2>Start Trading With Higher Capital</h2>
          <a className="rules-cta" href={FUNDED_URL}>
            View Funded Program
          </a>
        </section>

        <footer className="rules-footer">TradingNexus © {new Date().getFullYear()}</footer>
      </div>
    </div>
  );
};

export default Rules;
