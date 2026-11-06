import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import Checkout from "./components/Checkout";
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
          <Route path="/dashboard" element={<HomePage />} />
          <Route path="/hardware" element={<Checkout />} />
          <Route path="/projects/new" element={<CreateProjectPage />} />
          <Route path="/projects/join" element={<JoinProjectPage />} />
          <Route path="/projects/:projectId" element={<ProjectPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
          <Route path="/create-account" element={<CreateAccountPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;
