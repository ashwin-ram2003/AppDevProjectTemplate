import React from 'react';

export default function FormField({ id, label, value, onChange, type = 'text', ...inputProps }) {
  return (
    <div className="form-field">
      <label htmlFor={id}>{label}</label>
      <input id={id} type={type} value={value} onChange={(e) => onChange(e.target.value)} {...inputProps} />
    </div>
  );
}
