import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { fetchProject } from "../api/projectsApi";

// Full page for one project, reached from /projects/:projectId.
function ProjectPage() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  // Members list starts closed; clicking "Members (n)" opens it.
  const [membersOpen, setMembersOpen] = useState(false);

  useEffect(() => {
    // Ignore a slow response if the user has already moved to another project.
    let active = true;
    setLoading(true);
    setError("");

    fetchProject(projectId)
      .then((data) => {
        if (active) setProject(data);
      })
      .catch((requestError) => {
        if (active) setError(requestError.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [projectId]);

  const hardware = Object.entries(project?.hwSets || {});

  return (
    <section className="checkout-page">
      <header className="page-header">
        {/* Title with the project ID tucked right underneath it. */}
        <div className="project-heading">
          <h1 className="page-title">{project ? project.projectName : "Project"}</h1>
          {project && (
            <p className="project-id-line">Project ID: {project.projectId}</p>
          )}
        </div>
        <Link className="page-header-link" to="/dashboard">Back to Dashboard</Link>
      </header>

      <div className="checkout-content">
        {loading && <p className="loading-message">Loading project...</p>}
        {error && <p className="error-banner" role="alert">{error}</p>}

        {project && !loading && (
          // Two columns: description and hardware on the left, members on the right.
          <div className="project-page-layout">
            <div className="project-page-main">
              <div>
                <h2>Description</h2>
                <p>{project.description || "No description yet."}</p>
              </div>

              <div>
                <h2>Hardware</h2>
                {hardware.length === 0 ? (
                  <p className="empty-state">No hardware checked out yet.</p>
                ) : (
                  <ul aria-label="Hardware">
                    {hardware.map(([name, qty]) => (
                      <li key={name}>{name}: {qty}</li>
                    ))}
                  </ul>
                )}
                <nav className="dashboard-links">
                  <Link to="/hardware">Hardware Checkout</Link>
                </nav>
              </div>
            </div>

            <aside className="project-members">
              <h2 className="members-heading">
                <button
                  type="button"
                  className="members-toggle"
                  aria-expanded={membersOpen}
                  aria-controls="project-members-list"
                  onClick={() => setMembersOpen((open) => !open)}
                >
                  Members ({project.users.length})
                  <span aria-hidden="true">{membersOpen ? " ▾" : " ▸"}</span>
                </button>
              </h2>
              {membersOpen && (
                <ul id="project-members-list" aria-label="Members">
                  {project.users.map((userId) => (
                    <li key={userId}>{userId}</li>
                  ))}
                </ul>
              )}
            </aside>
          </div>
        )}
      </div>
    </section>
  );
}

export default ProjectPage;
