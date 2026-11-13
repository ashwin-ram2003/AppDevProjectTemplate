// Fallback route "*".
import React from 'react';
import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <main className="container narrow">
      <h1>Page not found</h1>
      <p><Link to="/projects">Back to projects</Link></p>
    </main>
  );
}
