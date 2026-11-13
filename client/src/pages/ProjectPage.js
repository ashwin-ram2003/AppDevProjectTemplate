// Route /projects/:projectId (not in the nav; reached from a project card).
// Reads :projectId from the URL, loads the project with getProject to show its name,
// owner and description (not found -> message + link back), and renders
// <Checkout projectId userId/> with userId from useAuth(). The nav bar comes from AppLayout.
import React, { useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import Checkout from '../components/Checkout';
import Modal from '../components/Modal';
import { getProject } from '../api/projects';
import { useAuth } from '../context/AuthContext';

export default function ProjectPage() {
  const { projectId } = useParams();
  const { user } = useAuth();

  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // Show members
  const [showMembers, setShowMembers] = useState(false);

  const closeMembers = useCallback(() => setShowMembers(false), []);

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

  const backLink = <Link to="/projects" className="back-link">&larr; Projects</Link>;

  if (loading) {
    return <p className="muted">Loading project...</p>;
  }
  if (error) {
    return (
      <>
        {backLink}
        <h1>Project unavailable</h1>
        <p className="msg err">{error}</p>
      </>
    );
  }
  // Members information
  const members = project.memberNames || [];
  const memberCount = project.users?.length || 0;
  return (
    <>
      {backLink}
      <h1>{project.projectName}</h1>
      {project.description && <p>{project.description}</p>}
      <dl className="details">
        {project.ownerName && <div><dt>Owner</dt><dd>{project.ownerName}</dd></div>}
        <div>
          <dt>Members</dt>
          <dd>
            <button
              type="button"
              className="secondary"
              style={{ padding: '2px 8px', fontSize: '0.85rem', minHeight: 'auto' }}
              onClick={() => setShowMembers(true)}
            >
              {memberCount}
            </button>
          </dd>
        </div>
        <div><dt>Project ID</dt><dd>{project.projectId}</dd></div>
      </dl>

      <Modal open={showMembers} title={`Members (${memberCount})`} onClose={closeMembers}>
        {members.length === 0 ? (
          <p className="muted">No members found.</p>
        ) : (
          <ul>
            {members.map((username, idx) => (
              <li key={`${username}-${idx}`}>{username}</li>
            ))}
          </ul>
        )}
      </Modal>

      <Checkout projectId={project.projectId} userId={user.userId} />
    </>
  );
}