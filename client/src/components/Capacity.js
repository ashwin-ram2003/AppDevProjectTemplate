/**
 * Capacity shows the fixed total number of units in a hardware set. It does
 * not change when units are checked out or in.
 *
 * Data source: props only
 *
 * @component
 * @param {Object} props
 * @param {number} props.capacity - Total units in the hardware set.
 */
export default function Capacity({ capacity }) {
  return (
    <div className="hw-cell">
      <span className="hw-cell__label">Capacity</span>
      <span className="hw-cell__value">{capacity}</span>
    </div>
  );
}
