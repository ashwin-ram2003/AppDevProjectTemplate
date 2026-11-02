import { useState } from 'react';
import { createHardwareSet } from '../api/hardware.js';

/**
 * CreateHardwareSet lets a project member add a brand-new hardware set
 * (a name plus a fixed starting capacity) to the project. Without this,
 * a project has no way to ever get its first hardware set -- checkin/
 * checkout only operate on sets that already exist.
 *
 * Data source: mutates via client/src/api/hardware.js
 *
 * @component
 * @param {Object} props
 * @param {string} props.projectId - The project to create the set in.
 * @param {string} props.userId - The acting member's id.
 * @param {Function} props.onCreated - Async reload callback, awaited
 *   after a successful create.
 */
export default function CreateHardwareSet({ projectId, userId, onCreated }) {
  const [hwSetName, setHwSetName] = useState('');
  const [capacity, setCapacity] = useState('');
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await createHardwareSet({ projectId, userId, hwSetName, capacity: Number(capacity) });
      setHwSetName('');
      setCapacity('');
      await onCreated();
    } catch (createError) {
      setError(describeCreateError(createError));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="auth-form create-hw-set" onSubmit={handleSubmit}>
      <h3>Add a hardware set</h3>

      <label className="auth-form__field">
        Name
        <input
          type="text"
          value={hwSetName}
          onChange={(event) => setHwSetName(event.target.value)}
          required
        />
      </label>

      <label className="auth-form__field">
        Starting capacity
        <input
          type="number"
          min="1"
          step="1"
          value={capacity}
          onChange={(event) => setCapacity(event.target.value)}
          required
        />
      </label>

      <button type="submit" disabled={submitting}>
        {submitting ? 'Adding...' : 'Add hardware set'}
      </button>

      {error && (
        <p role="alert" className="error-text auth-form__message">
          {error}
        </p>
      )}
    </form>
  );
}

// Translates /api/hardware/create's error shapes into copy a user
// filling out this form can act on.
function describeCreateError(error) {
  if (error.field === 'capacity') {
    return 'Starting capacity must be a whole number of 1 or more.';
  }
  if (error.field === 'hwSetName') {
    return 'Name is required.';
  }
  return error.message;
}
