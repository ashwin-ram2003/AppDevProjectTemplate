async function requestJson(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error || "Something went wrong. Please try again.");
  }

  return payload;
}

export async function createProject({ projectName, projectId, description, userId }) {
  return requestJson("/api/projects", {
    method: "POST",
    body: JSON.stringify({ projectName, projectId, description, userId }),
  });
}

export async function joinProject({ projectId, userId }) {
  return requestJson(`/api/projects/${encodeURIComponent(projectId)}/users`, {
    method: "POST",
    body: JSON.stringify({ userId }),
  });
}

export async function fetchProject(projectId) {
  return requestJson(`/api/projects/${encodeURIComponent(projectId)}`);
}

export async function fetchProjects() {
  const payload = await requestJson("/api/projects");
  return payload.projects;
}

export async function fetchUserProjects(userId) {
  const payload = await requestJson(
    `/api/users/${encodeURIComponent(userId)}/projects`
  );
  return payload.projects;
}
