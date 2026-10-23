import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { addUser } from '../api/users';

const DEV_USER = { username: 'Dev', userId: 'dev', password: 'dev' };

// Development shortcut: signs in as a "dev" user without typing credentials.
// It still goes through the real login, creating the account first if it doesn't
// exist (e.g. after the mock database restarts), so the userId is real.
// Renders nothing outside `npm start`; NODE_ENV is inlined at build time, so
// production builds drop this button entirely.
export default function DevLogin() {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  if (process.env.NODE_ENV !== 'development') return null;

  async function handleClick() {
    setBusy(true);
    setError(null);
    try {
      try {
        await signIn(DEV_USER.userId, DEV_USER.password);
      } catch {
        await addUser(DEV_USER.username, DEV_USER.userId, DEV_USER.password);
        await signIn(DEV_USER.userId, DEV_USER.password);
      }
      navigate('/projects');
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card">
      <button type="button" onClick={handleClick} disabled={busy}>
        {busy ? 'Signing in...' : 'Dev login (skip sign-in)'}
      </button>
      <p className="muted">Development only. Signs in as userId "dev".</p>
      {error && <p className="msg err">{error}</p>}
    </div>
  );
}
