import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import MyLoginPage from './pages/MyLoginPage';
import MyRegistrationPage from './pages/MyRegistrationPage';
import ForgotMyPassword from './pages/ForgotMyPassword';
import MyUserPortal from './pages/MyUserPortal';
import './App.css';

function App() {
  return (
    <div className="app-container">
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<MyLoginPage />} />
          <Route path="/register" element={<MyRegistrationPage />} />
          <Route path="/forgot-password" element={<ForgotMyPassword />} />
          <Route path="/portal" element={<MyUserPortal />} />
        </Routes>
      </main>
      <footer className="footer">
        <p>&copy; {new Date().getFullYear()} MakerHub - The University of Texas at Austin</p>
      </footer>
    </div>
  );
}

export default App;

