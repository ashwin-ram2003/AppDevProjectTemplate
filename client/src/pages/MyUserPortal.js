// Route /projects. Project area from Figure 2 (needs a logged-in user):
// the user's projects, the create / use-existing project forms, and the hardware
// sets in the system (with a form to add sets such as HWSet1 and HWSet2).
// Everything shown here comes from the database; nothing is hard-coded.
import React, { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import HardwareSetForm from '../components/HardwareSetForm';
import HardwareSetList from '../components/HardwareSetList';
import Navbar from '../components/Navbar';
import Project from '../components/Project';
import { createHardwareSet, getAllHardwareSets } from '../api/hardware';
import { getProject, getUserProjects } from '../api/projects';
import { useAuth } from '../context/AuthContext';

export default function MyUserPortal() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [projects, setProjects] = useState([]);
  const [projectsLoading, setProjectsLoading] = useState(true);
  const [projectsError, setProjectsError] = useState(null);

  const [hwSets, setHwSets] = useState([]);
  const [hwError, setHwError] = useState(null);

  // The user record holds project IDs; fetch each project for its name and description
  const loadProjects = useCallback(async () => {
    setProjectsLoading(true);
    setProjectsError(null);
    try {
      const ids = await getUserProjects(user.userId);
      // One missing project shouldn't break the whole list, so skip ones that fail
      const results = await Promise.allSettled(ids.map((id) => getProject(id)));
      setProjects(results.filter((r) => r.status === 'fulfilled').map((r) => r.value));
    } catch (err) {
      setProjectsError(err.message);
    } finally {
      setProjectsLoading(false);
    }
  }, [user.userId]);

  const loadHardware = useCallback(async () => {
    try {
      setHwSets(await getAllHardwareSets());
      setHwError(null);
    } catch (err) {
      setHwError(err.message);
    }
  }, []);

  useEffect(() => { loadProjects(); }, [loadProjects]);
  useEffect(() => { loadHardware(); }, [loadHardware]);

  // HardwareSetForm shows its own success/error message from this promise
  async function handleCreateHardwareSet(name, capacity) {
    await createHardwareSet(name, capacity);
    await loadHardware();
  }

  return (
    <>
      <Navbar />
      <main>
        <h1>Projects</h1>

        <section className="card">
          <h2>My projects</h2>
          {projectsLoading && <p className="muted">Loading...</p>}
          {projectsError && <p className="msg err">{projectsError}</p>}
          {!projectsLoading && !projectsError && projects.length === 0 && (
            <p className="muted">You aren't in any projects yet. Create one or use an existing one below.</p>
          )}
          {projects.length > 0 && (
            <ul>
              {projects.map((p) => (
                <li key={p.projectId}>
                  <Link to={`/projects/${encodeURIComponent(p.projectId)}`}>
                    <strong>{p.projectName}</strong>
                  </Link>
                  <span className="muted"> ({p.projectId})</span>
                  {p.description && <div className="muted">{p.description}</div>}
                </li>
              ))}
            </ul>
          )}
        </section>

        <Project
          userId={user.userId}
          onSelect={(project) => navigate(`/projects/${encodeURIComponent(project.projectId)}`)}
        />

        <section className="card">
          <h2>Hardware sets</h2>
          {hwError ? <p className="msg err">{hwError}</p> : <HardwareSetList sets={hwSets} />}
          <HardwareSetForm title="Add a hardware set" onSubmit={handleCreateHardwareSet} />
        </section>
      </main>
    </>
  );
}
