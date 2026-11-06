// Route /create-join. The create new project / use existing project forms.
// Once a project is created or joined, the user is taken to its checkout page.
import React from 'react';
import { useNavigate } from 'react-router-dom';
import Project from '../components/Project';
import { useAuth } from '../context/AuthContext';

export default function CreateJoinPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <>
      <h1>Create or join a project</h1>

      <Project
        userId={user.userId}
        onSelect={(project) => navigate(`/projects/${encodeURIComponent(project.projectId)}`)}
      />
    </>
  );
}
