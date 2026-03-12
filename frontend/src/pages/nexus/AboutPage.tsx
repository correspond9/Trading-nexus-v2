import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../../styles/nexus/GlassStyles.css';

const AboutPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="nexus-glass-portal" style={{ minHeight: '100vh' }}>
      <main style={{ maxWidth: '1000px', margin: '0 auto', padding: '2rem 1rem 4rem' }}>
        <section className="glass" style={{ padding: '2rem', borderRadius: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
            <div>
              <h1 style={{ marginBottom: '0.75rem' }}>About TradingNexus Learn</h1>
              <p style={{ maxWidth: '720px' }}>
                We help new and intermediate traders build practical skills with structured education, disciplined risk
                thinking, and a clear path toward higher-capital opportunities.
              </p>
            </div>
            <button className="btn btn-glass" onClick={() => navigate('/')}>
              Back Home
            </button>
          </div>
        </section>

        <section className="glass" style={{ marginTop: '1.5rem', padding: '2rem', borderRadius: '20px' }}>
          <h2 style={{ marginBottom: '0.75rem' }}>What We Focus On</h2>
          <p>1. Market structure and derivatives basics.</p>
          <p>2. Risk-first execution and position sizing discipline.</p>
          <p>3. Consistent process over emotional decision making.</p>
          <p>4. Transparent progression from learning to evaluation.</p>
        </section>

        <section className="glass" style={{ marginTop: '1.5rem', padding: '2rem', borderRadius: '20px' }}>
          <h2 style={{ marginBottom: '0.75rem' }}>Next Step</h2>
          <p style={{ marginBottom: '1.25rem' }}>
            Start with the free crash course, then register for upcoming batches.
          </p>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <button className="btn" onClick={() => navigate('/course')}>Explore Course</button>
            <button className="btn btn-glass" onClick={() => navigate('/register')}>Register</button>
          </div>
        </section>
      </main>
    </div>
  );
};

export default AboutPage;
