/**
 * MyCheckedOut shows how many units of a hardware set the CURRENT user
 * personally has checked out right now -- not the project-wide total
 * (that's Availability/Capacity). Checkin is capped at this number, not
 * at what the whole project has checked out, so a user can never check
 * in units a different project member checked out.
 *
 * Data source: props only
 *
 * @component
 * @param {Object} props
 * @param {number} props.myCheckedOut - Units this user personally holds.
 */
export default function MyCheckedOut({ myCheckedOut }) {
  return (
    <div className="hw-cell">
      <span className="hw-cell__label">You've Checked Out</span>
      <span className="hw-cell__value">{myCheckedOut}</span>
    </div>
  );
}
