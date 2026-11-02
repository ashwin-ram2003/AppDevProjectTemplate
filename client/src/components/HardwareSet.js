import Availability from './Availability.js';
import Capacity from './Capacity.js';
import MyCheckedOut from './MyCheckedOut.js';
import CheckIn from './CheckIn.js';
import CheckOut from './CheckOut.js';
import HardwareSetAdmin from './HardwareSetAdmin.js';

/**
 * HardwareSet is one hardware set's card: its name plus five components --
 * Availability, Capacity, My Checked Out, Check In, and Check Out.
 *
 * Data source: props only
 *
 * @component
 * @param {Object} props
 * @param {string} props.projectId - The project the set belongs to.
 * @param {string} props.userId - The acting member's id.
 * @param {Object} props.hwSet - `{ hwSetName, capacity, available,
 *   myCheckedOut, active }`. active === false means deactivated (a missing
 *   value reads as active). myCheckedOut is this user's own holding (server-
 *   tracked per user), not derived from capacity/available -- those are
 *   project-wide and say nothing about who personally holds what.
 * @param {Function} props.onChanged - Async reload callback.
 */
export default function HardwareSet({ projectId, userId, hwSet, onChanged }) {
  const inactive = hwSet.active === false;

  return (
    <section
      className={inactive ? 'hw-set hw-set--inactive' : 'hw-set'}
      aria-label={hwSet.hwSetName}
    >
      <div className="hw-set__header">
        <h2 className="hw-set__name">{hwSet.hwSetName}</h2>
        {inactive && <span className="hw-set__status">Inactive</span>}
      </div>
      {inactive && (
        <p className="muted-text">
          Deactivated -- no new check-outs. Units already out can still be checked in.
        </p>
      )}
      <div className="hw-set__grid">
        <Availability available={hwSet.available} />
        <Capacity capacity={hwSet.capacity} />
        <MyCheckedOut myCheckedOut={hwSet.myCheckedOut} />
        <CheckIn
          projectId={projectId}
          userId={userId}
          hwSetName={hwSet.hwSetName}
          checkedOut={hwSet.myCheckedOut}
          onChanged={onChanged}
        />
        <CheckOut
          projectId={projectId}
          userId={userId}
          hwSetName={hwSet.hwSetName}
          available={hwSet.available}
          onChanged={onChanged}
          disabled={inactive}
        />
      </div>
      <HardwareSetAdmin
        projectId={projectId}
        userId={userId}
        hwSet={hwSet}
        onChanged={onChanged}
      />
    </section>
  );
}
