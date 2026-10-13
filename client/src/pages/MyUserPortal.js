import React, { useState } from 'react';
import Project from '../components/Project';
import Checkout from '../components/Checkout';

const MyUserPortal = () => {
  const [activeProject, setActiveProject] = useState(null);

  // Mock data for initial render
  const mockProjects = [
    { projectId: 'P001', name: 'Embedded Systems Final', description: 'Arduino-based weather station.' },
    { projectId: 'P002', name: 'IoT Research', description: 'Raspberry Pi smart home hub.' }
  ];

  return (
    <div>
      <div className="portal-header">
        <div>
          <h1 style={{color: 'var(--ut-burnt-orange)'}}>My Workspace</h1>
          <p>Manage your projects and request hardware from the UT Austin Makerspace.</p>
        </div>
        <button className="btn btn-primary">+ Create New Project</button>
      </div>
      
      {activeProject ? (
        <div>
          <button className="btn btn-secondary" style={{marginBottom: '1rem'}} onClick={() => setActiveProject(null)}>
            &larr; Back to Projects
          </button>
          <Checkout project={activeProject} />
        </div>
      ) : (
        <div className="dashboard-grid">
          {mockProjects.map(proj => (
            <div key={proj.projectId} onClick={() => setActiveProject(proj)} style={{cursor: 'pointer'}}>
              <Project project={proj} />
            </div>
          ))}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', borderStyle: 'dashed', borderWidth: '2px', borderColor: 'var(--ut-dark-gray)', cursor: 'pointer', background: 'transparent', boxShadow: 'none' }}>
            <h3 style={{ color: 'var(--ut-charcoal)', opacity: 0.7 }}>Join Existing Project</h3>
            <p style={{ opacity: 0.6 }}>Enter a project ID to collaborate</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default MyUserPortal;

