// Top bar shown on logged-in pages.
// Shows the app title, the signed-in userId, a link to /projects and a Logout button
// (calls signOut, then navigates to /login).
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// Inline styles
const barStyle = {
  display: 'flex',
  alignItems: 'center',
  flexWrap: 'wrap',
  gap: 16,
  padding: '12px 16px',
  background: '#fff',
  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.12)',
};

const titleStyle = {
  fontWeight: 700,
  fontSize: 20,
  color: '#bf5700',
  textDecoration: 'none',
};

const userAreaStyle = {
  marginLeft: 'auto',
  display: 'flex',
  alignItems: 'center',
  gap: 12,
};

export default function Navbar() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    signOut();
    navigate('/login', { replace: true });
  }

  return (
    <header style={barStyle}>
      <Link to="/projects" style={titleStyle}>HaaS</Link>
      <nav>
        <Link to="/projects">My projects</Link>
      </nav>
      <div style={userAreaStyle}>
        {user && (
          <span className="muted">
            Signed in as <strong>{user.userId}</strong>
          </span>
        )}
        <button type="button" onClick={handleLogout}>Log out</button>
      </div>
    </header>
  );
}