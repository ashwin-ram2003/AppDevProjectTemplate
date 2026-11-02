import { useState } from 'react';
import { signUp } from '../api/auth.js';

/**
 * US-01 -- Sign up. Collects a new username/userId/password, creates the
 * account via POST /add_user (server/app.py -> usersDatabase.addUser,
 * which bcrypt-hashes the password before storage -- SR3), and hands the
 * created identity back to the caller on success.
 *
 * Data source: mutates via client/src/api/auth.js
 * No hard-coded fallback: this component renders nothing it was not given or told.
 *
 * @component
 * @param {Object} props
 * @param {Function} props.onSignedUp - Called with { username, userId }
 *   after a successful sign-up. No default -- the caller decides what
 *   happens next (e.g. treat the new account as signed in).
 * @param {Function} props.onSwitchToSignIn - Called when the user picks
 *   "Already have an account? Sign in" instead.
 */
export default function MyRegistrationPage({ onSignedUp, onSwitchToSignIn }) {
  const [username, setUsername] = useState('');
  const [userId, setUserId] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setSubmitting(true);
    try {
      const account = await signUp({ username, userId, password });
      await onSignedUp(account);
    } catch (signUpError) {
      setError(describeSignUpError(signUpError));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <h2>Create an account</h2>

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
          autoComplete="new-password"
          required
        />
      </label>

      <label className="auth-form__field">
        Confirm password
        <input
          type="password"
          value={confirmPassword}
          onChange={(event) => setConfirmPassword(event.target.value)}
          autoComplete="new-password"
          required
        />
      </label>

      <button type="submit" disabled={submitting}>
        {submitting ? 'Creating account...' : 'Create account'}
      </button>

      {error && (
        <p role="alert" className="error-text auth-form__message">
          {error}
        </p>
      )}

      <p className="muted-text auth-form__switch">
        Already have an account?{' '}
        <button type="button" className="auth-form__link" onClick={onSwitchToSignIn}>
          Sign in
        </button>
      </p>
    </form>
  );
}

// Translates /add_user's error shapes (see server/app.py) into copy a
// user filling out this form can act on.
function describeSignUpError(error) {
  if (error.message === 'user_already_exists') {
    return 'That user ID is already taken. Try a different one.';
  }
  if (error.field === 'password') {
    return 'Password must be 8-72 characters.';
  }
  if (error.field) {
    return `${error.field} is required.`;
  }
  return error.message;
}
