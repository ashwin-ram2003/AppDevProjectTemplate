import { useCallback, useEffect, useState } from 'react';
import { createProject, getUserProjects, joinProject } from '../api/projects.js';

/**
 * US-03/US-05 -- lists every project the signed-in user belongs to, and
 * lets them create a new project or join an existing one by ID. Picking
 * "Open" on a project hands its projectId back to the caller, which
 * decides what to render next (the resource view).
 *
 * Data source: fetches/mutates via client/src/api/projects.js
 * No hard-coded fallback: this component renders nothing it was not given or told.
 *
 * @component
 * @param {Object} props
 * @param {string} props.userId - The signed-in user's id. No fallback/default.
 * @param {Function} props.onOpenProject - Called with a projectId when the
 *   user picks a project to open.
 */
export default function MyProjectsPage({ userId, onOpenProject }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  const [newProjectId, setNewProjectId] = useState('');
  const [newProjectName, setNewProjectName] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [createError, setCreateError] = useState(null);
  const [creating, setCreating] = useState(false);

  const [joinProjectId, setJoinProjectId] = useState('');
  const [joinError, setJoinError] = useState(null);
  const [joining, setJoining] = useState(false);

  const loadProjects = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const data = await getUserProjects({ userId });
      setProjects(data.projects);
    } catch (error) {
      setLoadError(error.message);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  async function handleCreate(event) {
    event.preventDefault();
    setCreateError(null);
    setCreating(true);
    try {
      const { project } = await createProject({
        projectId: newProjectId,
        projectName: newProjectName,
        description: newDescription,
        userId,
      });
      setNewProjectId('');
      setNewProjectName('');
      setNewDescription('');
      await loadProjects();
      onOpenProject(project.projectId);
    } catch (error) {
      setCreateError(describeProjectError(error));
    } finally {
      setCreating(false);
    }
  }

  async function handleJoin(event) {
    event.preventDefault();
    setJoinError(null);
    setJoining(true);
    try {
      await joinProject({ projectId: joinProjectId, userId });
      const joinedProjectId = joinProjectId;
      setJoinProjectId('');
      await loadProjects();
      onOpenProject(joinedProjectId);
    } catch (error) {
      setJoinError(describeProjectError(error));
    } finally {
      setJoining(false);
    }
  }

  return (
    <div className="projects-page">
      <h2>My Projects</h2>

      {loading && <p className="muted-text">Loading your projects...</p>}
      {loadError && (
        <p role="alert" className="error-text">
          {loadError}
        </p>
      )}

      {!loading && !loadError && projects.length === 0 && (
        <p className="muted-text">
          You're not part of any project yet. Create one or join one below.
        </p>
      )}

      {!loading && !loadError && projects.length > 0 && (
        <ul className="projects-page__list">
          {projects.map((project) => (
            <li key={project.projectId} className="projects-page__item">
              <div>
                <strong>{project.projectName}</strong>{' '}
                <span className="muted-text">({project.projectId})</span>
                {project.description && <p className="muted-text">{project.description}</p>}
              </div>
              <button type="button" onClick={() => onOpenProject(project.projectId)}>
                Open
              </button>
            </li>
          ))}
        </ul>
      )}

      <form className="auth-form" onSubmit={handleCreate}>
        <h3>Create a project</h3>

        <label className="auth-form__field">
          Project ID
          <input
            type="text"
            value={newProjectId}
            onChange={(event) => setNewProjectId(event.target.value)}
            required
          />
        </label>

        <label className="auth-form__field">
          Name
          <input
            type="text"
            value={newProjectName}
            onChange={(event) => setNewProjectName(event.target.value)}
            required
          />
        </label>

        <label className="auth-form__field">
          Description
          <input
            type="text"
            value={newDescription}
            onChange={(event) => setNewDescription(event.target.value)}
            required
          />
        </label>

        <button type="submit" disabled={creating}>
          {creating ? 'Creating...' : 'Create project'}
        </button>

        {createError && (
          <p role="alert" className="error-text auth-form__message">
            {createError}
          </p>
        )}
      </form>

      <form className="auth-form" onSubmit={handleJoin}>
        <h3>Join a project</h3>

        <label className="auth-form__field">
          Project ID
          <input
            type="text"
            value={joinProjectId}
            onChange={(event) => setJoinProjectId(event.target.value)}
            required
          />
        </label>

        <button type="submit" disabled={joining}>
          {joining ? 'Joining...' : 'Join project'}
        </button>

        {joinError && (
          <p role="alert" className="error-text auth-form__message">
            {joinError}
          </p>
        )}
      </form>
    </div>
  );
}

// Translates /create_project's and /join_project's error shapes into
// copy a user filling out either form can act on.
function describeProjectError(error) {
  if (error.message === 'project_already_exists') {
    return 'That project ID is already taken. Try a different one.';
  }
  if (error.message === 'project_not_found') {
    return 'No project with that ID exists.';
  }
  if (error.field) {
    return `${error.field} is required.`;
  }
  return error.message;
}
