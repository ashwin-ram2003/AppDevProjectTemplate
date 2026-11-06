import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { fetchProjects, fetchUserProjects, joinProject } from "../api/projectsApi";
import Button from "../components/Button";
import ProjectCard from "../components/ProjectCard";

// Remembers the last user ID so the list reloads when you come back from
// Create or Join. TODO: remove once Sign In (#2) gives us the real user.
const USER_ID_KEY = "dashboardUserId";

const INITIAL_HARDWARE = [
  { name: "HWSet1", capacity: 100, available: 100 },
  { name: "HWSet2", capacity: 100, available: 100 },
];

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
  const [allProjects, setAllProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hardware, setHardware] = useState(INITIAL_HARDWARE);

  const updateHardware = (projectId, hardwareName, quantityChange) => {
    setHardware((items) => items.map((item) => (
      item.name === hardwareName
        ? {
          ...item,
          available: Math.min(item.capacity, item.available - quantityChange),
        }
        : item
    )));
    setProjects((items) => items.map((project) => (
      project.projectId === projectId
        ? {
          ...project,
          hwSets: {
            ...project.hwSets,
            [hardwareName]: (project.hwSets?.[hardwareName] || 0) + quantityChange,
          },
        }
        : project
    )));
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
      const [userProjects, everyProject] = await Promise.all([
        fetchUserProjects(userId),
        fetchProjects(),
      ]);
      setProjects(userProjects);
      setAllProjects(everyProject);
      setLoadedUserId(userId);
      saveUserId(userId);
    } catch (requestError) {
      setProjects([]);
      setAllProjects([]);
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

  const joinAvailableProject = async (projectId) => {
    setError("");
    try {
      const joinedProject = await joinProject({
        projectId,
        userId: loadedUserId,
      });
      setProjects((items) => [...items, joinedProject]);
      setAllProjects((items) => items.map((project) => (
        project.projectId === projectId ? joinedProject : project
      )));
    } catch (requestError) {
      setError(requestError.message);
    }
  };

  const projectIds = new Set(projects.map((project) => project.projectId));
  const availableProjects = allProjects.filter(
    (project) => !projectIds.has(project.projectId)
  );

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
                      hardware={hardware}
                      onUpdateHardware={updateHardware}
                    />
                  ))}
                </ul>
              )}

              {loadedUserId && availableProjects.length > 0 && (
                <>
                  <h2 className="available-projects-title">Available Projects</h2>
                  <ul className="project-list" aria-label="Available projects">
                    {availableProjects.map((project) => (
                      <ProjectCard
                        key={project.projectId}
                        project={project}
                        hardware={hardware}
                        canManage={false}
                        onJoin={joinAvailableProject}
                        onUpdateHardware={updateHardware}
                      />
                    ))}
                  </ul>
                </>
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
