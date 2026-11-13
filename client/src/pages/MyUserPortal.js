// Route /projects. The projects the user owns, the projects shared with them,
// and a sidebar with the hardware sets in the system (HWSet1 and HWSet2, created
// by the server). Creating and joining projects lives on /create-join.
// Everything shown here comes from the database; nothing is hard-coded.
import React, { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import HardwareSetList from '../components/HardwareSetList';
import { getAllHardwareSets } from '../api/hardware';
import { getProjectsByOwnership } from '../api/projects';
import { useAuth } from '../context/AuthContext';

const projectPath = (projectId) => `/projects/${encodeURIComponent(projectId)}`;

// One list of projects as a table. The whole row opens the project; the name is
// the real link so keyboard users can reach it. showOwner adds an Owner column
// (left off for "My projects", where the owner is always you).
function ProjectTable({ title, projects, empty, showOwner }) {
  const navigate = useNavigate();
  return (
    <section className="section">
      <h2>{title}</h2>
      {projects.length === 0 ? (
        <div className="empty">{empty}</div>
      ) : (
        <div className="table-wrap">
          <table className="project-table">
            <thead>
              <tr>
                <th scope="col">Name</th>
                <th scope="col">{showOwner ? 'Owner' : 'Project ID'}</th>
                <th scope="col" className="num">Members</th>
                <th scope="col" className="num">Units held</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((p) => {
                const unitsHeld = Object.values(p.hwSets || {}).reduce((sum, n) => sum + n, 0);
                return (
                  <tr key={p.projectId} onClick={() => navigate(projectPath(p.projectId))}>
                    <td><Link to={projectPath(p.projectId)}>{p.projectName}</Link></td>
                    <td>{showOwner ? p.ownerName || 'Unknown' : p.projectId}</td>
                    <td className="num">{p.users?.length || 0}</td>
                    <td className="num">{unitsHeld}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default function MyUserPortal() {
  const { user } = useAuth();

  const [projects, setProjects] = useState({ owned: [], shared: [] });
  const [projectsLoading, setProjectsLoading] = useState(true);
  const [projectsError, setProjectsError] = useState(null);

  const [hwSets, setHwSets] = useState([]);
  const [hwError, setHwError] = useState(null);

  const loadProjects = useCallback(async () => {
    setProjectsLoading(true);
    setProjectsError(null);
    try {
      setProjects(await getProjectsByOwnership(user.userId));
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

  let projectsBody;
  if (projectsLoading) {
    projectsBody = <p className="muted">Loading projects...</p>;
  } else if (projectsError) {
    projectsBody = <p className="msg err">{projectsError}</p>;
  } else {
    projectsBody = (
      <>
        <ProjectTable
          title="My projects"
          projects={projects.owned}
          empty={<p>You haven't created a project yet. <Link to="/create-join">Create a project</Link></p>}
        />
        <ProjectTable
          title="Shared projects"
          projects={projects.shared}
          empty={<p>Nothing is shared with you yet. Ask a teammate for their project ID, then <Link to="/create-join">join it</Link>.</p>}
          showOwner
        />
      </>
    );
  }

  return (
    <>
      <div className="page-header">
        <h1>Projects</h1>
        <Link to="/create-join" className="button">New project</Link>
      </div>

      <div className="with-sidebar">
        <div>{projectsBody}</div>

        <aside>
          <h2>Hardware</h2>
          {hwError ? <p className="msg err">{hwError}</p> : <HardwareSetList sets={hwSets} />}
        </aside>
      </div>
    </>
  );
}
