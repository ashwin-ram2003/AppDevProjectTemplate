import ResourceView from './components/Project.js';
import './App.css';

// Track A's session/auth layer (ACCT-04) has not landed yet, so there is no
// login flow to source projectId/userId/userName from. These are
// placeholder identifiers for this tracer slice only. Track A wires real
// session values in here once ACCT-04 lands.
const PROJECT_ID = 'P1';
const USER_ID = 'alice';
const USER_NAME = 'Alice';

export default function App() {
  return (
    <div className="app-container">
      <h1 className="app-heading">Project {PROJECT_ID} — Hardware Resources</h1>
      <ResourceView projectId={PROJECT_ID} userId={USER_ID} userName={USER_NAME} />
    </div>
  );
}
