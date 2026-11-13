import React from 'react';

// Below this share of capacity a set counts as running low and its meter turns orange
const LOW_STOCK = 0.2;

// Thin bar showing how much of a set is still available
export function StockMeter({ availability, capacity }) {
  const share = capacity ? availability / capacity : 0;
  const pct = Math.round(share * 100);
  return (
    <div className={share < LOW_STOCK ? 'meter low' : 'meter'} role="img" aria-label={`${pct}% available`}>
      <span style={{ width: `${pct}%` }} />
    </div>
  );
}

// Compact list of hardware sets: name, available / capacity, and a stock meter.
export default function HardwareSetList({ sets }) {
  if (sets.length === 0) return <p className="muted">No hardware sets yet.</p>;
  return (
    <ul className="stock-list">
      {sets.map((s) => (
        <li key={s.hwName}>
          <div className="stock-row">
            <span>{s.hwName}</span>
            <span className="stock-count">
              <strong>{s.availability}</strong> <span className="muted">/ {s.capacity}</span>
            </span>
          </div>
          <StockMeter availability={s.availability} capacity={s.capacity} />
        </li>
      ))}
    </ul>
  );
}
