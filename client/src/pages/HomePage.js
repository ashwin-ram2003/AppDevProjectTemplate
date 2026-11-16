import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { fetchUserProjects } from "../api/projectsApi";
import Button from "../components/Button";
import JoinProjectForm from "../components/JoinProjectForm";
import PageHeader from "../components/PageHeader";
import ProjectCard from "../components/ProjectCard";
import { getSignedInUserId, signOut } from "../session";

function HomePage() {
  const navigate = useNavigate();

  const handleSignOut = () => {
    signOut();
    navigate("/", { replace: true });
  };

  // RequireSignIn only lets signed-in users reach this page.
  const userId = getSignedInUserId();
  const [projects, setProjects] = useState([]);
  const [loaded, setLoaded] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  // Only one project's snippet is open at a time; null means none.
  const [expandedId, setExpandedId] = useState(null);
  // Join Project tab starts closed; clicking it opens the form in place.
  const [joinOpen, setJoinOpen] = useState(false);
  // Bumped after a successful join so the project list reloads.
  const [reloadKey, setReloadKey] = useState(0);

  const toggleProject = (projectId) => {
    setExpandedId((current) => (current === projectId ? null : projectId));
  };

  // Load the signed-in user's projects as soon as the page opens.
  useEffect(() => {
    // Ignore a slow response if the page has already closed.
    let active = true;
    setLoading(true);
    setError("");

    fetchUserProjects(userId)
      .then((userProjects) => {
        if (!active) return;
        setProjects(userProjects);
        setLoaded(true);
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
  }, [userId, reloadKey]);

  return (
    <section className="checkout-page">
      {/* Title on the left, who is signed in on the right. */}
      <PageHeader
        title="My Dashboard"
        actions={
          <div className="dashboard-header-actions">
            <p className="signed-in-as">
              Signed in as <strong>{userId}</strong>
            </p>

            <Button variant="primary" onClick={handleSignOut}>
              Sign Out
            </Button>
          </div>
        }
      />

      <div className="checkout-content">
        <p>Welcome to HardwareShare! Manage your projects and hardware resources.</p>

        <div>
          <h2>My Projects</h2>

          {/* Two columns: project list on the left, actions on the right. */}
          <div className="dashboard-layout">
            <div className="dashboard-main">
              {loading && <p className="loading-message">Loading your projects...</p>}
              {error && <p className="error-banner" role="alert">{error}</p>}

              {loaded && !loading && projects.length === 0 && (
                <p className="empty-state">
                  You don't belong to any projects yet. Create one or join one.
                </p>
              )}

              {projects.length > 0 && (
                <ul className="project-list" aria-label="My projects">
                  {projects.map((project) => (
                    <ProjectCard
                      key={project.projectId}
                      project={project}
                      expanded={expandedId === project.projectId}
                      onToggle={() => toggleProject(project.projectId)}
                    />
                  ))}
                </ul>
              )}
            </div>

            <div className="dashboard-links dashboard-actions" aria-label="Project actions">
              <Link to="/projects/new">+ Create Project</Link>

              {/* Join Project is a tab: click to open the form right here. */}
              <div className="join-tab">
                <button
                  type="button"
                  className="join-tab-toggle"
                  aria-expanded={joinOpen}
                  aria-controls="join-tab-panel"
                  onClick={() => setJoinOpen((open) => !open)}
                >
                  Join Project
                  <span aria-hidden="true">{joinOpen ? " ▾" : " ▸"}</span>
                </button>
                {joinOpen && (
                  <div className="join-tab-panel" id="join-tab-panel">
                    <JoinProjectForm onJoined={() => setReloadKey((key) => key + 1)} />
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default HomePage;