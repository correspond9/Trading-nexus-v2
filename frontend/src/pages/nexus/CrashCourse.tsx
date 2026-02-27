import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import VanillaTilt from 'vanilla-tilt';
import { ArrowLeft } from 'lucide-react';
import '../../styles/nexus/GlassStyles.css';

const CrashCourse: React.FC = () => {
  const navigate = useNavigate();
  const revealRefs = useRef<HTMLDivElement[]>([]);

  useEffect(() => {
    // Disable Vanilla Tilt on mobile devices for performance
    const isMobile = window.innerWidth < 768;

    if (!isMobile) {
      const tiltElements = document.querySelectorAll('.tilt-card');
      tiltElements.forEach((el) => {
        VanillaTilt.init(el as HTMLElement, {
          max: 3,
          speed: 400,
          glare: true,
          'max-glare': 0.1,
        });
      });
    }

    // Intersection Observer for scroll reveal
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('active');
        }
      });
    }, { threshold: 0.1 });

    revealRefs.current.forEach(ref => {
      if (ref) observer.observe(ref);
    });

    return () => observer.disconnect();
  }, []);

  const addToRefs = (el: HTMLDivElement | null) => {
    if (el && !revealRefs.current.includes(el)) {
      revealRefs.current.push(el);
    }
  };

  const modules = [
    {
      id: 1,
      title: "Introduction to Trading (The Foundation)",
      icon: "💡",
      topics: [
        { name: "1. Basics of Trading", desc: "Distinguishing trading (short-term) from investing (long-term). Understanding the goal: profit from price movements." },
        { name: "2. Types of Trading", desc: "Defining Scalping (seconds/minutes), Day Trading (intraday), Swing Trading (days/weeks), and Position Trading (weeks/years)." },
        { name: "3. Trading Instruments", desc: "Overview of Stocks (equity), Forex (currency pairs), Options (derivative right, not obligation), and Futures (derivative obligation)." }
      ]
    },
    {
      id: 2,
      title: "Technical Analysis and Charting (The Language of the Market)",
      icon: "📈",
      topics: [
        { name: "1. Introduction to TA", desc: "The three pillars: Price discounts everything, price moves in trends, history repeats. Focus on price action over fundamentals." },
        { name: "2. Understanding Charts", desc: "Focus on Candlestick Charts (OHLC data). The difference between Bullish (Green) and Bearish (Red) candles." },
        { name: "3. Key Concepts of TA", desc: "Identifying Support (floor) and Resistance (ceiling). Drawing Trend Lines and interpreting Volume as a confirmation tool." }
      ]
    },
    {
      id: 3,
      title: "Risk Management and Position Sizing (The Core of Survival)",
      icon: "🛡️",
      topics: [
        { name: "1. Risk Philosophy", desc: "The golden rule: Preserve capital first. Never risk more than a small, fixed percentage of the account on any single trade (e.g., 1% to 2%)." },
        { name: "2. Defining Risk", desc: "Calculating the Maximum Dollar Risk per trade (Account Size × Risk Percentage)." },
        { name: "3. Implementing the Stop-Loss", desc: "Using the Stop-Loss (S/L) order to enforce the maximum loss limit, based on technical chart points." },
        { name: "4. Position Sizing", desc: "The critical formula to determine how many shares/contracts to buy: (Maximum Dollar Risk / Risk Per Share)." }
      ]
    },
    {
      id: 4,
      title: "Strategy Development and Psychology (Discipline and Edge)",
      icon: "🧠",
      topics: [
        { name: "1. Developing a Strategy", desc: "Creating an objective Checklist of entry, exit, and management rules. Understanding the concept of a statistical \"Edge.\"" },
        { name: "2. Risk-to-Reward Ratio", desc: "Defining the R:R (Reward ÷ Risk). Understanding why aiming for 1 : 1.5 or 1 : 2 is necessary for long-term profitability, even with losses." },
        { name: "3. Trading Psychology", desc: "Identifying and combating common traps like FOMO, Revenge Trading, and moving the Stop-Loss." },
        { name: "4. Trading Journal", desc: "The importance of documenting every trade and the associated emotions for performance review and rule reinforcement." }
      ]
    },
    {
      id: 5,
      title: "Practical Implementation and Tools (Execution)",
      icon: "🛠️",
      topics: [
        { name: "1. Choosing a Broker", desc: "Criteria for selection: Regulation, low commissions/spreads, and a reliable Trading Platform." },
        { name: "2. Order Execution", desc: "Differentiating between Market Orders (immediate execution) and Limit Orders (execution only at a desired price)." },
        { name: "3. The Trading Workflow", desc: "Step-by-step process: Preparation → Analysis → Position Sizing → Order Placement (with S/L & T/P) → Review." }
      ]
    }
  ];

  return (
    <div className="nexus-glass-portal" style={{ minHeight: '100vh', padding: '2rem 1rem', display: 'flex', flexDirection: 'column' }}>
      <nav style={{ padding: '0 1rem', maxWidth: '1200px', margin: '0 auto', width: '100%', display: 'flex' }}>
        <button
          className="btn btn-glass"
          onClick={() => navigate('/')}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1.5rem' }}
        >
          <ArrowLeft size={20} /> Back to Home
        </button>
      </nav>

      <main style={{ maxWidth: '1000px', margin: '3rem auto 0', width: '100%' }}>
        <section className="reveal" ref={addToRefs} style={{ textAlign: 'center', marginBottom: '4rem', padding: '0 1rem' }}>
          <h1 style={{ fontSize: 'clamp(2rem, 5vw, 3.5rem)', marginBottom: '1.5rem', fontWeight: '800', background: 'linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Trading Crash Course
          </h1>
          <p style={{ fontSize: 'clamp(1rem, 2vw, 1.25rem)', color: 'var(--text-dim, #a0a0a0)', maxWidth: '700px', margin: '0 auto', lineHeight: '1.6' }}>
            Master the fundamentals of trading with this comprehensive crash course. We cover the core concepts from introductory market mechanics to practical execution strategies.
          </p>
        </section>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem', padding: '0 1rem' }}>
          {modules.map((module) => (
            <div
              key={module.id}
              className="glass reveal tilt-card"
              ref={addToRefs}
              style={{
                padding: 'clamp(1.5rem, 4vw, 3rem)',
                borderRadius: '16px',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                background: 'linear-gradient(145deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%)',
                boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.2)'
              }}
            >
              <h2 style={{ fontSize: 'clamp(1.2rem, 3vw, 1.6rem)', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '1rem', borderBottom: '1px solid rgba(255, 255, 255, 0.1)', paddingBottom: '1.5rem' }}>
                <span style={{ fontSize: '1.5em', textShadow: '0 0 20px rgba(255,255,255,0.3)' }}>{module.icon}</span>
                <span>Module {module.id}: <span style={{ fontWeight: '400', opacity: 0.9 }}>{module.title}</span></span>
              </h2>

              {/* Table Header (Desktop only visually, flex behavior changes on mobile) */}
              <div className="module-header" style={{ display: 'grid', gridTemplateColumns: '1fr 2.5fr', gap: '1.5rem', marginBottom: '1rem', color: 'var(--text-dim, #a0a0a0)', fontWeight: 600, fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '1px', padding: '0 1rem' }}>
                <div className="hidden-mobile">Topic</div>
                <div className="hidden-mobile">Key Concepts for Students</div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {module.topics.map((topic) => (
                  <div
                    key={topic.name}
                    className="topic-row"
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                      gap: '1.5rem',
                      padding: '1.25rem',
                      background: 'rgba(255, 255, 255, 0.02)',
                      borderRadius: '8px',
                      borderLeft: '3px solid rgba(255, 255, 255, 0.1)',
                      transition: 'all 0.3s ease',
                      cursor: 'default'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                      e.currentTarget.style.borderLeftColor = 'rgba(255, 255, 255, 0.6)';
                      e.currentTarget.style.transform = 'translateX(5px)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'rgba(255, 255, 255, 0.02)';
                      e.currentTarget.style.borderLeftColor = 'rgba(255, 255, 255, 0.1)';
                      e.currentTarget.style.transform = 'translateX(0)';
                    }}
                  >
                    <div style={{ fontWeight: 600, color: 'var(--text, #fff)', fontSize: '1.05rem' }}>
                      {topic.name}
                    </div>
                    <div style={{ color: 'var(--text-dim, #a0a0a0)', lineHeight: '1.6', fontSize: '1rem' }} dangerouslySetInnerHTML={{ __html: topic.desc.replace(/Maximum Dollar Risk/, '<b>Maximum Dollar Risk</b>').replace(/Risk Per Share/, '<b>Risk Per Share</b>').replace(/Price discounts everything, price moves in trends, history repeats/, '<i>Price discounts everything, price moves in trends, history repeats</i>') }}>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <footer style={{ padding: '4rem 1rem 2rem', textAlign: 'center', color: 'var(--text-dim, #a0a0a0)', fontSize: '0.9rem' }}>
          <p>Trading involves significant risk. This content is for educational purposes only.</p>
        </footer>
      </main>

      {/* CSS for mobile fallbacks */}
      <style dangerouslySetInnerHTML={{
        __html: `
                @media (min-width: 768px) {
                    .topic-row {
                        grid-template-columns: 1fr 2.5fr !important;
                    }
                }
                @media (max-width: 767px) {
                    .hidden-mobile {
                        display: none;
                    }
                    .module-header {
                        display: none !important;
                    }
                }
            `}} />
    </div>
  );
};

export default CrashCourse;
