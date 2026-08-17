export const formatCurrency = (amount) => {
  if (amount === null || amount === undefined || isNaN(amount)) return '৳0'
  const num = Number(amount)
  // Format with Bangladeshi/Indian numbering or standard thousands
  return `৳${num.toLocaleString('en-IN', {
    maximumFractionDigits: 2,
    minimumFractionDigits: num % 1 === 0 ? 0 : 2
  })}`
}

export const formatNumber = (num) => {
  if (num === null || num === undefined || isNaN(num)) return '0'
  return Number(num).toLocaleString('en-IN')
}

export const formatCompact = (num) => {
  if (!num || isNaN(num)) return '0'
  const n = Number(num)
  if (n >= 10000000) return `${(n / 10000000).toFixed(1)}Cr`
  if (n >= 100000) return `${(n / 100000).toFixed(1)}L`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`
  return String(n)
}

export const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    })
  } catch (e) {
    return dateStr
  }
}

export const getInitials = (name) => {
  if (!name) return 'AI'
  const parts = name.trim().split(' ')
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
}
