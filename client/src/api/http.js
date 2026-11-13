// Shared fetch helper for the Flask API. The api/ wrappers use it so components
// only ever deal with resolved data or a thrown Error carrying a readable message.

// POST JSON to the backend and return the parsed body.
// Throws when the server can't be reached, when the HTTP status is not ok,
// or when the body says success: false.
export async function post(path, body = {}) {
  let res;
  try {
    res = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
  } catch {
    throw new Error('Could not reach the server. Is the backend running?');
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.success === false) {
    throw new Error(data.message || `Request failed (${res.status})`);
  }
  return data;
}
