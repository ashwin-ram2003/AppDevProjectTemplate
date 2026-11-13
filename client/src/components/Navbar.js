// Top bar shown on logged-in pages.
// Shows the app title, links to the Projects and Create / Join pages, the signed-in
// userId and a Logout button (calls signOut, then navigates to /login).
// The project checkout page isn't in the nav; it's reached from a project card, and
// the Projects tab stays highlighted there since it lives under /projects.
import React from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const navLinkClass = ({ isActive }) => (isActive ? 'nav-link active' : 'nav-link');

export default function Navbar() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    try {
      await signOut();
    } catch {
      // Local auth state is cleared even when the server is unreachable.
    }
    navigate('/login', { replace: true });
  }

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <Link to="/projects" className="brand">HaaS</Link>
        <nav className="nav-links" aria-label="Main">
          <NavLink to="/projects" className={navLinkClass}>Projects</NavLink>
          <NavLink to="/create-join" className={navLinkClass}>Create / Join</NavLink>
        </nav>
        <div className="nav-user">
          {user && (
            <span>
              Signed in as <strong>{user.userId}</strong>
            </span>
          )}
          <button type="button" className="secondary" onClick={handleLogout}>Log out</button>
        </div>
      </div>
    </header>
  );
}
