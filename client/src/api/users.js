// Thin wrapper around the Flask user routes. Components never call fetch directly.
import { post } from './http';

// Rejects with "Invalid credentials" on a bad userId/password.
export const login = (userId, password) => post('/login', { userId, password });

// Rejects with "That userId is already taken" when the userId exists.
export const addUser = (username, userId, password) =>
  post('/add_user', { username, userId, password });
