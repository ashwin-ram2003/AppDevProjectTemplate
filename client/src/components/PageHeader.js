import { Link } from "react-router-dom";

// Shared top bar for app pages: title (and optional subtitle) on the left,
// actions on the right. Most pages just want a way back to the dashboard,
// so that is the default action.
//
//   <PageHeader title="Create Project" />
//   <PageHeader title={name} subtitle={`Project ID: ${id}`} />
//   <PageHeader title="My Dashboard" actions={<SignOutArea />} />
function PageHeader({ title, subtitle, actions }) {
  return (
    <header className="page-header">
      {subtitle ? (
        // Same markup ProjectPage used, so the existing CSS keeps the
        // subtitle tucked right under the title.
        <div className="project-heading">
          <h1 className="page-title">{title}</h1>
          <p className="project-id-line">{subtitle}</p>
        </div>
      ) : (
        <h1 className="page-title">{title}</h1>
      )}
      {actions ?? (
        <Link className="page-header-link" to="/dashboard">
          Back to Dashboard
        </Link>
      )}
    </header>
  );
}

export default PageHeader;
