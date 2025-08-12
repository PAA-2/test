export const validateValue = (field, value) => {
  if (field.required) {
    if (field.type === 'tags') {
      if (!value || value.length === 0) return 'Champ requis'
    } else if (field.type === 'bool') {
      if (value === undefined || value === null) return 'Champ requis'
    } else if (value === undefined || value === null || value === '') {
      return 'Champ requis'
    }
  }

  if (value === undefined || value === null || value === '') return null

  switch (field.type) {
    case 'number': {
      if (typeof value !== 'number' || Number.isNaN(value)) return 'Type invalide'
      if (field.min != null && value < field.min) return `Min ${field.min}`
      if (field.max != null && value > field.max) return `Max ${field.max}`
      break
    }
    case 'date': {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return 'Date invalide'
      break
    }
    case 'bool': {
      if (typeof value !== 'boolean') return 'Type invalide'
      break
    }
    case 'text': {
      if (field.min != null && value.length < field.min) return `Min ${field.min}`
      if (field.max != null && value.length > field.max) return `Max ${field.max}`
      if (field.regex && !new RegExp(field.regex).test(value)) return 'Format invalide'
      break
    }
    case 'tags': {
      if (!Array.isArray(value)) return 'Type invalide'
      if (field.min != null && value.length < field.min) return `Min ${field.min}`
      if (field.max != null && value.length > field.max) return `Max ${field.max}`
      if (field.options) {
        const opts = field.options.map((o) => o.value)
        if (!value.every((v) => opts.includes(v))) return 'Valeur invalide'
      }
      break
    }
    case 'select': {
      if (field.options) {
        const opts = field.options.map((o) => o.value)
        if (!opts.includes(value)) return 'Valeur invalide'
      }
      break
    }
  }
  return null
}

export const validateAll = (schema, values) => {
  const errors = {}
  if (schema && schema.fields) {
    schema.fields.forEach((field) => {
      const err = validateValue(field, values[field.key])
      if (err) errors[field.key] = err
    })
  }
  return { errors, isValid: Object.keys(errors).length === 0 }
}
