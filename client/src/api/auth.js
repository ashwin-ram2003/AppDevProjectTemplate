async function parseErrorBody(response) {
  try {
    const body = await response.json();
    return body || {};
  } catch (parseError) {
    return {};
  }
}

async function throwForErrorResponse(response) {
  const body = await parseErrorBody(response);
  const message = body.error ? body.error : `Request failed with status ${response.status}`;
  const error = new Error(message);
  if (body.field) {
    error.field = body.field;
  }
  throw error;
}

async function postJson(path, payload) {
  const response = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    await throwForErrorResponse(response);
  }

  return response.json();
}

async function getJson(path) {
  const response = await fetch(path);

  if (!response.ok) {
    await throwForErrorResponse(response);
  }

  return response.json();
}

// US-01 -- create an account. Resolves with { username, userId } on
// success; rejects (error.field set) on invalid input, a taken userId
// (error.message === 'user_already_exists'), or a rejected password
// (error.message === 'invalid_input'). Also establishes a session
// server-side (TD-02), same as signIn.
export async function signUp({ username, userId, password }) {
  return postJson('/add_user', { username, userId, password });
}

// US-02 -- authenticate. Resolves with { username, userId } on success;
// rejects with error.message === 'invalid_credentials' on any mismatch
// (wrong password or unknown user -- the server deliberately doesn't say
// which, see server/app.py's /login route).
export async function signIn({ username, userId, password }) {
  return postJson('/login', { username, userId, password });
}

// TD-02 -- check whether a session cookie from a previous sign-in/up is
// still valid (e.g. right after a page refresh). Resolves with
// { username, userId } if so; rejects (error.message === 'not_signed_in',
// or a network error) otherwise -- the caller treats any rejection the
// same way: show the sign-in form.
export async function getCurrentSession() {
  return getJson('/me');
}

// TD-02 -- clears the server-side session. The caller should clear its
// own local signed-in state regardless of whether this call succeeds, so
// sign-out never gets stuck on a network error.
export async function signOut() {
  return postJson('/logout', {});
}
