import { beforeEach, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

vi.mock('../api/auth.js', () => ({
  signUp: vi.fn(),
  signIn: vi.fn(),
  getCurrentSession: vi.fn(),
  signOut: vi.fn(),
}));

// Project.js/ResourceView fetches real hardware data via api/hardware.js --
// irrelevant to what App.js itself is responsible for (showing auth vs.
// the project picker vs. the resource view, and handing each the right
// identity). Stubbed so these tests only exercise App's own wiring.
vi.mock('../components/Project.js', () => ({
  default: ({ projectId, userId }) => (
    <div data-testid="resource-view">{projectId}:{userId}</div>
  ),
}));

// MyProjectsPage (US-03/US-05) fetches/mutates its own project list --
// irrelevant here too. Stubbed down to the one thing App.js cares about:
// handing it userId and reacting to onOpenProject.
vi.mock('../pages/MyProjectsPage.js', () => ({
  default: ({ userId, onOpenProject }) => (
    <div data-testid="projects-page">
      <span>projects-page:{userId}</span>
      <button type="button" onClick={() => onOpenProject('P2')}>
        Open P2
      </button>
    </div>
  ),
}));

import { getCurrentSession, signIn, signOut, signUp } from '../api/auth.js';
import App from '../App.js';

beforeEach(() => {
  vi.resetAllMocks();
  // TD-02's session check runs on every mount, before anything else
  // renders -- default to "no existing session" so tests that don't care
  // about session restoration still land on the sign-in form as before.
  getCurrentSession.mockRejectedValue(new Error('not_signed_in'));
  signOut.mockResolvedValue({});
});

it('shows the sign-in form by default, once there is no existing session to restore', async () => {
  render(<App />);
  expect(await screen.findByRole('heading', { name: 'Sign in' })).toBeInTheDocument();
});

it('shows a brief checking-session message before the sign-in form appears', async () => {
  let resolveCheck;
  getCurrentSession.mockReturnValue(
    new Promise((_resolve, reject) => {
      resolveCheck = reject;
    })
  );
  render(<App />);

  expect(screen.getByText('Checking session...')).toBeInTheDocument();
  expect(screen.queryByRole('heading', { name: 'Sign in' })).not.toBeInTheDocument();

  resolveCheck(new Error('not_signed_in'));
  expect(await screen.findByRole('heading', { name: 'Sign in' })).toBeInTheDocument();
});

it('switches to the sign-up form and back without signing in', async () => {
  render(<App />);
  await screen.findByRole('heading', { name: 'Sign in' });

  await userEvent.click(screen.getByRole('button', { name: 'Sign up' }));
  expect(screen.getByRole('heading', { name: 'Create an account' })).toBeInTheDocument();

  await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
  expect(screen.getByRole('heading', { name: 'Sign in' })).toBeInTheDocument();
});

it('shows the project picker with the signed-in userId after a successful sign-in', async () => {
  signIn.mockResolvedValue({ username: 'alice', userId: 'alice1' });
  render(<App />);
  await screen.findByRole('heading', { name: 'Sign in' });

  await userEvent.type(screen.getByLabelText('Username'), 'alice');
  await userEvent.type(screen.getByLabelText('User ID'), 'alice1');
  await userEvent.type(screen.getByLabelText('Password'), 'correct horse battery');
  await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));

  expect(await screen.findByTestId('projects-page')).toHaveTextContent('projects-page:alice1');
  expect(screen.getByText('Signed in as alice')).toBeInTheDocument();
});

it('shows the project picker with the created userId after a successful sign-up', async () => {
  signUp.mockResolvedValue({ username: 'bob', userId: 'bob1' });
  render(<App />);
  await screen.findByRole('heading', { name: 'Sign in' });

  await userEvent.click(screen.getByRole('button', { name: 'Sign up' }));
  await userEvent.type(screen.getByLabelText('Username'), 'bob');
  await userEvent.type(screen.getByLabelText('User ID'), 'bob1');
  await userEvent.type(screen.getByLabelText('Password'), 'correct horse battery');
  await userEvent.type(screen.getByLabelText('Confirm password'), 'correct horse battery');
  await userEvent.click(screen.getByRole('button', { name: 'Create account' }));

  expect(await screen.findByTestId('projects-page')).toHaveTextContent('projects-page:bob1');
});

it('opens the resource view for the project selected from the project picker', async () => {
  signIn.mockResolvedValue({ username: 'alice', userId: 'alice1' });
  render(<App />);
  await screen.findByRole('heading', { name: 'Sign in' });

  await userEvent.type(screen.getByLabelText('Username'), 'alice');
  await userEvent.type(screen.getByLabelText('User ID'), 'alice1');
  await userEvent.type(screen.getByLabelText('Password'), 'correct horse battery');
  await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
  await screen.findByTestId('projects-page');

  await userEvent.click(screen.getByRole('button', { name: 'Open P2' }));

  expect(await screen.findByTestId('resource-view')).toHaveTextContent('P2:alice1');
  expect(screen.queryByTestId('projects-page')).not.toBeInTheDocument();
});

it('returns to the project picker from the resource view', async () => {
  signIn.mockResolvedValue({ username: 'alice', userId: 'alice1' });
  render(<App />);
  await screen.findByRole('heading', { name: 'Sign in' });

  await userEvent.type(screen.getByLabelText('Username'), 'alice');
  await userEvent.type(screen.getByLabelText('User ID'), 'alice1');
  await userEvent.type(screen.getByLabelText('Password'), 'correct horse battery');
  await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
  await screen.findByTestId('projects-page');
  await userEvent.click(screen.getByRole('button', { name: 'Open P2' }));
  await screen.findByTestId('resource-view');

  await userEvent.click(screen.getByRole('button', { name: '← Back to my projects' }));

  expect(await screen.findByTestId('projects-page')).toBeInTheDocument();
  expect(screen.queryByTestId('resource-view')).not.toBeInTheDocument();
});

