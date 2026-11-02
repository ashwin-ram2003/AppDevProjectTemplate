import { checkoutHardware } from '../api/hardware.js';
import QuantityAction from './QuantityAction.js';

function describeCheckoutError(error) {
  if (error.message === 'hardware_set_inactive') {
    return "This hardware set is deactivated, so it can't be checked out.";
  }
  if (typeof error.onHand === 'number') {
    return `Only ${error.onHand} available -- can't check out ${error.requested}.`;
  }
  if (error.field === 'quantity') {
    return 'Enter a whole number of 1 or more.';
  }
  return error.message;
}

/**
 * CheckOut takes a quantity of one hardware set, lowering its availability.
 * Rejected with a visible message when more than is available is requested.
 *
 * Data source: mutates via client/src/api/hardware.js
 *
 * @component
 * @param {Object} props
 * @param {string} props.projectId - The project the set belongs to.
 * @param {string} props.userId - The acting member's id.
 * @param {string} props.hwSetName - The hardware set to check out.
 * @param {number} props.available - Units of this set currently
 *   available -- the most that can be checked out right now. No
 *   fallback/default.
 * @param {Function} props.onChanged - Async reload callback.
 * @param {boolean} [props.disabled] - True while the set is deactivated.
 */
export default function CheckOut({ projectId, userId, hwSetName, available, onChanged, disabled }) {
  return (
    <QuantityAction
      label="Check Out"
      busyLabel="Checking out..."
      action={(quantity) => checkoutHardware({ projectId, userId, hwSetName, quantity })}
      describeError={describeCheckoutError}
      onChanged={onChanged}
      max={available}
      disabled={disabled}
    />
  );
}
