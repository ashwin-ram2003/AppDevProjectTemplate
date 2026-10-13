import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const MyLoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    // In a real app, you would validate with the Flask backend here.
    // For now, just navigate to the portal.
    navigate('/portal');
  };

  return (
    <div className="auth-container">
      <div className="card auth-card">
        <h2>Sign In to MakerHub</h2>
        <form className="auth-form" onSubmit={handleLogin}>
          <div className="form-group">
            <label className="form-label" htmlFor="username">Username (UT EID)</label>
            <input 
              type="text" 
              id="username" 
              className="form-control" 
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <input 
              type="password" 
              id="password" 
              className="form-control" 
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }}>
            Sign In
          </button>
        </form>
        <div className="auth-links">
          <Link to="/forgot-password">Forgot your password?</Link>
          <span>Don't have an account? <Link to="/register">Create an account</Link></span>
        </div>
      </div>
    </div>
  );
};

export default MyLoginPage;

