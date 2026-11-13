import React from 'react';

// Labelled input. Pass as="textarea" for a multi-line field.
export default function FormField({ id, label, value, onChange, type = 'text', as = 'input', ...inputProps }) {
  const Input = as;
  const typeProp = as === 'input' ? { type } : {};
  return (
    <div className="form-field">
      <label htmlFor={id}>{label}</label>
      <Input id={id} {...typeProp} value={value} onChange={(e) => onChange(e.target.value)} {...inputProps} />
    </div>
  );
}
