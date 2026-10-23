// Thin wrapper around the Flask project routes. Components never call fetch directly.
import { post } from './http';

// userId is optional: when given, the backend adds the creator to the project.
export const createProject = (projectName, projectId, description, userId) =>
  post('/create_project', { projectName, projectId, description, userId });

// Returns the project document: { projectName, projectId, description, hwSets, users }
export async function getProject(projectId) {
  const { project } = await post('/get_project_info', { projectId });
  return project;
}

// Adds the user to an existing project. Rejects when the project doesn't exist.
export const joinProject = (userId, projectId) =>
  post('/join_project', { userId, projectId });

// Returns an array of project IDs the user belongs to.
export async function getUserProjects(userId) {
  const { projects } = await post('/get_user_projects_list', { userId });
  return projects;
}
