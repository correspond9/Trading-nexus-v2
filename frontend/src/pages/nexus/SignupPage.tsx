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
            <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
                <div className="glass" style={{ width: '100%', maxWidth: '500px', padding: '40px', borderRadius: '30px', textAlign: 'center' }}>
                    <img src="/logo.png" alt="TN" style={{ width: '60px', height: '60px', marginBottom: '15px' }} />
                    <h2>Join the Nexus</h2>
                    <p style={{ marginBottom: '30px' }}>Start your journey to institutional mastery</p>

                    <form onSubmit={handleSubmit} style={{ textAlign: 'left' }}>
                        <div className="form-group">
                            <input type="text" className="search-input" placeholder=" " required />
                            <label className="input-label">Full Name</label>
                        </div>
                        <div className="form-group">
                            <input type="email" className="search-input" placeholder=" " required />
                            <label className="input-label">Email Address</label>
                        </div>
                        <div className="form-group">
                            <input type="text" className="search-input" placeholder=" " required />
                            <label className="input-label">Trading Experience</label>
                        </div>

                        <button type="submit" className="submit-btn btn" style={{ width: '100%' }}>Create Account</button>
                    </form>

                    <button onClick={() => navigate('/')} className="back-link" style={{ background: 'none', border: 'none', color: 'var(--text-dim)', marginTop: '20px', width: '100%', cursor: 'pointer' }}>← Back to Nexus</button>
                </div>
            </div>

            <div className={`modal-overlay ${isSuccess ? 'active' : ''}`}>
                <div className="success-modal">
                    <span style={{ fontSize: '4rem', display: 'block', marginBottom: '20px' }}>✅</span>
                    <h3>Thank You!</h3>
                    <p>Our institutional desk will contact you soon.</p>
                    <div className={`timer-bar ${isSuccess ? 'start' : ''}`}></div>
                </div>
            </div>
        </div>
    );
};

export default SignupPage;
