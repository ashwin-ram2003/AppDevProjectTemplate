import React, { useState } from 'react';
import { Cpu, Server, CheckCircle, XCircle } from 'lucide-react';

const Checkout = ({ project }) => {
  // Mock data representing hardware sets
  const [hardwareSets, setHardwareSets] = useState([
    { id: 'HWSet1', name: 'Arduino Kits', capacity: 100, available: 45, checkedOutByProject: 5 },
    { id: 'HWSet2', name: 'Raspberry Pi Kits', capacity: 50, available: 12, checkedOutByProject: 2 }
  ]);

  const [requestQtys, setRequestQtys] = useState({ HWSet1: 0, HWSet2: 0 });

  const handleQtyChange = (id, val) => {
    setRequestQtys(prev => ({ ...prev, [id]: parseInt(val) || 0 }));
  };

  const handleAction = (id, action) => {
    const qty = requestQtys[id];
    if (qty <= 0) return;
    
    // Here we'd call the /check_out or /check_in Flask API.
    // For UI demonstration, we just show an alert.
    alert(`Successfully ${action === 'checkout' ? 'checked out' : 'checked in'} ${qty} units of ${id} for project ${project.name}`);
    setRequestQtys(prev => ({ ...prev, [id]: 0 }));
  };

  return (
    <div className="card">
      <div style={{ borderBottom: '2px solid var(--ut-light-gray)', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
        <h2 style={{ color: 'var(--ut-burnt-orange)' }}>{project.name}</h2>
        <p style={{ margin: 0 }}>Project ID: {project.projectId}</p>
      </div>

      <h3>Hardware Resources</h3>
      <div className="dashboard-grid" style={{ marginTop: '1rem' }}>
        {hardwareSets.map((hw) => (
          <div key={hw.id} style={{ border: '1px solid var(--ut-dark-gray)', borderRadius: '8px', padding: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
              {hw.id === 'HWSet1' ? <Cpu size={24} color="var(--ut-charcoal)" /> : <Server size={24} color="var(--ut-charcoal)" />}
              <h4 style={{ margin: 0 }}>{hw.name}</h4>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
              <span>Capacity: {hw.capacity}</span>
              <span style={{ fontWeight: 600, color: hw.available > 0 ? 'var(--success-green)' : 'var(--error-red)' }}>
                Available: {hw.available}
              </span>
            </div>
            <div style={{ marginBottom: '1.5rem', fontSize: '0.9rem', color: 'var(--ut-burnt-orange)', fontWeight: 600 }}>
              Currently Checked Out: {hw.checkedOutByProject}
            </div>

            <div className="form-group" style={{ marginBottom: '1rem' }}>
              <label className="form-label">Quantity</label>
              <input 
                type="number" 
                min="1" 
                className="form-control"
                value={requestQtys[hw.id] || ''}
                onChange={(e) => handleQtyChange(hw.id, e.target.value)}
                placeholder="Enter amount"
              />
            </div>

            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button 
                className="btn btn-primary" 
                style={{ flex: 1, display: 'flex', gap: '0.25rem', padding: '0.5rem' }}
                onClick={() => handleAction(hw.id, 'checkout')}
              >
                <CheckCircle size={16} /> Check Out
              </button>
              <button 
                className="btn btn-secondary" 
                style={{ flex: 1, display: 'flex', gap: '0.25rem', padding: '0.5rem' }}
                onClick={() => handleAction(hw.id, 'checkin')}
              >
                <XCircle size={16} /> Check In
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Checkout;

