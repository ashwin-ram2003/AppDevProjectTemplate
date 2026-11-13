import React, { useState } from 'react';
import FormField from './FormField';
import { createProject, getProject, getUserProjects, joinProject } from '../api/projects';

// "Create new project" and "Use existing project" forms (Figure 2 of the spec),
// shown side by side. Owns only form state and feedback. Both actions are done on
// behalf of userId (the creator / joiner becomes a project member), and once a
// project is ready it is handed to the parent through onSelect(project).
export default function Project({ userId, onSelect }) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [newId, setNewId] = useState('');
  const [existingId, setExistingId] = useState('');
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState(null); // { form: 'create' | 'join', ok: boolean, text: string }

  // Runs an async action for one form with shared busy/status handling
  async function run(form, action) {
    setBusy(true);
    setStatus(null);
    try {
      await action();
    } catch (err) {
      setStatus({ form, ok: false, text: err.message });
    } finally {
      setBusy(false);
    }
  }

  function handleCreate(e) {
    e.preventDefault();
    const projectName = name.trim();
    const projectId = newId.trim();
    if (!projectName || !projectId) {
      setStatus({ form: 'create', ok: false, text: 'Project name and project ID are required.' });
      return;
    }
    run('create', async () => {
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
      setStatus({ form: 'join', ok: false, text: 'Enter a project ID.' });
      return;
    }
    run('join', async () => {
      const mine = await getUserProjects(userId);
      if (!mine.includes(projectId)) await joinProject(userId, projectId);

      const project = await getProject(projectId);
      setExistingId('');
      onSelect(project);
    });
  }

  // Status message for one form, if it has one
  const statusFor = (form) => status?.form === form && (
    <p className={status.ok ? 'msg ok' : 'msg err'} role="status">{status.text}</p>
  );

  return (
    <div className="grid-2">
      <form className="card" onSubmit={handleCreate}>
        <h2>Create new project</h2>
        <p className="muted">You'll own it. Teammates join with the project ID.</p>
        <FormField id="project-name" label="Name" value={name} onChange={setName} />
        <FormField id="project-new-id" label="Project ID" value={newId} onChange={setNewId} />
        <FormField
          id="project-description"
          label="Description (optional)"
          as="textarea"
          value={description}
          onChange={setDescription}
        />
        <button type="submit" disabled={busy}>{busy ? 'Working...' : 'Create project'}</button>
        {statusFor('create')}
      </form>

      <form className="card" onSubmit={handleUseExisting}>
        <h2>Join existing project</h2>
        <p className="muted">It will show up under Shared projects.</p>
        <FormField id="project-existing-id" label="Project ID" value={existingId} onChange={setExistingId} />
        <button type="submit" disabled={busy}>{busy ? 'Working...' : 'Join project'}</button>
        {statusFor('join')}
      </form>
    </div>
  );
}
