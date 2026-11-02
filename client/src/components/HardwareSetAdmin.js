import { useState } from 'react';
import { renameHardwareSet, setHardwareSetActive } from '../api/hardware.js';

/**
 * HardwareSetAdmin holds the per-card management controls: rename,
 * deactivate and reactivate. It never applies a response to local state;
 * the only path to new values is the `onChanged` reload from the server.
 *
 * Data source: mutates via client/src/api/hardware.js
 *
 * @component
 * @param {Object} props
 * @param {string} props.projectId - The project the set belongs to.
 * @param {string} props.userId - The acting member's id.
 * @param {Object} props.hwSet - `{ hwSetName, active }`. The set counts as
 *   inactive only when `active === false`, so a missing value reads active.
 * @param {Function} props.onChanged - Async reload callback, awaited after
 *   every successful change.
 */
export default function HardwareSetAdmin({ projectId, userId, hwSet, onChanged }) {
  const [renaming, setRenaming] = useState(false);
  const [newName, setNewName] = useState('');
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const inactive = hwSet.active === false;

  function openRename() {
    setNewName(hwSet.hwSetName);
    setError(null);
    setRenaming(true);
  }

  function closeRename() {
    setRenaming(false);
    setError(null);
  }

  async function handleRename(event) {
    event.preventDefault();
    setError(null);
    setBusy('rename');
    try {
      await renameHardwareSet({ projectId, userId, hwSetName: hwSet.hwSetName, newName });
      setRenaming(false);
      await onChanged();
    } catch (renameError) {
      setError(describeAdminError(renameError));
    } finally {
      setBusy(false);
    }
  }

  async function handleToggleActive() {
    setError(null);
    setBusy('active');
    try {
      await setHardwareSetActive({
        projectId,
        userId,
        hwSetName: hwSet.hwSetName,
        active: inactive,
      });
      await onChanged();
    } catch (activeError) {
      setError(describeAdminError(activeError));
    } finally {
      setBusy(false);
    }
  }

  const toggleLabel = inactive ? 'Reactivate' : 'Deactivate';
  const toggleBusyLabel = inactive ? 'Reactivating...' : 'Deactivating...';

  return (
    <div className="hw-set__admin">
      <button type="button" onClick={openRename}>
        Rename
      </button>
      <button type="button" onClick={handleToggleActive} disabled={Boolean(busy)}>
        {busy === 'active' ? toggleBusyLabel : toggleLabel}
      </button>

      {renaming && (
        <form onSubmit={handleRename}>
          <label>
            New name
            <input
              type="text"
              value={newName}
              onChange={(event) => setNewName(event.target.value)}
              required
            />
          </label>
          <button type="submit" disabled={Boolean(busy)}>
            {busy === 'rename' ? 'Saving...' : 'Save name'}
          </button>
          <button type="button" onClick={closeRename}>
            Cancel
          </button>
        </form>
      )}

      {error && (
        <p className="error-text hw-action__error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

// Translates the rename / set_active error shapes into copy a member can
// act on.
function describeAdminError(error) {
  if (error.message === 'hardware_set_name_taken') {
    return 'Another hardware set in this project already uses that name.';
  }
  if (error.message === 'hardware_set_in_use') {
    return `Can't deactivate -- ${error.checkedOut} still checked out.`;
  }
  if (error.field === 'newName') {
    return 'Name is required.';
  }
  return error.message;
}
