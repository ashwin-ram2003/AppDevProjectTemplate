import HardwareSetRow from "./HardwareSetRow";
import Button from "./Button";

function ProjectCard({
  project,
  hardware,
  canManage = true,
  onJoin,
  onUpdateHardware,
}) {
  const { projectName, projectId, description, users, hwSets } = project;
  const memberLabel = users.length === 1 ? "member" : "members";

  return (
    <li className="project-card">
      <div className="project-card-header">
        <h3>{projectName}</h3>
        {!canManage && (
          <Button variant="primary" onClick={() => onJoin(projectId)}>Join</Button>
        )}
      </div>

      <p className="project-meta">
        Project ID: {projectId} · {users.length} {memberLabel}
      </p>

      <div className="project-snippet">
        <p>{description || "No description yet."}</p>
        <p>
          <strong>Members:</strong> {users.join(", ")}
        </p>
        <div className="project-hardware-list">
          {hardware.map((item) => (
            <HardwareSetRow
              key={item.name}
              hardware={item}
              checkedOut={hwSets?.[item.name] || 0}
              projectId={projectId}
              disabled={!canManage}
              onUpdateHardware={onUpdateHardware}
            />
          ))}
        </div>
      </div>
    </li>
  );
}

export default ProjectCard;
