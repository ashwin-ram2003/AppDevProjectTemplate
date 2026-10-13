import React from 'react';
import { Folder } from 'lucide-react';

const Project = ({ project }) => {
  return (
    <div className="card" style={{ transition: 'transform 0.2s', height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
        <Folder color="var(--ut-burnt-orange)" size={28} />
        <h3 style={{ margin: 0 }}>{project.name}</h3>
      </div>
      <p style={{ color: 'var(--ut-charcoal)', fontSize: '0.9rem', marginBottom: '1rem' }}>
        {project.description}
      </p>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto' }}>
        <span style={{ fontSize: '0.8rem', backgroundColor: 'var(--ut-light-gray)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
          ID: {project.projectId}
        </span>
        <span style={{ color: 'var(--ut-burnt-orange)', fontSize: '0.9rem', fontWeight: 500 }}>
          Manage Hardware &rarr;
        </span>
      </div>
    </div>
  );
};

export default Project;

