import React from 'react';
import { Link } from 'react-router-dom';

const ForgotMyPassword = () => {
  const handleReset = (e) => {
    e.preventDefault();
    alert("Password reset instructions have been sent to your email.");
  };

  return (
    <div className="auth-container">
      <div className="card auth-card">
        <h2>Reset Password</h2>
        <p style={{ marginBottom: '1.5rem', fontSize: '0.9rem', color: 'var(--ut-charcoal)' }}>
          Enter your UT EID or email address and we'll send you a link to reset your password.
        </p>
        <form className="auth-form" onSubmit={handleReset}>
          <div className="form-group">
            <label className="form-label" htmlFor="username">Username / Email</label>
            <input type="text" id="username" className="form-control" required />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '0.5rem' }}>
            Send Reset Link
          </button>
        </form>
        <div className="auth-links">
          <span>Remembered your password? <Link to="/login">Sign in here</Link></span>
        </div>
      </div>
    </div>
  );
};

export default ForgotMyPassword;

