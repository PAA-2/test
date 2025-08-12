import React from 'react'

export default function FieldRenderer({ field, value, onChange, error }) {
  const base = 'w-full border rounded-xl p-2'
  const className = error ? `${base} border-red-500` : base

  switch (field.type) {
    case 'text':
      return (
        <input
          type="text"
          className={className}
          value={value ?? ''}
          onChange={(e) => onChange(e.target.value)}
        />
      )
    case 'number':
      return (
        <input
          type="number"
          className={className}
          value={value ?? ''}
          onChange={(e) =>
            onChange(e.target.value === '' ? '' : Number(e.target.value))
          }
        />
      )
    case 'date':
      return (
        <input
          type="date"
          className={className}
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
        />
      )
    case 'select':
      return (
        <select
          className={className}
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
        >
          <option value=""></option>
          {(field.options || []).map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      )
    case 'tags':
      return (
        <select
          multiple
          className={`${className} h-32`}
          value={value || []}
          onChange={(e) =>
            onChange(Array.from(e.target.selectedOptions).map((o) => o.value))
          }
        >
          {(field.options || []).map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      )
    case 'bool':
      return (
        <input
          type="checkbox"
          checked={!!value}
          onChange={(e) => onChange(e.target.checked)}
        />
      )
    default:
      return null
  }
}
