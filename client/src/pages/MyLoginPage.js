import { useState } from 'react';
import { signIn } from '../api/auth.js';

/**
 * US-02 -- Sign in. Collects username/userId/password, authenticates via
 * POST /login (server/app.py -> usersDatabase.login, which verifies
 * against the stored bcrypt hash -- SR3), and hands the authenticated
 * identity back to the caller on success.
 *
 * Data source: mutates via client/src/api/auth.js
 * No hard-coded fallback: this component renders nothing it was not given or told.
 *
 * @component
 * @param {Object} props
 * @param {Function} props.onSignedIn - Called with { username, userId }
 *   after a successful sign-in.
 * @param {Function} props.onSwitchToSignUp - Called when the user picks
 *   "Need an account? Sign up" instead.
 */
export default function MyLoginPage({ onSignedIn, onSwitchToSignUp }) {
  const [username, setUsername] = useState('');
  const [userId, setUserId] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const account = await signIn({ username, userId, password });
      await onSignedIn(account);
    } catch (signInError) {
      setError(describeSignInError(signInError));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <h2>Sign in</h2>

      <label className="auth-form__field">
        Username
        <input
          type="text"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          autoComplete="username"
          required
        />
      </label>

      <label className="auth-form__field">
        User ID
        <input
          type="text"
          value={userId}
          onChange={(event) => setUserId(event.target.value)}
          autoComplete="off"
          required
        />
      </label>

      <label className="auth-form__field">
        Password
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
          required
        />
      </label>

      <button type="submit" disabled={submitting}>
        {submitting ? 'Signing in...' : 'Sign in'}
      </button>

      {error && (
        <p role="alert" className="error-text auth-form__message">
          {error}
        </p>
      )}

      <p className="muted-text auth-form__switch">
        Need an account?{' '}
        <button type="button" className="auth-form__link" onClick={onSwitchToSignUp}>
          Sign up
        </button>
      </p>
    </form>
  );
}

// Translates /login's error shapes (see server/app.py) into copy a user
// filling out this form can act on. Deliberately does not distinguish
// "wrong password" from "no such user" -- the server already blurs that
// on purpose (see usersDatabase.login's docstring).
function describeSignInError(error) {
  if (error.message === 'invalid_credentials') {
    return 'Incorrect username, user ID, or password.';
  }
  if (error.field) {
    return `${error.field} is required.`;
  }
  return error.message;
}
