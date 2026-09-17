import type { ReactNode } from 'react';

type FormFieldProps = {
  children: ReactNode;
  label: string;
};

export function FormField({ children, label }: FormFieldProps) {
  return (
    <label className="form-field">
      <span>{label}</span>
      {children}
    </label>
  );
}
