import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import RequireSignIn from "./components/RequireSignIn";

import HomePage from "./pages/HomePage";
import CreateAccountPage from "./pages/CreateAccountPage";
import CreateProjectPage from "./pages/CreateProjectPage";
import JoinProjectPage from "./pages/JoinProjectPage";
import ProjectPage from "./pages/ProjectPage";
import "./App.css";
import LoginPage from "./pages/LoginPage";

function App() {
  return (
    <BrowserRouter>
      <main className="app-shell">
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route
            path="/dashboard"
            element={
              <RequireSignIn>
                <HomePage />
              </RequireSignIn>
            }
          />
          <Route
            path="/projects/new"
            element={
              <RequireSignIn>
                <CreateProjectPage />
              </RequireSignIn>
            }
          />
          <Route
            path="/projects/join"
            element={
              <RequireSignIn>
                <JoinProjectPage />
              </RequireSignIn>
            }
          />
          <Route
            path="/projects/:projectId"
            element={
              <RequireSignIn>
                <ProjectPage />
              </RequireSignIn>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
          <Route path="/create-account" element={<CreateAccountPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;