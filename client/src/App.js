import React from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import './App.css';
import { AuthProvider } from './context/AuthContext';
import RequireAuth from './components/RequireAuth';
import MyLoginPage from './pages/MyLoginPage';
import MyUserPortal from './pages/MyUserPortal';
import ProjectPage from './pages/ProjectPage';
import NotFound from './pages/NotFound';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/projects" replace />} />
          <Route path="/login" element={<MyLoginPage />} />
          <Route path="/projects" element={<RequireAuth><MyUserPortal /></RequireAuth>} />
          <Route path="/projects/:projectId" element={<RequireAuth><ProjectPage /></RequireAuth>} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
