import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import {
  checkinHardware,
  checkoutHardware,
  fetchHardwareSets,
} from "../api/hardwareApi";
import { fetchProject, leaveProject } from "../api/projectsApi";
import Button from "../components/Button";
import HardwareSetRow from "../components/HardwareSetRow";
import PageHeader from "../components/PageHeader";
import { getSignedInUserId } from "../session";

// Full page for one project, reached from /projects/:projectId.
// Issue #7: members see the project's info.
// Issue #9: members can leave the project from here.
// Issues #18-#24: members check hardware out and back in from here.
function ProjectPage() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  // RequireSignIn only lets signed-in users reach this page.
  const userId = getSignedInUserId();

  const [project, setProject] = useState(null);
  const [hardwareSets, setHardwareSets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [hardwareError, setHardwareError] = useState("");
  // Members list starts closed; clicking "Members (n)" opens it.
  const [membersOpen, setMembersOpen] = useState(false);
  const [leaving, setLeaving] = useState(false);
  const [leaveError, setLeaveError] = useState("");

  useEffect(() => {
    // Ignore a slow response if the user has already moved to another project.
    let active = true;
    setLoading(true);
    setError("");
    setHardwareError("");

    // Load the project and the hardware list at the same time. A hardware
    // failure still lets the rest of the page show.
    Promise.allSettled([fetchProject(projectId), fetchHardwareSets()])
      .then(([projectResult, hardwareResult]) => {
        if (!active) return;

        if (projectResult.status === "fulfilled") {
          setProject(projectResult.value);
        } else {
          setProject(null);
          setError(projectResult.reason.message);
        }

        if (hardwareResult.status === "fulfilled") {
          setHardwareSets(hardwareResult.value);
        } else {
          setHardwareError(hardwareResult.reason.message);
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [projectId]);

  // Called by each HardwareSetRow. A positive change checks out, a negative
  // change checks in. If the server says no, the error is thrown back to the
  // row, which shows it instead of a success message.
  const updateHardware = async (rowProjectId, hardwareName, quantityChange) => {
    const result = quantityChange > 0
      ? await checkoutHardware(rowProjectId, hardwareName, quantityChange)
      : await checkinHardware(rowProjectId, hardwareName, -quantityChange);

    // Use the server's numbers so the page matches the database.
    if (result.project) setProject(result.project);
    if (result.hardware) {
      setHardwareSets((sets) => sets.map((set) => (
        set.name === result.hardware.name ? result.hardware : set
      )));
    }
  };

  const handleLeave = async () => {
    const confirmed = window.confirm(
      `Leave ${project.projectName}? You can rejoin later with the project ID.`
    );
    if (!confirmed) return;

    setLeaving(true);
    setLeaveError("");
    try {
      await leaveProject({ projectId: project.projectId, userId });
      // The dashboard reloads the list, so the project is gone from it.
      navigate("/dashboard");
    } catch (requestError) {
      setLeaveError(requestError.message);
      setLeaving(false);
    }
  };

  const isMember = Boolean(project && userId && project.users.includes(userId));
  // Hardware this project has checked out, keyed by hardware set name.
  const checkedOut = project?.hwSets || {};

  return (
    <section className="checkout-page">
      {/* Only members see the real name and ID; everyone else sees "Project". */}
      <PageHeader
        title={isMember ? project.projectName : "Project"}
        subtitle={isMember ? `Project ID: ${project.projectId}` : null}
      />

      <div className="checkout-content">
        {loading && <p className="loading-message">Loading project...</p>}
        {error && <p className="error-banner" role="alert">{error}</p>}

        {/* Only members get to see a project's details. */}
        {project && !loading && !isMember && (
          <p className="empty-state">
            You are not a member of this project.{" "}
            <Link to="/projects/join">Join a project</Link> to see its details.
          </p>
        )}

        {isMember && !loading && (
          // Two columns: description and hardware on the left, members on the right.
          <div className="project-page-layout">
            <div className="project-page-main">
              <div>
                <h2>Description</h2>
                <p>{project.description || "No description yet."}</p>
              </div>

              <div>
                <h2>Hardware</h2>
                {hardwareError && (
                  <p className="error-banner" role="alert">{hardwareError}</p>
                )}
                {!hardwareError && hardwareSets.length === 0 && (
                  <p className="empty-state">No hardware sets are available yet.</p>
                )}
                {hardwareSets.length > 0 && (
                  <div className="project-hardware-list" aria-label="Hardware">
                    {hardwareSets.map((hardware) => (
                      <div className="project-hardware-item" key={hardware.name}>
                        <HardwareSetRow
                          hardware={hardware}
                          checkedOut={checkedOut[hardware.name] || 0}
                          projectId={project.projectId}
                          onUpdateHardware={updateHardware}
                        />
                        <p className="project-hardware-held">
                          Checked out by this project: {checkedOut[hardware.name] || 0}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <aside className="project-members">
              {/* Leave sits above the members list so it is easy to find. */}
              <div className="leave-project">
                <Button
                  className="button-danger"
                  onClick={handleLeave}
                  disabled={leaving}
                >
                  {leaving ? "Leaving..." : "Leave Project"}
                </Button>
                {leaveError && (
                  <p className="error-banner" role="alert">{leaveError}</p>
                )}
              </div>
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
                  {project.users.map((memberId) => (
                    <li key={memberId}>{memberId}</li>
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