import { useState } from 'react';
import { checkoutHardware, requestHardware, releaseRequest } from '../api/hardware.js';

/**
 * The name "Checkout.js" carries over from the assignment's Resource
 * Management mockup, which shows Checkout and Checkin buttons directly.
 * This component renders Checkout and Request/Release -- everything a
 * project member does to a hardware set's own row besides checking it in.
 *
 * A request is a coordination signal among project members ("dibs"), never a
 * lock (SN3). The checkout control below is never disabled, hidden, or
 * gated by the presence of any request, and the request display below only
 * ever names who claimed what -- it never says "unavailable", "locked", or
 * "blocked".
 *
 * Data source: mutates via client/src/api/hardware.js
 * No hard-coded fallback: this component renders nothing it was not given or told.
 *
 * @component
 * @param {Object} props
 * @param {string} props.projectId - The project this hardware set belongs
 *   to. No fallback/default.
 * @param {Object} props.hwSet - The already-fetched hardware set object.
 *   Reads `hwSetName`, `capacity`, `requests`, and `requestedQuantity`.
 * @param {string} props.userId - The acting member's identity. No default.
 * @param {string} props.userName - The acting member's display name. No
 *   default.
 * @param {Function} props.onChanged - Async reload callback, awaited after
 *   every successful mutation.
 */
export default function HardwareActions({ projectId, hwSet, userId, userName, onChanged }) {
  const [checkoutQuantity, setCheckoutQuantity] = useState('1');
  const [requestQuantity, setRequestQuantity] = useState('1');
  const [checkoutError, setCheckoutError] = useState(null);
  const [requestError, setRequestError] = useState(null);
  const [releaseError, setReleaseError] = useState(null);
  const [checkingOut, setCheckingOut] = useState(false);
  const [claimInFlight, setClaimInFlight] = useState(false);
  const [releaseTargetId, setReleaseTargetId] = useState(null);

  async function handleCheckout(event) {
    event.preventDefault();
    setCheckoutError(null);
    setCheckingOut(true);
    try {
      await checkoutHardware({
        projectId,
        userId,
        hwSetName: hwSet.hwSetName,
        quantity: Number(checkoutQuantity),
      });
      // Leave the entered quantity in place on success too -- a member
      // checking out the same amount repeatedly shouldn't have to retype it
      // every time.
      await onChanged();
    } catch (error) {
      if (typeof error.onHand === 'number') {
        setCheckoutError(
          `Only ${error.onHand} available -- can't check out ${error.requested}. Try a smaller amount.`
        );
      } else {
        setCheckoutError(error.message);
      }
    } finally {
      setCheckingOut(false);
    }
  }

  async function handleRequest(event) {
    event.preventDefault();
    setRequestError(null);
    setClaimInFlight(true);
    try {
      await requestHardware({
        projectId,
        userId,
        userName,
        hwSetName: hwSet.hwSetName,
        quantity: Number(requestQuantity),
      });
      await onChanged();
    } catch (error) {
      setRequestError(error.message);
    } finally {
      setClaimInFlight(false);
    }
  }

  async function handleRelease(targetId) {
    setReleaseError(null);
    setReleaseTargetId(targetId);
    try {
      await releaseRequest({
        projectId,
        userId,
        requestId: targetId,
      });
      await onChanged();
    } catch (error) {
      setReleaseError(error.message);
    } finally {
      setReleaseTargetId(null);
    }
  }

  const requests = hwSet.requests || [];
  const requestedTotal = hwSet.requestedQuantity || 0;
  const overRequested = requestedTotal > hwSet.capacity;

  return (
    // Clicking inside these controls must not toggle any surrounding
    // disclosure the hardware set row lives in.
    <div className="hw-actions" onClick={(event) => event.stopPropagation()}>
      <form className="hw-actions__row" onSubmit={handleCheckout}>
        <label className="hw-actions__field">
          Checkout
          <input
            type="number"
            min="1"
            value={checkoutQuantity}
            onChange={(event) => setCheckoutQuantity(event.target.value)}
          />
        </label>
        <button type="submit" disabled={checkingOut}>
          {checkingOut ? 'Checking out...' : 'Checkout'}
        </button>
      </form>
      {checkoutError && <p className="error-text hw-actions__message">{checkoutError}</p>}

      <form className="hw-actions__row" onSubmit={handleRequest}>
        <label className="hw-actions__field">
          Request
          <input
            type="number"
            min="1"
            value={requestQuantity}
            onChange={(event) => setRequestQuantity(event.target.value)}
          />
        </label>
        <button type="submit" disabled={claimInFlight}>
          {claimInFlight ? 'Requesting...' : 'Request'}
        </button>
      </form>
      {requestError && <p className="error-text hw-actions__message">{requestError}</p>}

      <div className="hw-actions__requests">
        {requests.length === 0 ? (
          <p className="muted-text">No one has requested this hardware set.</p>
        ) : (
          <ul className="request-list">
            {requests.map((entry) => {
              const entryId = entry.requestId;
              const isThisRowPending = releaseTargetId === entryId;
              return (
                <li
                  key={entryId}
                  className={
                    entry.userId === userId
                      ? 'request-entry request-entry--own'
                      : 'request-entry request-entry--other'
                  }
                >
                  <span className="request-entry__label">
                    Requested by {entry.userName}: {entry.quantity}
                  </span>
                  {entry.userId === userId && (
                    <button
                      type="button"
                      className="request-entry__release"
                      onClick={() => handleRelease(entryId)}
                      disabled={isThisRowPending}
                    >
                      {isThisRowPending ? 'Releasing...' : 'Release'}
                    </button>
                  )}
                </li>
              );
            })}
          </ul>
        )}
        {overRequested && (
          <p className="muted-text hw-actions__over-requested">
            {requestedTotal} requested of {hwSet.capacity} capacity -- requesting is a
            coordination signal, not a hold, so this is expected.
          </p>
        )}
      </div>
      {releaseError && <p className="error-text hw-actions__message">{releaseError}</p>}
    </div>
  );
}
