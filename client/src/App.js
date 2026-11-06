import React from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import './App.css';
import { AuthProvider } from './context/AuthContext';
import AppLayout from './components/AppLayout';
import RequireAuth from './components/RequireAuth';
import MyLoginPage from './pages/MyLoginPage';
import MyUserPortal from './pages/MyUserPortal';
import CreateJoinPage from './pages/CreateJoinPage';
import ProjectPage from './pages/ProjectPage';
import NotFound from './pages/NotFound';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/projects" replace />} />
          <Route path="/login" element={<MyLoginPage />} />
          {/* Signed-in pages share the nav bar through AppLayout */}
          <Route element={<RequireAuth><AppLayout /></RequireAuth>}>
            <Route path="/projects" element={<MyUserPortal />} />
            <Route path="/create-join" element={<CreateJoinPage />} />
            <Route path="/projects/:projectId" element={<ProjectPage />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
