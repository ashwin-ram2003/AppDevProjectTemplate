import { useState } from 'react';

/**
 * QuantityAction is the shared control behind Check In and Check Out: a
 * quantity input plus one action button, with its own busy and error state.
 *
 * Data source: calls the `action` prop
 *
 * @component
 * @param {Object} props
 * @param {string} props.label - Button text and input label, e.g. "Check Out".
 * @param {string} props.busyLabel - Button text while the call is in flight.
 * @param {Function} props.action - Async `(quantity: number) => void`; throws
 *   on failure.
 * @param {Function} props.describeError - `(error) => string` user-facing
 *   message for a failed action.
 * @param {Function} props.onChanged - Async reload callback, awaited after
 *   every successful action.
 * @param {number} [props.max] - The largest quantity this action can
 *   legitimately take right now (e.g. units available for Check Out,
 *   units checked out for Check In). Caps the input's spinner arrows;
 *   with no cap to apply (undefined), the input is left unbounded. When
 *   max is below 1, there is nothing valid to submit, so the control is
 *   disabled outright rather than left stuck between an unreachable
 *   min="1" and max.
 * @param {boolean} [props.disabled] - Disables the input and button
 *   regardless of max (e.g. a deactivated hardware set). Omitted = no effect.
 */
export default function QuantityAction({
  label,
  busyLabel,
  action,
  describeError,
  onChanged,
  max,
  disabled = false,
}) {
  const [quantity, setQuantity] = useState('1');
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const nothingToDo = disabled || (typeof max === 'number' && max < 1);

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await action(Number(quantity));
      await onChanged();
    } catch (actionError) {
      setError(describeError(actionError));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="hw-cell hw-action" onSubmit={handleSubmit}>
      <label className="hw-cell__label">
        {label}
        <input
          type="number"
          min="1"
          max={max}
          step="1"
          value={quantity}
          onChange={(event) => setQuantity(event.target.value)}
          disabled={nothingToDo}
        />
      </label>
      <button type="submit" disabled={busy || nothingToDo}>
        {busy ? busyLabel : label}
      </button>
      {error && (
        <p className="error-text hw-action__error" role="alert">
          {error}
        </p>
      )}
    </form>
  );
}
