// Generic pop-up dialog, used for sign up

import React, { useEffect, useId, useRef } from 'react';

// Inline styles so the pop-up works without any extra CSS
const backdropStyle = {
  position: 'fixed',
  inset: 0,
  background: 'rgba(0, 0, 0, 0.45)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: 16,
  zIndex: 1000,
};

const dialogStyle = {
  width: '100%',
  maxWidth: 420,
  maxHeight: '90vh',
  overflowY: 'auto',
  margin: 0,
};

const headerStyle = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  marginBottom: 8,
};

const closeButtonStyle = {
  background: 'transparent',
  color: 'inherit',
  fontSize: 18,
  padding: '4px 8px',
};

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
    <div style={backdropStyle} onMouseDown={onClose}>
      <div
        className="card"
        style={dialogStyle}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}
        ref={dialogRef}
        onMouseDown={(e) => e.stopPropagation()}
      >
        <div style={headerStyle}>
          <h2 id={titleId} style={{ margin: 0 }}>{title}</h2>
          <button type="button" style={closeButtonStyle} aria-label="Close" onClick={onClose}>
            ✕
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}