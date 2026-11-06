import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { fetchUserProjects } from "../api/projectsApi";
import Button from "../components/Button";
import ProjectCard from "../components/ProjectCard";

// Remembers the last user ID so the list reloads when you come back from
// Create or Join. TODO: remove once Sign In (#2) gives us the real user.
const USER_ID_KEY = "dashboardUserId";

function readSavedUserId() {
  try {
    return sessionStorage.getItem(USER_ID_KEY) || "";
  } catch {
    return "";
  }
}

function saveUserId(userId) {
  try {
    sessionStorage.setItem(USER_ID_KEY, userId);
  } catch {
    // Storage can be blocked (private mode); the page still works without it.
  }
}

function HomePage() {
  const [userIdInput, setUserIdInput] = useState(readSavedUserId);
  const [loadedUserId, setLoadedUserId] = useState("");
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  // Only one project's snippet is open at a time; null means none.
  const [expandedId, setExpandedId] = useState(null);

  const toggleProject = (projectId) => {
    setExpandedId((current) => (current === projectId ? null : projectId));
  };

  const loadProjects = async (rawUserId) => {
    const userId = rawUserId.trim();
    setError("");
    if (!userId) {
      setError("Enter your user ID to see your projects.");
      return;
    }

    setLoading(true);
    try {
      const userProjects = await fetchUserProjects(userId);
      setProjects(userProjects);
      setExpandedId(null);
      setLoadedUserId(userId);
      saveUserId(userId);
    } catch (requestError) {
      setProjects([]);
      setLoadedUserId("");
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  // Load right away if we already know who the user is.
  useEffect(() => {
    const savedUserId = readSavedUserId();
    if (savedUserId) {
      loadProjects(savedUserId);
    }
  }, []); // Empty list: run once when the page opens.

  const handleSubmit = (event) => {
    event.preventDefault();
    loadProjects(userIdInput);
  };

  return (
    <section className="checkout-page">
      <h1 className="page-title">My Dashboard</h1>

      <div className="checkout-content">
        <p>Welcome to HardwareShare! Manage your projects and hardware resources.</p>

        <div>
          <h2>My Projects</h2>

          {/* Two columns: project list on the left, actions on the right. */}
          <div className="dashboard-layout">
            <div className="dashboard-main">
              {/* TODO: remove this form and use the signed-in user's ID once
                  Sign In (#2) is done. */}
              <form className="user-id-form" onSubmit={handleSubmit}>
                <div className="field-row">
                  <label htmlFor="dashboard-user-id">User ID</label>
                  <input
                    id="dashboard-user-id"
                    name="userId"
                    type="text"
                    placeholder="Your user ID"
                    value={userIdInput}
                    onChange={(event) => setUserIdInput(event.target.value)}
                  />
                </div>
                <Button type="submit" variant="primary" disabled={loading}>
                  {loading ? "Loading..." : "Show My Projects"}
                </Button>
              </form>

              {error && <p className="error-banner" role="alert">{error}</p>}

              {loadedUserId && !loading && projects.length === 0 && (
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

            <nav className="dashboard-links dashboard-actions" aria-label="Project actions">
              <Link to="/projects/new">+ Create Project</Link>
              <Link to="/projects/join">Join Project</Link>
            </nav>
          </div>
        </div>
      </div>
    </section>
  );
}

export default HomePage;
