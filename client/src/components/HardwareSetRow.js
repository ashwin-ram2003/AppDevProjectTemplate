import { useEffect, useState } from "react";

import Button from "./Button";

function HardwareSetRow({
  hardware,
  checkedOut,
  projectId,
  disabled = false,
  onUpdateHardware,
}) {
  const [quantity, setQuantity] = useState(1);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    if (message?.type !== "success") return undefined;
    const timer = setTimeout(() => setMessage(null), 2000);
    return () => clearTimeout(timer);
  }, [message]);

  const readQuantity = () => {
    const amount = Number(quantity);
    if (!Number.isInteger(amount) || amount < 1) {
      setMessage({ type: "error", text: "Enter a positive whole number." });
      return null;
    }
    return amount;
  };

  const checkOut = () => {
    const amount = readQuantity();
    if (amount === null) return;
    if (amount > hardware.available) {
      setMessage({
        type: "error",
        text: hardware.available === 0
          ? `${hardware.name} is out of stock.`
          : `Only ${hardware.available} unit(s) are available.`,
      });
      return;
    }

    onUpdateHardware(projectId, hardware.name, amount);
    setMessage({ type: "success", text: `Checked out ${amount} unit(s).` });
  };

  const checkIn = () => {
    const amount = readQuantity();
    if (amount === null) return;
    if (amount > checkedOut) {
      setMessage({
        type: "error",
        text: checkedOut === 0
          ? `${hardware.name} is already full.`
          : `This project can only check in ${checkedOut} unit(s).`,
      });
      return;
    }

    onUpdateHardware(projectId, hardware.name, -amount);
    setMessage({ type: "success", text: `Checked in ${amount} unit(s).` });
  };

  return (
    <div className="project-hardware-row" aria-label={`${hardware.name} controls`}>
      <div className="project-hardware-status">
        <strong>{hardware.name}</strong>
        <span>Available: {hardware.available} / {hardware.capacity}</span>
      </div>

      <div className="project-hardware-actions">
        <label htmlFor={`${projectId}-${hardware.name}-quantity`}>Qty</label>
        <input
          id={`${projectId}-${hardware.name}-quantity`}
          aria-label={`Quantity for ${hardware.name} in ${projectId}`}
          type="number"
          min="1"
          value={quantity}
          disabled={disabled}
          onChange={(event) => {
            setQuantity(event.target.value);
            setMessage(null);
          }}
        />
        <Button onClick={checkOut} disabled={disabled}>Check Out</Button>
        <Button onClick={checkIn} disabled={disabled}>Check In</Button>
      </div>

      {message && (
        <p
          className={`hardware-action-message ${message.type}`}
          role={message.type === "error" ? "alert" : "status"}
        >
          {message.text}
        </p>
      )}
    </div>
  );
}

export default HardwareSetRow;
