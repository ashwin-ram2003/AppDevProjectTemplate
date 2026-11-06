import { useState } from "react";
import { Link } from "react-router-dom";

import { joinProject } from "../api/projectsApi";
import Button from "../components/Button";

const EMPTY_FORM = { projectId: "", userId: "" };

function JoinProjectPage() {
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [joinedProject, setJoinedProject] = useState(null);

  const updateField = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setJoinedProject(null);

    const projectId = form.projectId.trim();
    const userId = form.userId.trim();
    if (!projectId || !userId) {
      setError("Project ID and user ID are required.");
      return;
    }

    setSubmitting(true);
    try {
      const project = await joinProject({ projectId, userId });
      setJoinedProject(project);
      setForm(EMPTY_FORM);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="checkout-page">
      <header className="page-header">
        <h1 className="page-title">Join Project</h1>
        <Link className="page-header-link" to="/dashboard">Back to Dashboard</Link>
      </header>

      <div className="checkout-content">
        <form className="project-form" onSubmit={handleSubmit}>
          <div className="field-row">
            <label htmlFor="join-project-id">Project ID</label>
            <input
              id="join-project-id"
              name="projectId"
              type="text"
              maxLength={32}
              placeholder="Project ID shared by a teammate"
              value={form.projectId}
              onChange={updateField}
            />
          </div>

          {/* TODO: remove this field and use the signed-in user's ID once
              Sign In (#2) is done. */}
          <div className="field-row">
            <label htmlFor="join-user-id">User ID</label>
            <input
              id="join-user-id"
              name="userId"
              type="text"
              placeholder="Your user ID"
              value={form.userId}
              onChange={updateField}
            />
          </div>

          <Button type="submit" variant="primary" disabled={submitting}>
            {submitting ? "Joining..." : "Join Project"}
          </Button>

          {error && <p className="error-banner" role="alert">{error}</p>}
          {joinedProject && (
            <p className="request-message" role="status">
              Joined "{joinedProject.projectName}" (Project ID: {joinedProject.projectId}).
            </p>
          )}
        </form>
      </div>
    </section>
  );
}

export default JoinProjectPage;