export const shortNumber = (num) => {
  if (num == null) return '0'
  if (num < 1000) return `${num}`
  if (num < 1_000_000) return `${(num / 1000).toFixed(1)}k`
  return `${(num / 1_000_000).toFixed(1)}m`
}

export const timeAgo = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const diff = (Date.now() - date.getTime()) / 1000
  if (diff < 60) return 'همین حالا'
  if (diff < 3600) return `${Math.floor(diff / 60)} دقیقه پیش`
  if (diff < 86400) return `${Math.floor(diff / 3600)} ساعت پیش`
  return `${Math.floor(diff / 86400)} روز پیش`
}
