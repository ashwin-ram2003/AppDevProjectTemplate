import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

vi.mock('../api/auth.js', () => ({
  signUp: vi.fn(),
  signIn: vi.fn(),
}));

import { signIn, signUp } from '../api/auth.js';
import MyLoginPage from '../pages/MyLoginPage.js';
import MyRegistrationPage from '../pages/MyRegistrationPage.js';

beforeEach(() => {
  vi.resetAllMocks();
});

async function fillAndSubmit({ username, userId, password, confirmPassword, submitName }) {
  await userEvent.type(screen.getByLabelText('Username'), username);
  await userEvent.type(screen.getByLabelText('User ID'), userId);
  await userEvent.type(screen.getByLabelText('Password'), password);
  if (confirmPassword !== undefined) {
    await userEvent.type(screen.getByLabelText('Confirm password'), confirmPassword);
  }
  // Both pages also render a same-role "switch" link (e.g. a "Sign up"
  // or "Sign in" button) alongside the submit button -- name must be
  // exact, not a loose pattern, or this matches both.
  await userEvent.click(screen.getByRole('button', { name: submitName }));
}

describe('MyRegistrationPage', () => {
  function setup(overrides = {}) {
    const props = {
      onSignedUp: vi.fn().mockResolvedValue(undefined),
      onSwitchToSignIn: vi.fn(),
      ...overrides,
    };
    render(<MyRegistrationPage {...props} />);
    return props;
  }

  it('submits username/userId/password and reports the created account', async () => {
    signUp.mockResolvedValue({ username: 'alice', userId: 'alice1' });
    const props = setup();

    await fillAndSubmit({
      username: 'alice',
      userId: 'alice1',
      password: 'correct horse battery',
      confirmPassword: 'correct horse battery',
      submitName: 'Create account',
    });

    expect(signUp).toHaveBeenCalledWith({
      username: 'alice',
      userId: 'alice1',
      password: 'correct horse battery',
    });
    await waitFor(() =>
      expect(props.onSignedUp).toHaveBeenCalledWith({ username: 'alice', userId: 'alice1' })
    );
  });

  it('rejects a mismatched confirmation locally, without calling the API', async () => {
    const props = setup();

    await fillAndSubmit({
      username: 'alice',
      userId: 'alice1',
      password: 'correct horse battery',
      confirmPassword: 'does not match',
      submitName: 'Create account',
    });

    expect(await screen.findByRole('alert')).toHaveTextContent('Passwords do not match.');
    expect(signUp).not.toHaveBeenCalled();
    expect(props.onSignedUp).not.toHaveBeenCalled();
  });

  it('shows a friendly message when the userId is already taken', async () => {
    signUp.mockRejectedValue(Object.assign(new Error('user_already_exists'), { field: 'userId' }));
    setup();

    await fillAndSubmit({
      username: 'alice',
      userId: 'alice1',
      password: 'correct horse battery',
      confirmPassword: 'correct horse battery',
      submitName: 'Create account',
    });

    expect(await screen.findByRole('alert')).toHaveTextContent('already taken');
  });

  it('shows a friendly message when the password is rejected', async () => {
    signUp.mockRejectedValue(Object.assign(new Error('invalid_input'), { field: 'password' }));
    setup();

    await fillAndSubmit({
      username: 'alice',
      userId: 'alice1',
      password: 'short',
      confirmPassword: 'short',
      submitName: 'Create account',
    });

    expect(await screen.findByRole('alert')).toHaveTextContent('8-72 characters');
  });

  it('disables the submit button while the request is in flight', async () => {
    let finish;
    signUp.mockReturnValue(new Promise((resolve) => { finish = resolve; }));
    setup();

    await fillAndSubmit({
      username: 'alice',
      userId: 'alice1',
      password: 'correct horse battery',
      confirmPassword: 'correct horse battery',
      submitName: 'Create account',
    });

    expect(await screen.findByRole('button', { name: 'Creating account...' })).toBeDisabled();

    finish({ username: 'alice', userId: 'alice1' });
    expect(await screen.findByRole('button', { name: 'Create account' })).toBeEnabled();
  });

  it('calls onSwitchToSignIn when the sign-in link is clicked', async () => {
    const props = setup();
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
    expect(props.onSwitchToSignIn).toHaveBeenCalledTimes(1);
  });
});

describe('MyLoginPage', () => {
  function setup(overrides = {}) {
    const props = {
      onSignedIn: vi.fn().mockResolvedValue(undefined),
      onSwitchToSignUp: vi.fn(),
      ...overrides,
    };
    render(<MyLoginPage {...props} />);
    return props;
  }

  it('submits username/userId/password and reports the authenticated account', async () => {
    signIn.mockResolvedValue({ username: 'alice', userId: 'alice1' });
    const props = setup();

    await fillAndSubmit({
      username: 'alice',
      userId: 'alice1',
      password: 'correct horse battery',
      submitName: 'Sign in',
    });

    expect(signIn).toHaveBeenCalledWith({
      username: 'alice',
      userId: 'alice1',
      password: 'correct horse battery',
    });
    await waitFor(() =>
      expect(props.onSignedIn).toHaveBeenCalledWith({ username: 'alice', userId: 'alice1' })
    );
  });

  it('shows the same message for a wrong password as for an unknown user', async () => {
    signIn.mockRejectedValue(new Error('invalid_credentials'));
    setup();

    await fillAndSubmit({
      username: 'alice',
      userId: 'alice1',
      password: 'wrong',
      submitName: 'Sign in',
    });

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Incorrect username, user ID, or password.'
    );
  });

  it('disables the submit button while the request is in flight', async () => {
    let finish;
    signIn.mockReturnValue(new Promise((resolve) => { finish = resolve; }));
    setup();

    await fillAndSubmit({
      username: 'alice',
      userId: 'alice1',
      password: 'correct horse battery',
      submitName: 'Sign in',
    });

    expect(await screen.findByRole('button', { name: 'Signing in...' })).toBeDisabled();

    finish({ username: 'alice', userId: 'alice1' });
    expect(await screen.findByRole('button', { name: 'Sign in' })).toBeEnabled();
  });

  it('calls onSwitchToSignUp when the sign-up link is clicked', async () => {
    const props = setup();
    await userEvent.click(screen.getByRole('button', { name: 'Sign up' }));
    expect(props.onSwitchToSignUp).toHaveBeenCalledTimes(1);
  });
});
