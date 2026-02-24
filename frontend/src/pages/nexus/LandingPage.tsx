import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import VanillaTilt from 'vanilla-tilt';
import '../../styles/nexus/GlassStyles.css';

interface LandingPageProps {
    toggleTheme: () => void;
    theme: string;
}

const LandingPage: React.FC<LandingPageProps> = ({ toggleTheme, theme }) => {
    const navigate = useNavigate();
    const revealRefs = useRef<HTMLDivElement[]>([]);

    useEffect(() => {
        // Vanilla Tilt
        const tiltElements = document.querySelectorAll('.card');
        tiltElements.forEach((el) => {
            VanillaTilt.init(el as HTMLElement, {
                max: 10,
                speed: 400,
                glare: true,
                'max-glare': 0.2,
            });
        });

        // Intersection Observer for scroll reveal
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                }
            });
        }, { threshold: 0.15 });

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

    return (
        <div className="nexus-glass-portal" data-theme={theme}>
            <nav>
                <div className="brand" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
                    <img src="/logo.png" alt="Trading Nexus" style={{ width: '80px', height: '80px', objectFit: 'contain' }} />
                    <span style={{ fontWeight: 800, letterSpacing: '3px', textTransform: 'uppercase', marginTop: '10px' }}>TRADING NEXUS</span>
                </div>
                <div className="theme-toggle" onClick={toggleTheme}>
                    <div className="toggle-dot"></div>
                </div>
            </nav>

            <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
                <section className="hero reveal" ref={addToRefs} style={{ padding: '100px 0', textAlign: 'center' }}>
                    <h1>The Ecosystem for Professional Traders</h1>
                    <p style={{ fontSize: '1.25rem', maxWidth: '700px', margin: '0 auto 40px' }}>From free foundational learning to institutional-grade trading accounts. We provide the infrastructure and instruments to conquer it.</p>
                    <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', flexWrap: 'wrap' }}>
                        <button onClick={() => navigate('/signup')} className="btn">Start Your Journey</button>
                        <button className="btn btn-glass">Learn More</button>
                    </div>
                </section>

                <div className="grid">
                    <div className="glass card reveal" ref={addToRefs}>
                        <div className="card-icon">📚</div>
                        <h3>Knowledge Hub</h3>
                        <p>High-tier education shouldn't be gated. Access our complete curriculum without spending a dime. Price Action mastery, Risk Management, and more.</p>
                        <button className="btn btn-glass">Explore Academy</button>
                    </div>

                    <div className="glass card reveal" ref={addToRefs}>
                        <div className="card-icon">💰</div>
                        <h3>Mentoring from Pro-Traders</h3>
                        <p>Ready to trade bigger? Nobody can earn on behalf of you, you have to learn and earn yourself</p>
                        <button className="btn btn-glass">Join hands</button>
                    </div>

                    <div className="glass card reveal" ref={addToRefs}>
                        <div className="card-icon">⚡</div>
                        <h3>Pro Infrastructure</h3>
                        <p>Optimized for professional scalpers and swing traders. Institutional leverage, low latency execution, and direct API access.</p>
                        <button className="btn btn-glass">Open Account</button>
                    </div>
                </div>

                <section className="join-now reveal" id="join" ref={addToRefs} style={{ padding: '100px 0', textAlign: 'center' }}>
                    <div className="glass join-box" style={{ padding: '80px 40px', maxWidth: '800px', margin: '0 auto' }}>
                        <h2>Ready to Join the Elite?</h2>
                        <p className="join-desc" style={{ marginBottom: '40px' }}>Become part of a global ecosystem of professional traders. Secure your spot today.</p>

                        <button className="uiverse-button" onClick={() => navigate('/signup')}>
                            <div className="bg"></div>
                            <div className="wrap">
                                <div className="btn-outline"></div>
                                <div className="btn-content">
                                    <span className="char state-1">
                                        <span style={{ '--i': 1 } as React.CSSProperties} data-label="S">S</span>
                                        <span style={{ '--i': 2 } as React.CSSProperties} data-label="i">i</span>
                                        <span style={{ '--i': 3 } as React.CSSProperties} data-label="g">g</span>
                                        <span style={{ '--i': 4 } as React.CSSProperties} data-label="n">n</span>
                                        <span style={{ '--i': 5 } as React.CSSProperties} data-label="U">U</span>
                                        <span style={{ '--i': 6 } as React.CSSProperties} data-label="p">p</span>
                                    </span>
                                    <div className="btn-icon"><div></div></div>
                                </div>
                            </div>
                        </button>
                    </div>
                </section>
            </main>

            <footer style={{ padding: '40px', textAlign: 'center', borderTop: '1px solid var(--glass-border)', color: 'var(--text-dim)' }}>
                <p>&copy; 2026 Institutional Trading Hub. All rights reserved.</p>
                <p style={{ marginTop: '10px', opacity: 0.6, fontSize: '0.9rem' }}>Trading involves risk. Education is key to success.</p>
            </footer>
        </div>
    );
};

export default LandingPage;
