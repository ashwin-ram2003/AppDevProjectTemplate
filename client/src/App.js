import { useEffect, useState } from 'react';
import ResourceView from './components/Project.js';
import MyLoginPage from './pages/MyLoginPage.js';
import MyRegistrationPage from './pages/MyRegistrationPage.js';
import MyProjectsPage from './pages/MyProjectsPage.js';
import { getCurrentSession, signOut } from './api/auth.js';
import './App.css';

export default function App() {
  const [account, setAccount] = useState(null);
  const [authView, setAuthView] = useState('signIn');
  // US-03/US-05 -- null means "show the project picker"; set once the
  // user opens (or creates/joins) a project from MyProjectsPage.
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  // TD-02 -- true only for the brief GET /me round-trip on first mount.
  // Without this, the sign-in form would flash on screen for a moment
  // even when a valid session is about to restore the resource view.
  const [checkingSession, setCheckingSession] = useState(true);

  // TD-02 -- on first mount, ask the server (not localStorage -- the
  // session is a signed, httpOnly cookie the browser already attached to
  // this request) whether we're still signed in from before. A refresh,
  // or even a server restart (the signing key is stable across restarts
  // via server/.env's SECRET_KEY), restores the same signed-in view
  // instead of asking to sign in again.
  useEffect(() => {
    let isCurrent = true;
    getCurrentSession()
      .then((session) => {
        if (isCurrent) setAccount(session);
      })
      .catch(() => {
        // No session (401) or a network hiccup -- either way, nothing to
        // restore. Fall through to the sign-in form below.
      })
      .finally(() => {
        if (isCurrent) setCheckingSession(false);
      });
    return () => {
      isCurrent = false;
    };
  }, []);

  // Runs after both sign-in and sign-up (US-01/US-02). Lands on the
  // project picker (MyProjectsPage) rather than any one project --
  // there's no single project every account belongs to anymore.
  function handleAuthenticated(newAccount) {
    setAccount(newAccount);
  }

  async function handleSignOut() {
    try {
      await signOut();
    } catch (error) {
      // Non-fatal -- clear local state regardless so sign-out never gets
      // stuck on a network error; worst case the old session cookie
      // lingers until it's overwritten by the next sign-in.
    }
    setAccount(null);
    setAuthView('signIn');
    setSelectedProjectId(null);
  }

  if (checkingSession) {
    return (
      <div className="app-container">
        <p className="muted-text">Checking session...</p>
      </div>
    );
  }

  if (!account) {
    return (
      <div className="app-container">
        {authView === 'signIn' ? (
          <MyLoginPage onSignedIn={handleAuthenticated} onSwitchToSignUp={() => setAuthView('signUp')} />
        ) : (
          <MyRegistrationPage onSignedUp={handleAuthenticated} onSwitchToSignIn={() => setAuthView('signIn')} />
        )}
      </div>
    );
  }

  return (
    <div className="app-container">
      <p className="app-session">
        <span className="muted-text">Signed in as {account.username}</span>
        <button type="button" className="app-session__sign-out" onClick={handleSignOut}>
          Sign out
        </button>
      </p>

      {selectedProjectId ? (
        <>
          <h1 className="app-heading">Project {selectedProjectId} — Hardware Resources</h1>
          <button
            type="button"
            className="app-back-to-projects"
            onClick={() => setSelectedProjectId(null)}
          >
            ← Back to my projects
          </button>
          <ResourceView projectId={selectedProjectId} userId={account.userId} />
        </>
      ) : (
        <MyProjectsPage userId={account.userId} onOpenProject={setSelectedProjectId} />
      )}
    </div>
  );
}
