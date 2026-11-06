import { Link } from "react-router-dom";

// One project on the dashboard. Clicking the card opens or closes a short
// snippet; clicking the project name goes to the full project page.
function ProjectCard({ project, expanded, onToggle }) {
  const { projectName, projectId, description, users, hwSets } = project;
  const detailsId = `project-details-${projectId}`;
  const hardware = Object.entries(hwSets || {});
  const memberLabel = users.length === 1 ? "member" : "members";

  return (
    <li
      className={`project-card${expanded ? " project-card-open" : ""}`}
      onClick={onToggle}
    >
      <div className="project-card-header">
        <h3>
          {/* stopPropagation: the name navigates instead of toggling */}
          <Link
            to={`/projects/${encodeURIComponent(projectId)}`}
            onClick={(event) => event.stopPropagation()}
          >
            {projectName}
          </Link>
        </h3>

        {/* Keyboard and screen-reader way to open the snippet. */}
        <button
          type="button"
          className="project-toggle"
          aria-expanded={expanded}
          aria-controls={detailsId}
          aria-label={`${expanded ? "Hide" : "Show"} details for ${projectName}`}
          onClick={(event) => {
            event.stopPropagation();
            onToggle();
          }}
        >
          {expanded ? "▾" : "▸"}
        </button>
      </div>

      <p className="project-meta">
        Project ID: {projectId} · {users.length} {memberLabel}
      </p>

      {expanded && (
        <div className="project-snippet" id={detailsId}>
          <p>{description || "No description yet."}</p>
          <p>
            <strong>Members:</strong> {users.join(", ")}
          </p>
          <p>
            <strong>Hardware:</strong>{" "}
            {hardware.length === 0
              ? "None checked out"
              : hardware.map(([name, qty]) => `${name} (${qty})`).join(", ")}
          </p>
          <Link
            className="project-open-link"
            to={`/projects/${encodeURIComponent(projectId)}`}
            onClick={(event) => event.stopPropagation()}
          >
            Open project →
          </Link>
        </div>
      )}
    </li>
  );
}

export default ProjectCard;
