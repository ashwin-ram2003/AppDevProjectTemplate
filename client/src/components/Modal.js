import { useEffect, useId, useRef } from 'react';

/**
 * Modal is the one shared dialog chrome for both the Add Item form and the
 * item-detail view (06-UI-SPEC.md Layout & Components §4). It renders a
 * backdrop and a centered dialog with a title row and a close button.
 *
 * Beyond the literal chrome markup it owns three keyboard/focus behaviors,
 * required because the backdrop click and the close button are both
 * pointer-only exits (06-UI-SPEC.md §4 cites H3 user control for requiring
 * two exits, but both it names are pointer-reachable only):
 *
 * - Escape closes the dialog -- without this a keyboard user has no exit
 *   at all (WCAG 2.1.1).
 * - Focus moves into the dialog on mount, so keyboard and screen-reader
 *   focus enters the dialog instead of staying behind it on the page
 *   (WCAG 2.4.3).
 * - Focus returns to whatever element opened the dialog on unmount, so
 *   closing the dialog doesn't strand focus at the top of the document.
 *
 * Data source: props only
 * No hard-coded fallback: this component renders nothing it was not given or told.
 *
 * @component
 * @param {Object} props
 * @param {string} props.title - The dialog's heading text.
 * @param {Function} props.onClose - Called when the backdrop, the close
 *   button, or the Escape key is used to dismiss the dialog.
 * @param {import('react').ReactNode} props.children - The dialog body.
 */
export default function Modal({ title, onClose, children }) {
  const titleId = useId();
  const dialogRef = useRef(null);

  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        onClose();
      }
    }
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  useEffect(() => {
    const previouslyFocused = document.activeElement;
    if (dialogRef.current) {
      dialogRef.current.focus();
    }
    return () => {
      if (previouslyFocused && typeof previouslyFocused.focus === 'function') {
        previouslyFocused.focus();
      }
    };
  }, []);

  return (
    <>
      <div className="modal-backdrop" onClick={onClose} />
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}
        ref={dialogRef}
      >
        <div className="modal__header">
          <h3 className="modal__title" id={titleId}>
            {title}
          </h3>
          <button
            type="button"
            className="modal__close"
            onClick={onClose}
            aria-label="Close dialog"
          >
            &#215;
          </button>
        </div>
        {children}
      </div>
    </>
  );
}
