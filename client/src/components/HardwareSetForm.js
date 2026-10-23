import React, { useState } from 'react';
import FormField from './FormField';

// Reusable "create hardware set" form. It owns only form state and feedback;
// what happens on submit is supplied by the parent via onSubmit(name, capacity),
// which should return a promise (rejecting with an Error on failure).
export default function HardwareSetForm({ onSubmit, title = 'Create hardware set' }) {
  // const [name, setName] = useState('');
  // const [capacity, setCapacity] = useState('');
  // const [busy, setBusy] = useState(false);
  // const [status, setStatus] = useState(null); // { ok: boolean, text: string }

  // async function handleSubmit(e) {
  //   e.preventDefault();
  //   const trimmed = name.trim();
  //   if (!trimmed || !/^[1-9]\d*$/.test(capacity)) {
  //     setStatus({ ok: false, text: 'Enter a name and a positive whole-number capacity.' });
  //     return;
  //   }
  //   setBusy(true);
  //   try {
  //     await onSubmit(trimmed, Number(capacity));
  //     setStatus({ ok: true, text: `Created ${trimmed}.` });
  //     setName('');
  //     setCapacity('');
  //   } catch (err) {
  //     setStatus({ ok: false, text: err.message });
  //   } finally {
  //     setBusy(false);
  //   }
  // }

  // return (
  //   <form className="card" onSubmit={handleSubmit}>
  //     <h2>{title}</h2>
  //     <FormField id="hw-name" label="Name" value={name} onChange={setName} placeholder="HWSet1" />
  //     <FormField id="hw-capacity" label="Capacity" value={capacity} onChange={setCapacity} inputMode="numeric" placeholder="100" />
  //     <button type="submit" disabled={busy}>{busy ? 'Creating...' : 'Create'}</button>
  //     {status && <p className={status.ok ? 'msg ok' : 'msg err'}>{status.text}</p>}
  //   </form>
  // );
  return null;
}
