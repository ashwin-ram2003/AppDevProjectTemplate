// Generic pop-up dialog, used for sign up

import React, { useEffect, useId, useRef } from 'react';

export default function Modal({ open, title, onClose, children }) {
  const titleId = useId();
  const dialogRef = useRef(null);

  useEffect(() => {
    if (!open) return undefined;

    // Remember what had focus so it can get it back when the dialog closes
    const previouslyFocused = document.activeElement;

    // Focus the first field inside the dialog
    const firstField = dialogRef.current?.querySelector('input, select, textarea');
    (firstField || dialogRef.current)?.focus();

    function handleKeyDown(e) {
      if (e.key === 'Escape') onClose();
    }
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      if (previouslyFocused && typeof previouslyFocused.focus === 'function') {
        previouslyFocused.focus();
      }
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    // Clicking the dim backdrop closes
    <div className="modal-backdrop" onMouseDown={onClose}>
      <div
        className="card modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}
        ref={dialogRef}
        onMouseDown={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h2 id={titleId}>{title}</h2>
          <button className="modal-close" type="button" aria-label="Close" onClick={onClose}>
            ✕
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}