import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../styles/nexus/GlassStyles.css';

interface SignupPageProps {
    theme: string;
}

const SignupPage: React.FC<SignupPageProps> = ({ theme }) => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        experience_level: '',
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [isSuccess, setIsSuccess] = useState(false);
    const [successMessage, setSuccessMessage] = useState('');
    const [successDetails, setSuccessDetails] = useState('');

    // Email validation regex
    const isValidEmail = (email: string): boolean => {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return emailRegex.test(email);
    };

    // Form validation
    const validateForm = (): string | null => {
        if (!formData.name.trim()) {
            return 'Full name is required';
        }
        if (!formData.email.trim()) {
            return 'Email address is required';
        }
        if (!isValidEmail(formData.email)) {
            return 'Please enter a valid email address';
        }
        if (!formData.experience_level.trim()) {
            return 'Trading experience is required';
        }
        return null;
    };

    const handleInputChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
    ) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        if (error) setError(''); // Clear error when user starts typing
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            // Validate form first
            const validationError = validateForm();
            if (validationError) {
                setError(validationError);
                setLoading(false);
                return;
            }

            // Call backend API
            const response = await fetch('/api/v2/auth/portal/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            const data = await response.json();

            if (response.ok) {
                // Success
                setSuccessMessage('Welcome to Trading Nexus!');
                setSuccessDetails(data.message || `Account created successfully for ${formData.email}`);
                setIsSuccess(true);
                setFormData({ name: '', email: '', experience_level: '' });
                
                // Redirect after 3 seconds
                setTimeout(() => {
                    navigate('/');
                }, 3000);
            } else {
                // Error from backend
                setError(data.detail || 'Failed to create account. Please try again.');
            }
        } catch (err) {
            console.error('Signup error:', err);
            setError('Network error. Please check your connection and try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="nexus-glass-portal" data-theme={theme}>
            {/* Success Modal */}
            {isSuccess && (
                <div className="modal-overlay active">
                    <div className="modal-content glass">
                        <div className="success-icon">✓</div>
                        <h2>{successMessage}</h2>
                        <p>{successDetails}</p>
                        <p style={{ fontSize: '0.9rem', opacity: 0.7, marginTop: '20px' }}>
                            Redirecting to home page in 3 seconds...
                        </p>
                    </div>
                </div>
            )}

            <div style={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '20px',
                background: 'var(--bg-base)',
            }}>
                <form
                    onSubmit={handleSubmit}
                    style={{
                        width: '100%',
                        maxWidth: '450px',
                        padding: '60px 40px',
                        position: 'relative',
                        zIndex: 10,
                    }}
                    className="glass"
                >
                    <h2 style={{
                        textAlign: 'center',
                        marginBottom: '10px',
                        color: 'var(--text-main)',
                        fontSize: '28px',
                        fontWeight: 700,
                        letterSpacing: '1px',
                    }}>
                        Join the Elite
                    </h2>
                    
                    <p style={{
                        textAlign: 'center',
                        marginBottom: '40px',
                        color: 'var(--text-dim)',
                        fontSize: '14px',
                    }}>
                        Start your trading education journey today
                    </p>

                    {/* Error Message */}
                    {error && (
                        <div style={{
                            padding: '12px 16px',
                            marginBottom: '20px',
                            borderRadius: '8px',
                            background: 'rgba(255, 59, 48, 0.15)',
                            border: '1px solid rgba(255, 59, 48, 0.5)',
                            color: '#ff3b30',
                            fontSize: '14px',
                            animation: 'slideDown 0.3s ease-out',
                        }}>
                            {error}
                        </div>
                    )}

                    {/* Full Name Field */}
                    <div className="form-group">
                        <input
                            type="text"
                            name="name"
                            className="search-input"
                            placeholder=" "
                            value={formData.name}
                            onChange={handleInputChange}
                            disabled={loading}
                            required
                            style={{ opacity: loading ? 0.6 : 1 }}
                        />
                        <label className="input-label">Full Name</label>
                    </div>

                    {/* Email Field */}
                    <div className="form-group">
                        <input
                            type="email"
                            name="email"
                            className="search-input"
                            placeholder=" "
                            value={formData.email}
                            onChange={handleInputChange}
                            disabled={loading}
                            required
                            style={{ opacity: loading ? 0.6 : 1 }}
                        />
                        <label className="input-label">Email Address</label>
                    </div>

                    {/* Experience Level Field */}
                    <div className="form-group">
                        <select
                            name="experience_level"
                            className="search-input"
                            value={formData.experience_level}
                            onChange={handleInputChange}
                            disabled={loading}
                            required
                            style={{
                                opacity: loading ? 0.6 : 1,
                                color: formData.experience_level ? 'var(--text-main)' : 'var(--text-dim)',
                            }}
                        >
                            <option value="">Select Experience Level</option>
                            <option value="Beginner">Beginner - Just Starting Out</option>
                            <option value="Intermediate">Intermediate - Some Experience</option>
                            <option value="Advanced">Advanced - Experienced Trader</option>
                            <option value="Professional">Professional - Managing Capital</option>
                        </select>
                        <label className="input-label">Trading Experience</label>
                    </div>

                    {/* Submit Button */}
                    <button
                        type="submit"
                        className="submit-btn btn"
                        disabled={loading}
                        style={{
                            opacity: loading ? 0.6 : 1,
                            cursor: loading ? 'not-allowed' : 'pointer',
                            width: '100%',
                            marginTop: '20px',
                            transition: 'all 0.3s ease',
                        }}
                    >
                        {loading ? 'Creating Account...' : 'Create Account'}
                    </button>

                    {/* Terms Text */}
                    <p style={{
                        textAlign: 'center',
                        marginTop: '20px',
                        fontSize: '12px',
                        color: 'var(--text-dim)',
                        lineHeight: '1.6',
                    }}>
                        By signing up, you agree to our Terms of Service and Privacy Policy.<br/>
                        We'll send confirmation details to your email.
                    </p>
                </form>
            </div>

            {/* Add animation for error slide */}
            <style>{`
                @keyframes slideDown {
                    from {
                        opacity: 0;
                        transform: translateY(-10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            `}</style>
        </div>
    );
};

export default SignupPage;
