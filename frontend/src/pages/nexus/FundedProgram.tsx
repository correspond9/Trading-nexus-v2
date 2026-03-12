import React from 'react';
import '../../styles/nexus/NeoTheme.css';

const REGISTER_URL = '/register';

const FundedProgram: React.FC = () => {
  return (
    <div className="funded-page">
      <div className="funded-container">
        <nav className="funded-nav">
          <div className="funded-logo-wrap">
            <img src="/logo.png" alt="TradingNexus" className="funded-logo-img" />
            <div className="funded-logo">TradingNexus</div>
          </div>
          <a href={REGISTER_URL}>Sign Up</a>
        </nav>

        <section className="funded-hero">
          <h1>
            Become a <span className="funded-gradient">Funded Trader</span>
          </h1>

          <p>
            TradingNexus is launching a unique opportunity for derivatives traders across India.
            Participate in our <span className="funded-gradient">Free 2-Day Derivatives Crash Course</span> where your trading
            knowledge and discipline will be evaluated. Top performers may receive the opportunity
            to trade with <span className="funded-gradient">400% capital provided by TradingNexus.</span>
          </p>

          <a className="funded-cta" href={REGISTER_URL}>
            Sign Up Now
          </a>
        </section>

        <section className="funded-grid">
          <div className="funded-card">
            <div className="funded-icon">💰</div>
            <h3>80% Capital Funding</h3>
            <p>Selected traders receive access to trading capital provided by TradingNexus.</p>
          </div>

          <div className="funded-card">
            <div className="funded-icon">📊</div>
            <h3>Derivatives Crash Course</h3>
            <p>A structured 2-day program covering essential futures and options concepts.</p>
          </div>

          <div className="funded-card">
            <div className="funded-icon">🧠</div>
            <h3>Skill Evaluation</h3>
            <p>Participants will be evaluated through discussions and a short test.</p>
          </div>

          <div className="funded-card">
            <div className="funded-icon">🎓</div>
            <h3>Certification</h3>
            <p>Participants completing the test will receive TradingNexus certification.</p>
          </div>
        </section>

        <section className="funded-process">
          <h2>Selection Process</h2>
          <div className="funded-steps">
            <div className="funded-step">
              <h4>Step 1</h4>
              <p>Register for the free crash course.</p>
            </div>

            <div className="funded-step">
              <h4>Step 2</h4>
              <p>Attend the 2-day derivatives training program.</p>
            </div>

            <div className="funded-step">
              <h4>Step 3</h4>
              <p>Complete the evaluation test during the program.</p>
            </div>

            <div className="funded-step">
              <h4>Step 4</h4>
              <p>Top candidates are shortlisted for TradingNexus funding.</p>
            </div>
          </div>
        </section>

        <section className="funded-final">
          <h2 className="funded-gradient">Limited Seats Available</h2>
          <p>
            Join the upcoming batch of the Free Derivatives Crash Course and get the
            opportunity to become a funded trader.
          </p>
          <a className="funded-cta" href={REGISTER_URL}>
            Secure Your Seat
          </a>
        </section>

        <footer className="funded-footer">TradingNexus © 2026</footer>
      </div>
    </div>
  );
};

export default FundedProgram;
