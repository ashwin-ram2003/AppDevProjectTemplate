/**
 * Availability shows how many units of a hardware set can be checked out
 * right now (capacity minus what is currently checked out).
 *
 * Data source: props only
 *
 * @component
 * @param {Object} props
 * @param {number} props.available - Units currently available.
 */
export default function Availability({ available }) {
  return (
    <div className="hw-cell">
      <span className="hw-cell__label">Available</span>
      <span className="hw-cell__value">{available}</span>
    </div>
  );
}
