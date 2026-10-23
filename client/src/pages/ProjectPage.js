// Route /projects/:projectId.
// Reads :projectId from the URL, loads the project with getProject to show its name
// and description (not found -> message + link back), and renders <Navbar/> and
// <Checkout projectId userId/> with userId from useAuth().
import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import Checkout from '../components/Checkout';
import Navbar from '../components/Navbar';
import { getProject } from '../api/projects';
import { useAuth } from '../context/AuthContext';

export default function ProjectPage() {
  const { projectId } = useParams();
  const { user } = useAuth();

  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Ignore a slow response if the user has already moved to another project
    let cancelled = false;
    setLoading(true);
    setError(null);
    getProject(projectId)
      .then((p) => { if (!cancelled) setProject(p); })
      .catch((err) => { if (!cancelled) setError(err.message); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [projectId]);

  let body;
  if (loading) {
    body = <p className="muted">Loading project...</p>;
  } else if (error) {
    body = (
      <section className="card">
        <h1>Project unavailable</h1>
        <p className="msg err">{error}</p>
        <p><Link to="/projects">Back to my projects</Link></p>
      </section>
    );
  } else {
    const memberCount = project.users?.length || 0;
    body = (
      <>
        <p><Link to="/projects">&larr; My projects</Link></p>
        <h1>{project.projectName}</h1>
        <p className="muted">
          Project ID: {project.projectId}
          {memberCount > 0 && ` · ${memberCount} member${memberCount === 1 ? '' : 's'}`}
        </p>
        {project.description && <p>{project.description}</p>}
        <Checkout projectId={project.projectId} userId={user.userId} />
      </>
    );
  }

  return (
    <>
      <Navbar />
      <main>{body}</main>
    </>
  );
}