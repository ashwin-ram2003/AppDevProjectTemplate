import { beforeEach, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

vi.mock('../api/projects.js', () => ({
  createProject: vi.fn(),
  getUserProjects: vi.fn(),
  joinProject: vi.fn(),
}));

import { createProject, getUserProjects, joinProject } from '../api/projects.js';
import MyProjectsPage from '../pages/MyProjectsPage.js';

beforeEach(() => {
  vi.resetAllMocks();
});

it('shows a loading message, then the list of projects the user belongs to', async () => {
  getUserProjects.mockResolvedValue({
    projects: [
      { projectId: 'P1', projectName: 'Original Project', description: 'Seeded project', users: ['alice1'] },
      { projectId: 'P2', projectName: 'Robotics Club', description: 'Lab hardware', users: ['alice1'] },
    ],
  });

  render(<MyProjectsPage userId="alice1" onOpenProject={vi.fn()} />);

  expect(screen.getByText('Loading your projects...')).toBeInTheDocument();

  expect(await screen.findByText('Original Project')).toBeInTheDocument();
  expect(screen.getByText('Robotics Club')).toBeInTheDocument();
  expect(getUserProjects).toHaveBeenCalledWith({ userId: 'alice1' });
});

it('shows an empty-state message when the user belongs to no projects', async () => {
  getUserProjects.mockResolvedValue({ projects: [] });

  render(<MyProjectsPage userId="alice1" onOpenProject={vi.fn()} />);

  expect(await screen.findByText(/not part of any project yet/)).toBeInTheDocument();
});

it('surfaces a load error instead of silently showing an empty list', async () => {
  getUserProjects.mockRejectedValue(new Error('network error'));

  render(<MyProjectsPage userId="alice1" onOpenProject={vi.fn()} />);

  expect(await screen.findByRole('alert')).toHaveTextContent('network error');
});

it('calls onOpenProject with the chosen projectId when "Open" is clicked', async () => {
  getUserProjects.mockResolvedValue({
    projects: [{ projectId: 'P2', projectName: 'Robotics Club', description: '', users: ['alice1'] }],
  });
  const onOpenProject = vi.fn();

  render(<MyProjectsPage userId="alice1" onOpenProject={onOpenProject} />);
  await screen.findByText('Robotics Club');

  await userEvent.click(screen.getByRole('button', { name: 'Open' }));

  expect(onOpenProject).toHaveBeenCalledWith('P2');
});

it('creates a project and opens it on success', async () => {
  getUserProjects.mockResolvedValue({ projects: [] });
  createProject.mockResolvedValue({
    project: { projectId: 'P2', projectName: 'Robotics Club', description: 'Lab hardware', users: ['alice1'] },
  });
  const onOpenProject = vi.fn();

  render(<MyProjectsPage userId="alice1" onOpenProject={onOpenProject} />);
  await screen.findByText(/not part of any project yet/);

  const projectIdInputs = screen.getAllByLabelText('Project ID');
  await userEvent.type(projectIdInputs[0], 'P2');
  await userEvent.type(screen.getByLabelText('Name'), 'Robotics Club');
  await userEvent.type(screen.getByLabelText('Description'), 'Lab hardware');
  await userEvent.click(screen.getByRole('button', { name: 'Create project' }));

  expect(createProject).toHaveBeenCalledWith({
    projectId: 'P2',
    projectName: 'Robotics Club',
    description: 'Lab hardware',
    userId: 'alice1',
  });
  expect(onOpenProject).toHaveBeenCalledWith('P2');
});

it('shows an error and does not open anything when creating a project fails', async () => {
  getUserProjects.mockResolvedValue({ projects: [] });
  const error = new Error('project_already_exists');
  error.field = 'projectId';
  createProject.mockRejectedValue(error);
  const onOpenProject = vi.fn();

  render(<MyProjectsPage userId="alice1" onOpenProject={onOpenProject} />);
  await screen.findByText(/not part of any project yet/);

  const projectIdInputs = screen.getAllByLabelText('Project ID');
  await userEvent.type(projectIdInputs[0], 'P1');
  await userEvent.type(screen.getByLabelText('Name'), 'Collides with seeded project');
  await userEvent.type(screen.getByLabelText('Description'), 'desc');
  await userEvent.click(screen.getByRole('button', { name: 'Create project' }));

  expect(await screen.findByText('That project ID is already taken. Try a different one.')).toBeInTheDocument();
  expect(onOpenProject).not.toHaveBeenCalled();
});

it('joins a project by ID and opens it on success', async () => {
  getUserProjects.mockResolvedValue({ projects: [] });
  joinProject.mockResolvedValue({ projectId: 'P3', userId: 'alice1' });
  const onOpenProject = vi.fn();

  render(<MyProjectsPage userId="alice1" onOpenProject={onOpenProject} />);
  await screen.findByText(/not part of any project yet/);

  const projectIdInputs = screen.getAllByLabelText('Project ID', { selector: 'input' });
  await userEvent.type(projectIdInputs[1], 'P3');
  await userEvent.click(screen.getByRole('button', { name: 'Join project' }));

  expect(joinProject).toHaveBeenCalledWith({ projectId: 'P3', userId: 'alice1' });
  expect(onOpenProject).toHaveBeenCalledWith('P3');
});

it('shows an error when joining a nonexistent project fails', async () => {
  getUserProjects.mockResolvedValue({ projects: [] });
  joinProject.mockRejectedValue(new Error('project_not_found'));
  const onOpenProject = vi.fn();

  render(<MyProjectsPage userId="alice1" onOpenProject={onOpenProject} />);
  await screen.findByText(/not part of any project yet/);

  const projectIdInputs = screen.getAllByLabelText('Project ID', { selector: 'input' });
  await userEvent.type(projectIdInputs[1], 'NoSuchProject');
  await userEvent.click(screen.getByRole('button', { name: 'Join project' }));

  expect(await screen.findByText('No project with that ID exists.')).toBeInTheDocument();
  expect(onOpenProject).not.toHaveBeenCalled();
});
