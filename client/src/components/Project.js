import React, { useState } from 'react';
import FormField from './FormField';
import { createProject, getProject, getUserProjects, joinProject } from '../api/projects';

// "Create new project" and "Use existing project" forms (Figure 2 of the spec).
// Owns only form state and feedback. Both actions are done on behalf of userId
// (the creator / joiner becomes a project member), and once a project is ready
// it is handed to the parent through onSelect(project).
export default function Project({ userId, onSelect }) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [newId, setNewId] = useState('');
  const [existingId, setExistingId] = useState('');
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState(null); // { ok: boolean, text: string }

  // Runs an async action with shared busy/status handling
  async function run(action) {
    setBusy(true);
    setStatus(null);
    try {
      await action();
    } catch (err) {
      setStatus({ ok: false, text: err.message });
    } finally {
      setBusy(false);
    }
  }

  function handleCreate(e) {
    e.preventDefault();
    const projectName = name.trim();
    const projectId = newId.trim();
    if (!projectName || !projectId) {
      setStatus({ ok: false, text: 'Project name and project ID are required.' });
      return;
    }
    run(async () => {
      await createProject(projectName, projectId, description.trim(), userId);
      const project = await getProject(projectId);
      setName('');
      setDescription('');
      setNewId('');
      onSelect(project);
    });
  }

  function handleUseExisting(e) {
    e.preventDefault();
    const projectId = existingId.trim();
    if (!projectId) {
      setStatus({ ok: false, text: 'Enter a project ID.' });
      return;
    }
    run(async () => {
      // Look the project up first so a typo says "Project not found"
      const project = await getProject(projectId);

      // The backend refuses to join a project you're already in, so only join if needed
      const mine = await getUserProjects(userId);
      if (!mine.includes(projectId)) await joinProject(userId, projectId);

      setExistingId('');
      onSelect(project);
    });
  }

  return (
    <section className="card">
      <form onSubmit={handleCreate}>
        <h2>Create new project</h2>
        <FormField id="project-name" label="Name" value={name} onChange={setName} />
        <FormField id="project-description" label="Description" value={description} onChange={setDescription} />
        <FormField id="project-new-id" label="Project ID" value={newId} onChange={setNewId} />
        <button type="submit" disabled={busy}>{busy ? 'Working...' : 'Create project'}</button>
      </form>

      <hr />

      <form onSubmit={handleUseExisting}>
        <h2>Use existing project</h2>
        <FormField id="project-existing-id" label="Project ID" value={existingId} onChange={setExistingId} />
        <button type="submit" disabled={busy}>{busy ? 'Working...' : 'Use project'}</button>
      </form>

      {status && <p className={status.ok ? 'msg ok' : 'msg err'}>{status.text}</p>}
    </section>
  );
}
