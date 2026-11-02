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

// US-04 -- add userId to projectId's membership list. Idempotent on the
// server (joining twice is a no-op), so this is safe to call on every
// sign-in/sign-up, not just once.
export async function joinProject({ projectId, userId }) {
  return postJson('/join_project', { projectId, userId });
}

// US-03 -- create a new project with userId as its first member.
export async function createProject({ projectId, projectName, description, userId }) {
  return postJson('/create_project', { projectId, projectName, description, userId });
}

// US-05 -- every project userId belongs to.
export async function getUserProjects({ userId }) {
  return postJson('/get_user_projects_list', { userId });
}

// Project name/description for one project, gated by membership.
export async function getProjectInfo({ projectId, userId }) {
  return postJson('/get_project_info', { projectId, userId });
}