it('returns to the sign-in form after signing out, clearing the session', async () => {
  signIn.mockResolvedValue({ username: 'alice', userId: 'alice1' });
  render(<App />);
  await screen.findByRole('heading', { name: 'Sign in' });

  await userEvent.type(screen.getByLabelText('Username'), 'alice');
  await userEvent.type(screen.getByLabelText('User ID'), 'alice1');
  await userEvent.type(screen.getByLabelText('Password'), 'correct horse battery');
  await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
  await screen.findByTestId('projects-page');

  await userEvent.click(screen.getByRole('button', { name: 'Sign out' }));

  expect(await screen.findByRole('heading', { name: 'Sign in' })).toBeInTheDocument();
  expect(screen.queryByTestId('projects-page')).not.toBeInTheDocument();
  expect(screen.queryByText('Signed in as alice')).not.toBeInTheDocument();
});

it('signing out calls POST /logout, not just clearing local state', async () => {
  signIn.mockResolvedValue({ username: 'alice', userId: 'alice1' });
  render(<App />);
  await screen.findByRole('heading', { name: 'Sign in' });

  await userEvent.type(screen.getByLabelText('Username'), 'alice');
  await userEvent.type(screen.getByLabelText('User ID'), 'alice1');
  await userEvent.type(screen.getByLabelText('Password'), 'correct horse battery');
  await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
  await screen.findByTestId('projects-page');

  await userEvent.click(screen.getByRole('button', { name: 'Sign out' }));
  expect(signOut).toHaveBeenCalledTimes(1);
});

it('still signs out locally even if the /logout call fails', async () => {
  signIn.mockResolvedValue({ username: 'alice', userId: 'alice1' });
  signOut.mockRejectedValue(new Error('network error'));
  render(<App />);
  await screen.findByRole('heading', { name: 'Sign in' });

  await userEvent.type(screen.getByLabelText('Username'), 'alice');
  await userEvent.type(screen.getByLabelText('User ID'), 'alice1');
  await userEvent.type(screen.getByLabelText('Password'), 'correct horse battery');
  await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
  await screen.findByTestId('projects-page');

  await userEvent.click(screen.getByRole('button', { name: 'Sign out' }));
  expect(await screen.findByRole('heading', { name: 'Sign in' })).toBeInTheDocument();
});

it('signing back in after a sign-out starts a fresh username/password field', async () => {
  signIn.mockResolvedValue({ username: 'alice', userId: 'alice1' });
  render(<App />);
  await screen.findByRole('heading', { name: 'Sign in' });

  await userEvent.type(screen.getByLabelText('Username'), 'alice');
  await userEvent.type(screen.getByLabelText('User ID'), 'alice1');
  await userEvent.type(screen.getByLabelText('Password'), 'correct horse battery');
  await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
  await screen.findByTestId('projects-page');
  await userEvent.click(screen.getByRole('button', { name: 'Sign out' }));

  expect(await screen.findByLabelText('Username')).toHaveValue('');
});

it('signing out while viewing a project also resets back to the project picker on the next sign-in', async () => {
  signIn.mockResolvedValue({ username: 'alice', userId: 'alice1' });
  render(<App />);
  await screen.findByRole('heading', { name: 'Sign in' });

  await userEvent.type(screen.getByLabelText('Username'), 'alice');
  await userEvent.type(screen.getByLabelText('User ID'), 'alice1');
  await userEvent.type(screen.getByLabelText('Password'), 'correct horse battery');
  await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
  await screen.findByTestId('projects-page');
  await userEvent.click(screen.getByRole('button', { name: 'Open P2' }));
  await screen.findByTestId('resource-view');

  await userEvent.click(screen.getByRole('button', { name: 'Sign out' }));
  await screen.findByRole('heading', { name: 'Sign in' });

  await userEvent.type(screen.getByLabelText('Username'), 'alice');
  await userEvent.type(screen.getByLabelText('User ID'), 'alice1');
  await userEvent.type(screen.getByLabelText('Password'), 'correct horse battery');
  await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));

  expect(await screen.findByTestId('projects-page')).toBeInTheDocument();
});

// ---------------------------------------------------------------------------
// TD-02 -- session restoration on mount (the point of this file's changes)
// ---------------------------------------------------------------------------

it('restores a signed-in session via GET /me on mount, skipping the sign-in form entirely', async () => {
  getCurrentSession.mockResolvedValue({ username: 'alice', userId: 'alice1' });
  render(<App />);

  expect(await screen.findByTestId('projects-page')).toHaveTextContent('projects-page:alice1');
  expect(screen.getByText('Signed in as alice')).toBeInTheDocument();
  expect(screen.queryByRole('heading', { name: 'Sign in' })).not.toBeInTheDocument();
});

it('falls through to the sign-in form when GET /me rejects (no session, or a network error)', async () => {
  getCurrentSession.mockRejectedValue(new Error('not_signed_in'));
  render(<App />);

  expect(await screen.findByRole('heading', { name: 'Sign in' })).toBeInTheDocument();
  expect(screen.queryByTestId('projects-page')).not.toBeInTheDocument();
});
