import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createProject, getProjectInfo, getUserProjects, joinProject } from '../api/projects.js';

function jsonResponse(status, body) {
  return { ok: status >= 200 && status < 300, status, json: async () => body };
}

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn());
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('joinProject', () => {
  it('POSTs projectId and userId to /join_project and returns the body', async () => {
    fetch.mockResolvedValue(jsonResponse(200, { userId: 'alice1', projectId: 'P1' }));

    const data = await joinProject({ projectId: 'P1', userId: 'alice1' });

    expect(fetch).toHaveBeenCalledWith('/join_project', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ projectId: 'P1', userId: 'alice1' }),
    });
    expect(data).toEqual({ userId: 'alice1', projectId: 'P1' });
  });

  it('throws an Error carrying the server error code on a non-ok response', async () => {
    fetch.mockResolvedValue(jsonResponse(404, { error: 'project_not_found', field: 'projectId' }));

    const error = await joinProject({ projectId: 'NoSuchProject', userId: 'alice1' }).catch(
      (caught) => caught
    );

    expect(error.message).toBe('project_not_found');
    expect(error.field).toBe('projectId');
  });

  it('falls back to a status message when the body has no error field', async () => {
    fetch.mockResolvedValue(jsonResponse(500, {}));

    await expect(joinProject({ projectId: 'P1', userId: 'alice1' })).rejects.toThrow(
      'Request failed with status 500'
    );
  });
});

describe('createProject', () => {
  it('POSTs projectId/projectName/description/userId to /create_project and returns the body', async () => {
    const project = { projectId: 'P2', projectName: 'Robotics Club', description: 'Lab hardware', users: ['alice1'] };
    fetch.mockResolvedValue(jsonResponse(201, { project }));

    const data = await createProject({
      projectId: 'P2',
      projectName: 'Robotics Club',
      description: 'Lab hardware',
      userId: 'alice1',
    });

    expect(fetch).toHaveBeenCalledWith('/create_project', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        projectId: 'P2',
        projectName: 'Robotics Club',
        description: 'Lab hardware',
        userId: 'alice1',
      }),
    });
    expect(data).toEqual({ project });
  });

  it('throws an Error carrying the server error code when the projectId is taken', async () => {
    fetch.mockResolvedValue(jsonResponse(409, { error: 'project_already_exists', field: 'projectId' }));

    const error = await createProject({
      projectId: 'P2',
      projectName: 'Robotics Club',
      description: 'Lab hardware',
      userId: 'alice1',
    }).catch((caught) => caught);

    expect(error.message).toBe('project_already_exists');
    expect(error.field).toBe('projectId');
  });
});

describe('getUserProjects', () => {
  it('POSTs userId to /get_user_projects_list and returns the body', async () => {
    const projects = [{ projectId: 'P2', projectName: 'Robotics Club', description: '', users: ['alice1'] }];
    fetch.mockResolvedValue(jsonResponse(200, { projects }));

    const data = await getUserProjects({ userId: 'alice1' });

    expect(fetch).toHaveBeenCalledWith('/get_user_projects_list', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId: 'alice1' }),
    });
    expect(data).toEqual({ projects });
  });
});

describe('getProjectInfo', () => {
  it('POSTs projectId and userId to /get_project_info and returns the body', async () => {
    const project = { projectId: 'P2', projectName: 'Robotics Club', description: '', users: ['alice1'] };
    fetch.mockResolvedValue(jsonResponse(200, { project }));

    const data = await getProjectInfo({ projectId: 'P2', userId: 'alice1' });

    expect(fetch).toHaveBeenCalledWith('/get_project_info', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ projectId: 'P2', userId: 'alice1' }),
    });
    expect(data).toEqual({ project });
  });

  it('throws an Error carrying the server error code for a non-member', async () => {
    fetch.mockResolvedValue(jsonResponse(403, { error: 'not_a_project_member' }));

    const error = await getProjectInfo({ projectId: 'P2', userId: 'mallory' }).catch((caught) => caught);

    expect(error.message).toBe('not_a_project_member');
  });
});
