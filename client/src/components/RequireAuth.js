import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// Route guard for pages that need a signed-in user. Signed-out visitors are sent
// to /login, with the page they wanted passed along in location state.
export default function RequireAuth({ children }) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) return <Navigate to="/login" replace state={{ from: location }} />;
  return children;
}
