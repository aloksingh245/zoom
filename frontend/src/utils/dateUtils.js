import { SESSION_DURATION_MINS } from '../constants'

export function startOfWeek(date) {
  const d = new Date(date)
  const day = d.getDay()
  const diff = (day === 0 ? -6 : 1) - day
  d.setDate(d.getDate() + diff)
  d.setHours(0, 0, 0, 0)
  return d
}

export function formatDate(date) {
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function formatHour(hour) {
  const h = hour % 12 || 12
  const suffix = hour >= 12 ? 'PM' : 'AM'
  return `${h}:00 ${suffix}`
}

export function dayLabel(date) {
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  })
}

export function getClassStatus(item) {
  try {
    const now = new Date()
    const nowInTz = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }))
    
    const start = new Date(`${item.date}T${item.start_time}:00`)
    const end = new Date(start.getTime() + SESSION_DURATION_MINS * 60000)

    if (nowInTz < start) return 'upcoming'
    if (nowInTz >= start && nowInTz <= end) return 'live'
    return 'completed'
  } catch {
    return 'upcoming'
  }
}

export function isPastLocal(dateStr, timeStr, timezone) {
  try {
    const now = new Date()
    const parts = new Intl.DateTimeFormat('en-US', {
      timeZone: timezone,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    })
      .formatToParts(now)
      .reduce((acc, part) => {
        if (part.type !== 'literal') acc[part.type] = part.value
        return acc
      }, {})

    const nowTz = Date.parse(
      `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}:${parts.second}`,
    )
    const local = Date.parse(`${dateStr}T${timeStr}:00`)
    if (Number.isNaN(local) || Number.isNaN(nowTz)) return true
    return local <= nowTz
  } catch {
    return true
  }
}

export function getEndTime(startTimeStr) {
  const [h, mm] = startTimeStr.split(':').map(Number)
  const total = h * 60 + mm + SESSION_DURATION_MINS
  const eh = Math.floor(total / 60) % 24
  const em = total % 60
  return `${String(eh).padStart(2, '0')}:${String(em).padStart(2, '0')}`
}
