import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../styles/nexus/GlassStyles.css';

const SignupPage: React.FC = () => {
    const navigate = useNavigate();
    const [isSuccess, setIsSuccess] = useState(false);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setIsSuccess(true);
        setTimeout(() => {
            navigate('/');
        }, 3000);
    };

    return (
        <div className="nexus-glass-portal">
            <div style={{ 
                minHeight: '100vh', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                padding: 'clamp(1rem, 3vw, 2rem)' 
            }}>
                <div className="glass" style={{ 
                    width: '100%', 
                    maxWidth: 'min(500px, 100%)', 
                    padding: 'clamp(1.5rem, 5vw, 2.5rem)', 
                    borderRadius: 'clamp(20px, 5vw, 30px)', 
                    textAlign: 'center' 
                }}>
                    <img 
                        src="/logo.png" 
                        alt="TN" 
                        style={{ 
                            width: 'clamp(50px, 10vw, 60px)', 
                            height: 'clamp(50px, 10vw, 60px)', 
                            marginBottom: '15px' 
                        }} 
                    />
                    <h2 style={{ fontSize: 'clamp(1.5rem, 5vw, 2rem)', marginBottom: '0.5rem' }}>Join the Nexus</h2>
                    <p style={{ 
                        marginBottom: 'clamp(1.5rem, 4vw, 2rem)', 
                        fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' 
                    }}>Start your journey to institutional mastery</p>

                    <form onSubmit={handleSubmit} style={{ textAlign: 'left' }}>
                        <div className="form-group" style={{ marginBottom: 'clamp(1rem, 3vw, 1.5rem)' }}>
                            <input 
                                type="text" 
                                className="search-input" 
                                placeholder=" " 
                                required 
                                style={{ 
                                    width: '100%', 
                                    fontSize: 'clamp(14px, 3vw, 16px)',
                                    padding: 'clamp(0.75rem, 2vw, 1rem)',
                                    minHeight: '48px' 
                                }} 
                            />
                            <label className="input-label" style={{ fontSize: 'clamp(0.8rem, 2vw, 0.9rem)' }}>Full Name</label>
                        </div>
                        <div className="form-group" style={{ marginBottom: 'clamp(1rem, 3vw, 1.5rem)' }}>
                            <input 
                                type="email" 
                                className="search-input" 
                                placeholder=" " 
                                required 
                                style={{ 
                                    width: '100%', 
                                    fontSize: 'clamp(14px, 3vw, 16px)',
                                    padding: 'clamp(0.75rem, 2vw, 1rem)',
                                    minHeight: '48px' 
                                }} 
                            />
                            <label className="input-label" style={{ fontSize: 'clamp(0.8rem, 2vw, 0.9rem)' }}>Email Address</label>
                        </div>
                        <div className="form-group" style={{ marginBottom: 'clamp(1.5rem, 4vw, 2rem)' }}>
                            <input 
                                type="text" 
                                className="search-input" 
                                placeholder=" " 
                                required 
                                style={{ 
                                    width: '100%', 
                                    fontSize: 'clamp(14px, 3vw, 16px)',
                                    padding: 'clamp(0.75rem, 2vw, 1rem)',
                                    minHeight: '48px' 
                                }} 
                            />
                            <label className="input-label" style={{ fontSize: 'clamp(0.8rem, 2vw, 0.9rem)' }}>Trading Experience</label>
                        </div>

                        <button 
                            type="submit" 
                            className="submit-btn btn" 
                            style={{ 
                                width: '100%', 
                                minHeight: '48px',
                                fontSize: 'clamp(14px, 3vw, 16px)',
                                padding: 'clamp(0.75rem, 2vw, 1rem) clamp(1.5rem, 4vw, 2rem)'
                            }}
                        >Create Account</button>
                    </form>

                    <button 
                        onClick={() => navigate('/')} 
                        className="back-link" 
                        style={{ 
                            background: 'none', 
                            border: 'none', 
                            color: 'var(--text-dim)', 
                            marginTop: 'clamp(1rem, 3vw, 1.5rem)', 
                            width: '100%', 
                            cursor: 'pointer',
                            fontSize: 'clamp(0.9rem, 2.5vw, 1rem)',
                            minHeight: '44px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}
                    >← Back to Nexus</button>
                </div>
            </div>

            <div className={`modal-overlay ${isSuccess ? 'active' : ''}`}>
                <div className="success-modal" style={{ 
                    padding: 'clamp(2rem, 5vw, 3rem)',
                    width: '90%',
                    maxWidth: 'min(400px, 100%)'
                }}>
                    <span style={{ 
                        fontSize: 'clamp(3rem, 10vw, 4rem)', 
                        display: 'block', 
                        marginBottom: 'clamp(1rem, 3vw, 1.5rem)' 
                    }}>✅</span>
                    <h3 style={{ fontSize: 'clamp(1.5rem, 5vw, 2rem)' }}>Thank You!</h3>
                    <p style={{ fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>Our institutional desk will contact you soon.</p>
                    <div className={`timer-bar ${isSuccess ? 'start' : ''}`}></div>
                </div>
            </div>
        </div>
    );
};

export default SignupPage;
