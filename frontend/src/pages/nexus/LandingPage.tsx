import React, { useEffect, useRef, useState } from 'react';
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
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    useEffect(() => {
        // Disable Vanilla Tilt on mobile devices for performance
        const isMobile = window.innerWidth < 768;
        
        if (!isMobile) {
            const tiltElements = document.querySelectorAll('.card');
            tiltElements.forEach((el) => {
                VanillaTilt.init(el as HTMLElement, {
                    max: 10,
                    speed: 400,
                    glare: true,
                    'max-glare': 0.2,
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
            <nav style={{ padding: '1rem 2rem' }}>
                <div className="brand" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} style={{ cursor: 'pointer' }}>
                    <img src="/logo.png" alt="Trading Nexus" style={{ width: '60px', height: '60px', objectFit: 'contain' }} />
                    <span style={{ fontWeight: 800, letterSpacing: '2px', textTransform: 'uppercase', fontSize: 'clamp(0.9rem, 2.5vw, 1.1rem)' }}>TRADING NEXUS</span>
                </div>
                <div className="theme-toggle" onClick={toggleTheme} style={{ cursor: 'pointer' }}>
                    <div className="toggle-dot"></div>
                </div>
            </nav>

            <main style={{ maxWidth: '1200px', margin: '0 auto', padding: 'clamp(1rem, 3vw, 2rem)' }}>
                <section className="hero reveal" ref={addToRefs} style={{ padding: 'clamp(3rem, 10vw, 6rem) 0', textAlign: 'center' }}>
                    <h1 style={{ fontSize: 'clamp(2rem, 6vw, 3.5rem)', marginBottom: '1.5rem' }}>The Ecosystem for Professional Traders</h1>
                    <p style={{ fontSize: 'clamp(1rem, 3vw, 1.25rem)', maxWidth: '700px', margin: '0 auto 2.5rem', padding: '0 1rem' }}>From free foundational learning to institutional-grade trading accounts. We provide the infrastructure and instruments to conquer it.</p>
                    <div style={{ display: 'flex', gap: 'clamp(0.75rem, 2vw, 1.25rem)', justifyContent: 'center', flexWrap: 'wrap', padding: '0 1rem' }}>
                        <button onClick={() => navigate('/signup')} className="btn" style={{ padding: 'clamp(0.75rem, 2vw, 1rem) clamp(1.5rem, 4vw, 2.5rem)' }}>Start Your Journey</button>
                        <button className="btn btn-glass" style={{ padding: 'clamp(0.75rem, 2vw, 1rem) clamp(1.5rem, 4vw, 2.5rem)' }}>Learn More</button>
                    </div>
                </section>

                <div className="grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(300px, 100%), 1fr))', gap: 'clamp(1rem, 3vw, 2rem)', padding: '0 1rem' }}>
                    <div className="glass card reveal tilt-card" ref={addToRefs}>
                        <div className="card-icon" style={{ fontSize: 'clamp(2rem, 5vw, 3rem)' }}>📚</div>
                        <h3 style={{ fontSize: 'clamp(1.25rem, 4vw, 1.5rem)' }}>Knowledge Hub</h3>
                        <p style={{ fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>High-tier education shouldn't be gated. Access our complete curriculum without spending a dime. Price Action mastery, Risk Management, and more.</p>
                        <button className="btn btn-glass" style={{ marginTop: '1rem', width: '100%' }}>Explore Academy</button>
                    </div>

                    <div className="glass card reveal tilt-card" ref={addToRefs}>
                        <div className="card-icon" style={{ fontSize: 'clamp(2rem, 5vw, 3rem)' }}>💰</div>
                        <h3 style={{ fontSize: 'clamp(1.25rem, 4vw, 1.5rem)' }}>Mentoring from Pro-Traders</h3>
                        <p style={{ fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>Ready to trade bigger? Nobody can earn on behalf of you, you have to learn and earn yourself</p>
                        <button className="btn btn-glass" style={{ marginTop: '1rem', width: '100%' }}>Join hands</button>
                    </div>

                    <div className="glass card reveal tilt-card" ref={addToRefs}>
                        <div className="card-icon" style={{ fontSize: 'clamp(2rem, 5vw, 3rem)' }}>⚡</div>
                        <h3 style={{ fontSize: 'clamp(1.25rem, 4vw, 1.5rem)' }}>Pro Infrastructure</h3>
                        <p style={{ fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>Optimized for professional scalpers and swing traders. Institutional leverage, low latency execution, and direct API access.</p>
                        <button className="btn btn-glass" style={{ marginTop: '1rem', width: '100%' }}>Open Account</button>
                    </div>
                </div>

                <section className="join-now reveal" id="join" ref={addToRefs} style={{ padding: 'clamp(3rem, 10vw, 6rem) 0', textAlign: 'center' }}>
                    <div className="glass join-box" style={{ padding: 'clamp(2rem, 8vw, 5rem) clamp(1.5rem, 5vw, 2.5rem)', maxWidth: '800px', margin: '0 auto' }}>
                        <h2 style={{ fontSize: 'clamp(1.75rem, 5vw, 2.5rem)', marginBottom: '1rem' }}>Ready to Join the Elite?</h2>
                        <p className="join-desc" style={{ marginBottom: '2.5rem', fontSize: 'clamp(1rem, 3vw, 1.1rem)' }}>Become part of a global ecosystem of professional traders. Secure your spot today.</p>

                        <button className="uiverse-button" onClick={() => navigate('/signup')} style={{ margin: '0 auto' }}>
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

            <footer className="footer" style={{ padding: 'clamp(2rem, 5vw, 2.5rem)', textAlign: 'center', borderTop: '1px solid var(--glass-border)', color: 'var(--text-dim)' }}>
                <p style={{ fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>&copy; 2026 Institutional Trading Hub. All rights reserved.</p>
                <p style={{ marginTop: '10px', opacity: 0.6, fontSize: 'clamp(0.8rem, 2vw, 0.9rem)' }}>Trading involves risk. Education is key to success.</p>
            </footer>
        </div>
    );
};

export default LandingPage;
