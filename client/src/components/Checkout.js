// Resource Management panel (Figure 3 of the spec).
// Loads hardware sets

import React, { useCallback, useEffect, useState } from 'react';
import { checkIn, checkOut, getAllHardwareSets } from '../api/hardware';
import { getProject } from '../api/projects';

const POLL_MS = 5000;
const WHOLE_NUMBER = /^[1-9]\d*$/;

const numStyle = { textAlign: 'right' };
const qtyInputStyle = {
  width: 70,
  padding: 6,
  border: '1px solid #c4ccd4',
  borderRadius: 4,
};
const actionsStyle = { display: 'flex', gap: 8, flexWrap: 'wrap' };

export default function Checkout({ projectId, userId }) {
  const [sets, setSets] = useState([]);
  const [project, setProject] = useState(null);
  const [requests, setRequests] = useState({});
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState(null); // { ok: boolean, text: string }

  // Fetch the latest hardware numbers and this project's checked-out counts together
  const refresh = useCallback(async () => {
    const [nextSets, nextProject] = await Promise.all([getAllHardwareSets(), getProject(projectId)]);
    setSets(nextSets);
    setProject(nextProject);
  }, [projectId]);

  // Initial load, then poll so changes made by other users show up
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    refresh()
      .catch((err) => { if (!cancelled) setStatus({ ok: false, text: err.message }); })
      .finally(() => { if (!cancelled) setLoading(false); });

    const timer = setInterval(() => {
      refresh().catch(() => { /* keep showing the last good numbers */ });
    }, POLL_MS);

    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [refresh]);

  function setRequest(hwName, value) {
    setRequests((prev) => ({ ...prev, [hwName]: value }));
  }

  // Shared handler: action is checkOut or checkIn from api/hardware
  async function handle(action, hwName) {
    const raw = (requests[hwName] || '').trim();
    if (!WHOLE_NUMBER.test(raw)) {
      setStatus({ ok: false, text: `Enter a positive whole number of units for ${hwName}.` });
      return;
    }

    setBusy(true);
    setStatus(null);
    try {
      const { message } = await action(projectId, hwName, userId, Number(raw));
      setStatus({ ok: true, text: message });
      setRequest(hwName, '');
    } catch (err) {
      // e.g. "Request exceeds available units of HWSet1"
      setStatus({ ok: false, text: err.message });
    } finally {
      // Refresh either way so the table shows the real numbers
      try { await refresh(); } catch { /* status already shows the error */ }
      setBusy(false);
    }
  }

  if (loading) {
    return <section className="card"><p className="muted">Loading hardware...</p></section>;
  }

  // How many units of each set this project holds, e.g. { HWSet1: 5 }
  const usage = project?.hwSets || {};

  return (
    <section className="card">
      <h2>Resource management</h2>

      {sets.length === 0 ? (
        <p className="muted">
          No hardware sets exist yet. Add one from the Hardware sets panel on the My projects page.
        </p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th scope="col">Set</th>
                <th scope="col" style={numStyle}>Capacity</th>
                <th scope="col" style={numStyle}>Available</th>
                <th scope="col" style={numStyle}>Checked out</th>
                <th scope="col">Request</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              {sets.map((set) => {
                const checkedOut = usage[set.hwName] || 0;
                const inputId = `request-${set.hwName}`;
                return (
                  <tr key={set.hwName}>
                    <th scope="row">{set.hwName}</th>
                    <td style={numStyle}>{set.capacity}</td>
                    <td style={numStyle}>{set.availability}</td>
                    <td style={numStyle}>{checkedOut}</td>
                    <td>
                      <label htmlFor={inputId} style={{ position: 'absolute', left: -9999 }}>
                        Units of {set.hwName}
                      </label>
                      <input
                        id={inputId}
                        style={qtyInputStyle}
                        inputMode="numeric"
                        placeholder="0"
                        value={requests[set.hwName] || ''}
                        onChange={(e) => setRequest(set.hwName, e.target.value)}
                        disabled={busy}
                      />
                    </td>
                    <td>
                      <div style={actionsStyle}>
                        <button type="button" onClick={() => handle(checkOut, set.hwName)} disabled={busy}>
                          Check out
                        </button>
                        <button
                          type="button"
                          onClick={() => handle(checkIn, set.hwName)}
                          disabled={busy || checkedOut === 0}
                        >
                          Check in
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {status && <p className={status.ok ? 'msg ok' : 'msg err'} role="status">{status.text}</p>}
      <p className="muted">"Checked out" is what this project holds. Numbers refresh every few seconds.</p>
    </section>
  );
}