import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { getCurrentSession, signIn, signOut, signUp } from '../api/auth.js';

function jsonResponse(status, body) {
  return { ok: status >= 200 && status < 300, status, json: async () => body };
}

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn());
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('signUp', () => {
  it('POSTs username/userId/password to /add_user and returns the body', async () => {
    fetch.mockResolvedValue(jsonResponse(201, { username: 'alice', userId: 'alice1' }));

    const data = await signUp({ username: 'alice', userId: 'alice1', password: 'correct horse battery' });

    expect(fetch).toHaveBeenCalledWith('/add_user', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'alice', userId: 'alice1', password: 'correct horse battery' }),
    });
    expect(data).toEqual({ username: 'alice', userId: 'alice1' });
  });

  it('throws an Error carrying the server error code and field on a non-ok response', async () => {
    fetch.mockResolvedValue(jsonResponse(409, { error: 'user_already_exists', field: 'userId' }));

    const error = await signUp({ username: 'alice', userId: 'alice1', password: 'x' }).catch((caught) => caught);

    expect(error.message).toBe('user_already_exists');
    expect(error.field).toBe('userId');
  });
});

describe('signIn', () => {
  it('POSTs username/userId/password to /login and returns the body', async () => {
    fetch.mockResolvedValue(jsonResponse(200, { username: 'alice', userId: 'alice1' }));

    const data = await signIn({ username: 'alice', userId: 'alice1', password: 'correct horse battery' });

    expect(fetch).toHaveBeenCalledWith('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'alice', userId: 'alice1', password: 'correct horse battery' }),
    });
    expect(data).toEqual({ username: 'alice', userId: 'alice1' });
  });

  it('throws invalid_credentials on a 401, with no field (same response for wrong user or password)', async () => {
    fetch.mockResolvedValue(jsonResponse(401, { error: 'invalid_credentials' }));

    const error = await signIn({ username: 'alice', userId: 'alice1', password: 'wrong' }).catch((caught) => caught);

    expect(error.message).toBe('invalid_credentials');
    expect(error.field).toBeUndefined();
  });
});

describe('getCurrentSession', () => {
  it('GETs /me and returns the body on success', async () => {
    fetch.mockResolvedValue(jsonResponse(200, { username: 'alice', userId: 'alice1' }));

    const data = await getCurrentSession();

    expect(fetch).toHaveBeenCalledWith('/me');
    expect(data).toEqual({ username: 'alice', userId: 'alice1' });
  });

  it('throws not_signed_in on a 401 (no existing session)', async () => {
    fetch.mockResolvedValue(jsonResponse(401, { error: 'not_signed_in' }));

    await expect(getCurrentSession()).rejects.toThrow('not_signed_in');
  });
});

describe('signOut', () => {
  it('POSTs an empty body to /logout', async () => {
    fetch.mockResolvedValue(jsonResponse(200, {}));

    await signOut();

    expect(fetch).toHaveBeenCalledWith('/logout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });
  });
});
