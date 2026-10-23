// New User sign-up form, rendered inside <Modal> on the login page.
// Props: { onDone }   (called with the new userId after a successful sign-up, so the
//                      login page can close the modal and pre-fill the sign-in form)
// Fields: username, userId, password + confirm password (checked client-side).
// Submit calls api/users.addUser; shows "That userId is already taken" (409) and other errors inline.
import React, { useState } from 'react';
import FormField from '../components/FormField';
import { addUser } from '../api/users';

export default function MyRegistrationPage({ onDone }) {
  const [username, setUsername] = useState('');
  const [userId, setUserId] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    const name = username.trim();
    const id = userId.trim();

    if (!name || !id || !password) {
      setError('Name, user ID and password are all required.');
      return;
    }
    if (password !== confirm) {
      setError('The passwords do not match.');
      return;
    }

    setBusy(true);
    setError(null);
    try {
      await addUser(name, id, password);
      onDone(id);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <FormField id="reg-username" label="Name" value={username} onChange={setUsername} autoComplete="name" />
      <FormField id="reg-userid" label="User ID" value={userId} onChange={setUserId} autoComplete="username" />
      <FormField
        id="reg-password"
        label="Password"
        type="password"
        value={password}
        onChange={setPassword}
        autoComplete="new-password"
      />
      <FormField
        id="reg-confirm"
        label="Confirm password"
        type="password"
        value={confirm}
        onChange={setConfirm}
        autoComplete="new-password"
      />
      <button type="submit" disabled={busy}>{busy ? 'Creating account...' : 'Create account'}</button>
      {error && <p className="msg err" role="status">{error}</p>}
    </form>
  );
}