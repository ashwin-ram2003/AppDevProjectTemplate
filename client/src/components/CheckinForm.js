import { useState } from 'react';
import { checkinHardware } from '../api/hardware.js';

/**
 * CheckinForm renders the form a project member uses to check units of a
 * hardware set into the project, creating the hardware set if it does not
 * already exist. Matches the assignment's Figure 3 mockup: a hardware-set
 * name and a quantity, nothing else -- no location, no dates.
 *
 * Data source: mutates via client/src/api/hardware.js
 * No hard-coded fallback: this component renders nothing it was not given or told.
 *
 * @component
 * @param {Object} props
 * @param {string} props.projectId - The project this checkin belongs to.
 *   No fallback/default.
 * @param {string} props.userId - The acting user's id. No fallback/default.
 * @param {Function} props.onCheckedIn - Called after a successful checkin.
 */
export default function CheckinForm({ projectId, userId, onCheckedIn }) {
  const [hwSetName, setHwSetName] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      await checkinHardware({
        projectId,
        userId,
        hwSetName,
        quantity: Number(quantity),
      });
      await onCheckedIn();
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="checkin-form" onSubmit={handleSubmit}>
      <h3>Check in a hardware set</h3>

      <label>
        Hardware set name
        <input
          type="text"
          value={hwSetName}
          onChange={(event) => setHwSetName(event.target.value)}
          required
        />
      </label>

      <label>
        Quantity
        <input
          type="number"
          min="1"
          value={quantity}
          onChange={(event) => setQuantity(event.target.value)}
          required
        />
      </label>

      <button type="submit" disabled={submitting}>
        {submitting ? 'Checking in...' : 'Checkin'}
      </button>

      {error && <p className="error-text">{error}</p>}
    </form>
  );
}
