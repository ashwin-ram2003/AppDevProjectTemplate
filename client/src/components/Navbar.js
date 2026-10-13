import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Wrench, Moon, Sun } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();
  const isAuthPage = ['/login', '/register', '/forgot-password'].includes(location.pathname);
  
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        <Wrench size={24} color="#BF5700" />
        <div>Maker<span>Hub</span></div>
      </Link>
      
      <div className="navbar-nav">
        <button onClick={toggleTheme} className="btn btn-secondary" style={{ padding: '0.4rem', borderRadius: '50%' }} aria-label="Toggle Theme">
          {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
        </button>

        {!isAuthPage && (
          <>
            <Link to="/portal" className="nav-link">My Projects</Link>
            <Link to="/login" className="btn btn-secondary" style={{ padding: '0.4rem 1rem' }}>Sign Out</Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;

