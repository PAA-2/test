export function downloadBlob(response, filenameFallback) {
  const blob = response.data
  if (!(blob instanceof Blob)) {
    throw new Error('Invalid blob response')
  }
  let filename = filenameFallback
  const disposition = response.headers?.['content-disposition']
  if (disposition) {
    const match = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
    if (match && match[1]) {
      filename = decodeURIComponent(match[1].replace(/['"]/g, ''))
    }
  } else {
    const ts = new Date().toISOString().replace(/[-:]/g, '').split('.')[0]
    const dot = filenameFallback.lastIndexOf('.')
    if (dot !== -1) {
      const name = filenameFallback.slice(0, dot)
      const ext = filenameFallback.slice(dot)
      filename = `${name}_${ts}${ext}`
    } else {
      filename = `${filenameFallback}_${ts}`
    }
  }
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}
