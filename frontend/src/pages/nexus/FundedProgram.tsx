import React from 'react';
import '../../styles/nexus/NeoTheme.css';

const cardStyle: React.CSSProperties = {
  padding: '1.25rem',
  borderRadius: '16px',
  border: '1px solid rgba(255,255,255,0.1)',
  background: 'linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02))',
};

const REGISTER_URL = 'https://learn.tradingnexus.pro/register';

const FundedProgram: React.FC = () => {

  return (
    <div className="nexus-neo-page" style={{ padding: '1rem' }}>
      <main style={{ maxWidth: '1100px', margin: '0 auto', padding: '1rem' }}>
        <nav style={{ ...cardStyle, display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <img src="/logo.png" alt="TradingNexus" style={{ width: '38px', height: '38px', objectFit: 'contain' }} />
            <span style={{ fontWeight: 700, letterSpacing: '0.5px' }}>TradingNexus</span>
          </div>
          <a className="neo-btn-solid-purple" href={REGISTER_URL}>
            Sign Up
          </a>
        </nav>

        <section style={{ ...cardStyle, textAlign: 'center', padding: '2.2rem 1.2rem' }}>
          <div className="neo-badge" style={{ margin: '0 auto 1rem auto', display: 'inline-flex' }}>
            Funded Trader Opportunity
          </div>
          <h1 style={{ fontSize: 'clamp(1.8rem, 5vw, 3rem)', marginBottom: '1rem' }}>
            Become a <span className="text-gradient">Funded Trader</span>
          </h1>
          <p className="muted" style={{ maxWidth: '760px', margin: '0 auto', lineHeight: 1.65 }}>
            TradingNexus is launching a program to discover talented derivatives traders across India.
            Join our <strong>free 2-day derivatives crash course</strong>, where we evaluate discipline,
            strategy quality, and decision-making.
            Top performers may receive the opportunity to trade with
            <strong> 80% capital provided by TradingNexus.</strong>
          </p>
          <div style={{ marginTop: '1.4rem' }}>
            <a className="neo-btn-solid-purple" href={REGISTER_URL}>Sign Up Now</a>
          </div>
        </section>

        <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '0.9rem', marginTop: '1rem' }}>
          <div style={cardStyle}>
            <h3 style={{ marginBottom: '0.45rem' }}>Derivatives Crash Course</h3>
            <p className="muted" style={{ lineHeight: 1.5 }}>A practical 2-day program focused on futures and options execution.</p>
          </div>
          <div style={cardStyle}>
            <h3 style={{ marginBottom: '0.45rem' }}>Skill Evaluation</h3>
            <p className="muted" style={{ lineHeight: 1.5 }}>Live discussions, exercises, and a short performance test.</p>
          </div>
          <div style={cardStyle}>
            <h3 style={{ marginBottom: '0.45rem' }}>Certification</h3>
            <p className="muted" style={{ lineHeight: 1.5 }}>Participants who complete successfully receive a TradingNexus certificate.</p>
          </div>
          <div style={cardStyle}>
            <h3 style={{ marginBottom: '0.45rem' }}>80% Capital Funding</h3>
            <p className="muted" style={{ lineHeight: 1.5 }}>Top candidates may be shortlisted for funded trading under risk limits.</p>
          </div>
        </section>

        <section style={{ ...cardStyle, marginTop: '1rem' }}>
          <h2 style={{ marginBottom: '0.85rem' }}>Selection Process</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.8rem' }}>
            <div style={cardStyle}><strong>Step 1:</strong> Register for the free crash course.</div>
            <div style={cardStyle}><strong>Step 2:</strong> Attend the 2-day live program.</div>
            <div style={cardStyle}><strong>Step 3:</strong> Complete the in-course evaluation test.</div>
            <div style={cardStyle}><strong>Step 4:</strong> Top performers get shortlisted for funded opportunities.</div>
          </div>
        </section>

        <section style={{ ...cardStyle, marginTop: '1rem', textAlign: 'center', padding: '1.8rem 1.2rem' }}>
          <h2 style={{ marginBottom: '0.55rem' }}>Limited Seats Available</h2>
          <p className="muted" style={{ marginBottom: '1rem' }}>
            Join the upcoming batch and unlock your chance to become a funded trader.
          </p>
          <a className="neo-btn-solid-green" href={REGISTER_URL}>Secure Your Seat</a>
        </section>
      </main>
    </div>
  );
};

export default FundedProgram;
