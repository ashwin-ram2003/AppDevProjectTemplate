// Route /login. Sign-in area from Figure 2.
// Fields: userId, password. Submit calls useAuth().signIn, then navigates to /projects
// (or the page RequireAuth sent the user here from). Shows the server error inline
// (e.g. "Invalid credentials"). A "New User" button opens <MyRegistrationPage/> in a <Modal>.
// If already signed in, redirects to /projects.
import React, { useCallback, useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import DevLogin from '../components/DevLogin';
import FormField from '../components/FormField';
import Modal from '../components/Modal';
import MyRegistrationPage from './MyRegistrationPage';
import { useAuth } from '../context/AuthContext';

export default function MyLoginPage() {
  const { user, signIn } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [userId, setUserId] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState(null); // { ok: boolean, text: string }
  const [showRegister, setShowRegister] = useState(false);

  // Stable function so the Modal doesn't re-run its effects on every render
  const closeRegister = useCallback(() => setShowRegister(false), []);

  // After signing in, go back to the page RequireAuth bounced us from, else /projects
  const destination = location.state?.from?.pathname || '/projects';

  if (user) return <Navigate to={destination} replace />;

  async function handleSubmit(e) {
    e.preventDefault();
    const id = userId.trim();
    if (!id || !password) {
      setStatus({ ok: false, text: 'Enter your user ID and password.' });
      return;
    }
    setBusy(true);
    setStatus(null);
    try {
      await signIn(id, password);
      navigate(destination, { replace: true });
    } catch (err) {
      setStatus({ ok: false, text: err.message });
      setBusy(false);
    }
  }

  // Called by MyRegistrationPage after a successful sign-up
  function handleRegistered(newUserId) {
    setShowRegister(false);
    setUserId(newUserId);
    setPassword('');
    setStatus({ ok: true, text: 'Account created. Sign in with your new password.' });
  }

  return (
    <main>
      <h1>HaaS</h1>
      <p className="muted">Hardware as a Service: check hardware in and out for your projects.</p>

      <form className="card" onSubmit={handleSubmit}>
        <h2>Sign in</h2>
        <FormField
          id="login-userid"
          label="User ID"
          value={userId}
          onChange={setUserId}
          autoComplete="username"
        />
        <FormField
          id="login-password"
          label="Password"
          type="password"
          value={password}
          onChange={setPassword}
          autoComplete="current-password"
        />
        <button type="submit" disabled={busy}>{busy ? 'Signing in...' : 'Sign in'}</button>{' '}
        <button type="button" onClick={() => setShowRegister(true)} disabled={busy}>
          New User
        </button>
        {status && <p className={status.ok ? 'msg ok' : 'msg err'} role="status">{status.text}</p>}
      </form>

      <Modal open={showRegister} title="Create an account" onClose={closeRegister}>
        <MyRegistrationPage onDone={handleRegistered} />
      </Modal>

      <DevLogin />
    </main>
  );
}
