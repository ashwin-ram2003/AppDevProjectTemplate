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
  // Carried through only when present -- the 409 over-checkout and
  // over-checkin cases need these to say how many units are on hand or
  // checked out.
  if (typeof body.onHand === 'number') {
    error.onHand = body.onHand;
  }
  if (typeof body.checkedOut === 'number') {
    error.checkedOut = body.checkedOut;
  }
  if (typeof body.requested === 'number') {
    error.requested = body.requested;
  }
  if (body.field) {
    error.field = body.field;
  }
  throw error;
}

export async function fetchHardware(projectId, userId) {
  const params = new URLSearchParams({ projectId, userId });
  const response = await fetch(`/api/hardware?${params.toString()}`);

  if (!response.ok) {
    await throwForErrorResponse(response);
  }

  return response.json();
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

export async function createHardwareSet(payload) {
  return postJson('/api/hardware/create', payload);
}

export async function renameHardwareSet(payload) {
  return postJson('/api/hardware/rename', payload);
}

export async function setHardwareSetActive(payload) {
  return postJson('/api/hardware/set_active', payload);
}

export async function checkinHardware(payload) {
  return postJson('/api/hardware/checkin', payload);
}

export async function checkoutHardware(payload) {
  return postJson('/api/hardware/checkout', payload);
}

export async function requestHardware(payload) {
  return postJson('/api/hardware/request', payload);
}

export async function releaseRequest(payload) {
  return postJson('/api/hardware/release', payload);
}
