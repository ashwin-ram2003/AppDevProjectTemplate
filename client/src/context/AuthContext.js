// Holds who is logged in. The backend has no sessions, so this is only a
// client-side convenience: the userId is sent with each request that needs it.
import React, { createContext, useCallback, useContext, useMemo, useState } from 'react';
import { login, logout } from '../api/users';

// sessionStorage key. For development you can fake a sign-in without the login page:
//   sessionStorage.setItem('haas.user', JSON.stringify({ userId: 'al1' }))  then reload
export const STORAGE_KEY = 'haas.user';

const AuthContext = createContext(null);

// Storage can throw (private windows, blocked site data), so every access is guarded
function readStoredUser() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function writeStoredUser(user) {
  try {
    if (user) sessionStorage.setItem(STORAGE_KEY, JSON.stringify(user));
    else sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    // Not persisting just means a refresh signs the user out
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(readStoredUser); // { userId } | null

  // Rejects with the server message (e.g. "Invalid credentials") when sign-in fails
  const signIn = useCallback(async (userId, password) => {
    await login(userId, password);
    const next = { userId };
    setUser(next);
    writeStoredUser(next);
  }, []);

  const signOut = useCallback(async () => {
    try {
      await logout();
    } finally {
      setUser(null);
      writeStoredUser(null);
    }
  }, []);

  const value = useMemo(() => ({ user, signIn, signOut }), [user, signIn, signOut]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Returns { user, signIn, signOut }. Must be used inside <AuthProvider>.
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
