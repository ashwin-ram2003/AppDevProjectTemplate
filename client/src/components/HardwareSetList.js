import React from 'react';

// Reusable display of hardware sets: name, capacity, availability.
export default function HardwareSetList({ sets }) {
  if (sets.length === 0) return <p className="muted">No hardware sets yet.</p>;
  return (
    <table>
      <thead>
        <tr><th>Name</th><th>Capacity</th><th>Available</th></tr>
      </thead>
      <tbody>
        {sets.map((s) => (
          <tr key={s.hwName}>
            <td>{s.hwName}</td><td>{s.capacity}</td><td>{s.availability}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
