import FieldRenderer from './FieldRenderer.jsx'

export default function FormBuilder({ schema, values, onChange, errors = {} }) {
  if (!schema || !schema.fields) return null
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {schema.fields.map((field) => (
        <div key={field.key} className="rounded-2xl shadow p-4">
          <label className="block text-sm text-gray-600 mb-1">
            {field.label || field.key}
            {field.required && <span className="text-red-500 ml-1">*</span>}
          </label>
          <FieldRenderer
            field={field}
            value={values[field.key]}
            onChange={(val) => onChange(field.key, val)}
            error={errors[field.key]}
          />
          {field.help_text && (
            <p className="text-xs text-gray-500 mt-1">{field.help_text}</p>
          )}
          {errors[field.key] && (
            <p className="text-xs text-red-600 mt-1">{errors[field.key]}</p>
          )}
        </div>
      ))}
    </div>
  )
}
