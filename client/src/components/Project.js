import { useCallback, useEffect, useState } from 'react';
import { fetchHardware } from '../api/hardware.js';
import HardwareActions from './Checkout.js';
import CheckinForm from './CheckinForm.js';
import Modal from './Modal.js';

/**
 * HardwareTable renders one row per hardware set in the project, matching
 * the assignment's Figure 3 Resource Management mockup: a flat list showing
 * each set's name, capacity, and availability -- a hardware set is just a
 * named, countable resource, with no other dimension to it.
 *
 * Data source: props only
 * No hard-coded fallback: this component renders nothing it was not given or told.
 *
 * @component
 * @param {Object} props
 * @param {Array} props.hardwareSets - The project's hardware sets, each
 *   `{ hwSetName, capacity, available }`, in the order received.
 * @param {Function} props.onRowClick - Called with the clicked hardware set
 *   when a project member wants to check it out, request it, or check it in.
 */
function HardwareTable({ hardwareSets, onRowClick }) {
  return (
    <div className="hardware-table-wrap">
      <table className="hardware-table">
        <thead>
          <tr>
            <th>Hardware Set</th>
            <th>Capacity</th>
            <th>Available</th>
          </tr>
        </thead>
        <tbody>
          {hardwareSets.map((hwSet) => (
            <tr
              key={hwSet.hwSetName}
              className="hardware-table__row"
              onClick={() => onRowClick(hwSet)}
            >
              <td>
                <button type="button" className="hardware-table__open" aria-haspopup="dialog">
                  {hwSet.hwSetName}
                </button>
              </td>
              <td className="hardware-table__num">{hwSet.capacity}</td>
              <td className="hardware-table__num">{hwSet.available}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/**
 * ResourceView is the top-level presentational component for a project's
 * hardware resources. It fetches its own data through
 * client/src/api/hardware.js, but accepts session identity as props rather
 * than reading it from any global auth state -- Track A's session/auth layer
 * wires real values in here once it lands.
 *
 * Data source: fetches via client/src/api/hardware.js
 * No hard-coded fallback: this component renders nothing it was not given or told.
 *
 * @component
 * @param {Object} props
 * @param {string} props.projectId - The project whose hardware sets to load.
 *   No fallback/default; a real session must supply this.
 * @param {string} props.userId - The acting user's id, used for request/
 *   checkout/release calls. No fallback/default.
 * @param {string} props.userName - Display name shown on request entries
 *   this user creates. No fallback/default.
 */
export default function ResourceView({ projectId, userId, userName }) {
  const [hardware, setHardware] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openModal, setOpenModal] = useState(null);

  const loadHardware = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchHardware(projectId, userId);
      setHardware(data);
    } catch (fetchError) {
      setError(fetchError.message);
    } finally {
      setLoading(false);
    }
  }, [projectId, userId]);

  useEffect(() => {
    loadHardware();
  }, [loadHardware]);

  const handleCheckedIn = useCallback(async () => {
    await loadHardware();
  }, [loadHardware]);

  if (loading) {
    return <p>Loading hardware resources...</p>;
  }

  if (error) {
    return (
      <div>
        <p className="error-text">{error}</p>
        <button type="button" onClick={loadHardware}>
          Retry
        </button>
      </div>
    );
  }

  const hardwareSets = hardware ? hardware.hardwareSets : [];

  return (
    <div>
      <HardwareTable
        hardwareSets={hardwareSets}
        onRowClick={(hwSet) => setOpenModal({ kind: 'detail', hwSet })}
      />
      <CheckinForm projectId={projectId} userId={userId} onCheckedIn={handleCheckedIn} />
      {openModal && openModal.kind === 'detail' && (
        <Modal title={openModal.hwSet.hwSetName} onClose={() => setOpenModal(null)}>
          <p className="hw-detail__summary">
            Capacity {openModal.hwSet.capacity} &middot; Available {openModal.hwSet.available}
          </p>
          <HardwareActions
            projectId={projectId}
            hwSet={openModal.hwSet}
            userId={userId}
            userName={userName}
            onChanged={loadHardware}
          />
        </Modal>
      )}
    </div>
  );
}
