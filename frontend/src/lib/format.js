export function formatMonth(str) {
  if (!str) return ''
  const date = new Date(`${str}-01`)
  if (Number.isNaN(date.getTime())) return str
  return date.toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' })
}

export function formatInt(n) {
  return new Intl.NumberFormat('fr-FR').format(n || 0)
}
