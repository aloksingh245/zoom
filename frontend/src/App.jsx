import { useEffect, useMemo, useState } from 'react'
import {
  listClasses,
  createClass,
  updateClass,
  deleteClass,
  listCourses,
  createCourse,
} from './api'

const HOURS = Array.from({ length: 12 }, (_, idx) => 8 + idx)

function startOfWeek(date) {
  const d = new Date(date)
  const day = d.getDay()
  const diff = (day === 0 ? -6 : 1) - day
  d.setDate(d.getDate() + diff)
  d.setHours(0, 0, 0, 0)
  return d
}

function formatDate(date) {
  return date.toISOString().slice(0, 10)
}

function formatDateDisplay(yyyyMmDd) {
  const [y, m, d] = yyyyMmDd.split('-')
  if (!y || !m || !d) return yyyyMmDd
  return `${d}/${m}/${y}`
}

function formatHour(hour) {
  const h = hour % 12 || 12
  const suffix = hour >= 12 ? 'PM' : 'AM'
  return `${h}:00 ${suffix}`
}

function dayLabel(date) {
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  })
}

function emptyForm(selectedDate) {
  return {
    course_id: '',
    course_name: '',
    topic_name: '',
    assignment_name: '',
    date: selectedDate,
    start_time: '09:00',
    timezone: 'Asia/Kolkata',
  }
}

function isPastLocal(dateStr, timeStr, timezone) {
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

export default function App() {
  const [classes, setClasses] = useState([])
  const [courses, setCourses] = useState([])
  const [selectedDate, setSelectedDate] = useState(formatDate(new Date()))
  const [weekAnchor, setWeekAnchor] = useState(new Date())
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(emptyForm(selectedDate))
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const weekStart = useMemo(() => startOfWeek(weekAnchor), [weekAnchor])
  const weekDays = useMemo(() => {
    return Array.from({ length: 7 }, (_, idx) => {
      const d = new Date(weekStart)
      d.setDate(weekStart.getDate() + idx)
      return d
    })
  }, [weekStart])

  const classesByDate = useMemo(() => {
    const map = new Map()
    classes.forEach((item) => {
      if (!map.has(item.date)) map.set(item.date, [])
      map.get(item.date).push(item)
    })
    map.forEach((list) => list.sort((a, b) => a.start_time.localeCompare(b.start_time)))
    return map
  }, [classes])

  useEffect(() => {
    async function load() {
      setLoading(true)
      setError('')
      try {
        const [classList, courseList] = await Promise.all([listClasses(), listCourses()])
        setClasses(classList)
        setCourses(courseList)
      } catch (err) {
        setError(err.message || 'Failed to load data')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  useEffect(() => {
    setForm((prev) => ({ ...prev, date: selectedDate }))
  }, [selectedDate])

  function openCreate(date, hour) {
    setEditing(null)
    setForm({
      ...emptyForm(date),
      start_time: `${String(hour).padStart(2, '0')}:00`,
    })
    setIsModalOpen(true)
  }

  function openEdit(item) {
    setEditing(item)
    setForm({
      course_id: item.course_id,
      course_name: item.course_name,
      topic_name: item.topic_name,
      assignment_name: item.assignment_name || '',
      date: item.date,
      start_time: item.start_time,
      timezone: item.timezone,
    })
    setIsModalOpen(true)
  }

  async function handleSave(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (isPastLocal(form.date, form.start_time, form.timezone)) {
        setError('Start time must be in the future (Asia/Kolkata).')
        setLoading(false)
        return
      }
      let payload = {
        course_id: form.course_id || undefined,
        course_name: form.course_id ? undefined : form.course_name,
        topic_name: form.topic_name,
        assignment_name: form.assignment_name || undefined,
        date: form.date,
        start_time: form.start_time,
        timezone: form.timezone,
      }

      if (!payload.course_id && payload.course_name) {
        const existing = courses.find((c) => c.name.toLowerCase() === payload.course_name.toLowerCase())
        if (!existing) {
          const created = await createCourse({ name: payload.course_name })
          setCourses((prev) => [...prev, created])
          payload = { ...payload, course_id: created.id, course_name: undefined }
        }
      }

      let saved
      if (editing) {
        saved = await updateClass(editing.id, payload)
        setClasses((prev) => prev.map((item) => (item.id === saved.id ? saved : item)))
      } else {
        saved = await createClass(payload)
        setClasses((prev) => [...prev, saved])
      }
      setIsModalOpen(false)
    } catch (err) {
      setError(err.message || 'Failed to save class')
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete() {
    if (!editing) return
    setLoading(true)
    setError('')
    try {
      await deleteClass(editing.id)
      setClasses((prev) => prev.filter((item) => item.id !== editing.id))
      setIsModalOpen(false)
    } catch (err) {
      setError(err.message || 'Failed to delete class')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#05070c] via-[#0a1220] to-[#0b1c33] text-slate-100">
      <header className="px-6 py-6">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-blue-300/70">Class Scheduler</p>
            <h1 className="text-3xl font-semibold text-white">Weekly Studio</h1>
          </div>
          <div className="flex items-center gap-3">
            <button
              className="rounded-full border border-blue-500/40 bg-blue-500/10 px-4 py-2 text-sm text-blue-100 transition hover:border-blue-400 hover:bg-blue-500/20"
              onClick={() => setWeekAnchor(new Date())}
            >
              Today
            </button>
            <button
              className="rounded-full bg-blue-500 px-4 py-2 text-sm font-semibold text-slate-900 shadow-lg shadow-blue-500/30 transition hover:-translate-y-0.5"
              onClick={() => openCreate(selectedDate, 9)}
            >
              + New Class
            </button>
          </div>
        </div>
      </header>

      <main className="px-6 pb-12">
        {error ? (
          <div className="mb-4 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {error}
          </div>
        ) : null}

        <section className="rounded-3xl border border-white/10 bg-[#0b1324]/80 p-6 shadow-2xl shadow-blue-900/20 backdrop-blur">
          <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-blue-300/60">Week Of</p>
              <p className="text-lg font-semibold text-white">{dayLabel(weekStart)}</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                className="rounded-full border border-white/10 px-3 py-2 text-sm text-blue-100 hover:border-blue-400/50"
                onClick={() => {
                  const prev = new Date(weekAnchor)
                  prev.setDate(prev.getDate() - 7)
                  setWeekAnchor(prev)
                }}
              >
                Prev
              </button>
              <button
                className="rounded-full border border-white/10 px-3 py-2 text-sm text-blue-100 hover:border-blue-400/50"
                onClick={() => {
                  const next = new Date(weekAnchor)
                  next.setDate(next.getDate() + 7)
                  setWeekAnchor(next)
                }}
              >
                Next
              </button>
            </div>
          </div>

          <div className="grid grid-cols-8 gap-2 text-xs uppercase tracking-[0.2em] text-blue-200/70">
            <div></div>
            {weekDays.map((day) => {
              const dateStr = formatDate(day)
              const isSelected = dateStr === selectedDate
              return (
                <button
                  key={dateStr}
                  className={`rounded-xl border px-2 py-2 text-left transition ${
                    isSelected
                      ? 'border-blue-400 bg-blue-500/20 text-blue-100'
                      : 'border-white/5 bg-white/5 text-blue-200/70 hover:border-blue-400/40'
                  }`}
                  onClick={() => setSelectedDate(dateStr)}
                >
                  <div className="text-[10px]">{day.toLocaleDateString('en-US', { weekday: 'short' })}</div>
                  <div className="text-sm font-semibold text-white">{day.getDate()}</div>
                </button>
              )
            })}
          </div>

          <div className="mt-6 grid grid-cols-8 gap-2">
            <div className="flex flex-col gap-2">
              {HOURS.map((hour) => (
                <div key={hour} className="rounded-xl border border-white/5 bg-white/5 px-2 py-3 text-xs text-blue-200/70">
                  {formatHour(hour)}
                </div>
              ))}
            </div>
            {weekDays.map((day) => {
              const dateStr = formatDate(day)
              const dayClasses = classesByDate.get(dateStr) || []
              return (
                <div key={dateStr} className="flex flex-col gap-2">
                  {HOURS.map((hour) => {
                    const slot = dayClasses.filter((item) => Number(item.start_time.slice(0, 2)) === hour)
                    return (
                      <div
                        key={`${dateStr}-${hour}`}
                        className="group relative min-h-[56px] rounded-xl border border-white/5 bg-[#0a1629] p-2 text-xs text-blue-200/70 transition hover:border-blue-400/40"
                      >
                        <button
                          className="absolute inset-0"
                          onClick={() => openCreate(dateStr, hour)}
                        />
                        <div className="relative z-10 flex flex-col gap-1">
                          {slot.map((item) => (
                            <button
                              key={item.id}
                              onClick={(e) => {
                                e.stopPropagation()
                                openEdit(item)
                              }}
                              className="rounded-lg border border-blue-500/40 bg-blue-500/20 px-2 py-1 text-left text-[11px] text-blue-50 hover:bg-blue-500/30"
                            >
                              <div className="font-semibold">{item.course_name}</div>
                              <div className="text-blue-100/80">{item.topic_name}</div>
                            </button>
                          ))}
                        </div>
                      </div>
                    )
                  })}
                </div>
              )
            })}
          </div>
        </section>

        <section className="mt-8 rounded-3xl border border-white/10 bg-[#0b1324]/80 p-6 shadow-2xl shadow-blue-900/20">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-blue-300/60">Classes On</p>
              <h2 className="text-xl font-semibold text-white">{formatDateDisplay(selectedDate)}</h2>
            </div>
            {loading ? <span className="text-xs text-blue-200/70">Loading...</span> : null}
          </div>
          <div className="grid gap-3">
            {(classesByDate.get(selectedDate) || []).map((item) => (
              <div key={item.id} className="rounded-2xl border border-white/10 bg-[#0a1629] px-4 py-3">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <div className="text-sm text-blue-200/70">{item.start_time} · {item.duration_minutes} mins</div>
                    <div className="text-lg font-semibold text-white">{item.course_name}</div>
                    <div className="text-sm text-blue-100/80">{item.topic_name}</div>
                    {item.assignment_name ? (
                      <div className="text-xs text-blue-200/70">Assignment: {item.assignment_name}</div>
                    ) : null}
                  </div>
                  <div className="flex flex-col gap-2 text-right">
                    <button
                      className="rounded-full border border-blue-500/40 px-3 py-1 text-xs text-blue-100 hover:border-blue-400"
                      onClick={() => openEdit(item)}
                    >
                      Edit
                    </button>
                    <a
                      className="rounded-full bg-blue-500 px-3 py-1 text-xs font-semibold text-slate-900"
                      href={item.zoom_join_url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Join Zoom
                    </a>
                  </div>
                </div>
              </div>
            ))}
            {(classesByDate.get(selectedDate) || []).length === 0 ? (
              <div className="rounded-2xl border border-dashed border-blue-500/30 bg-blue-500/5 px-4 py-8 text-center text-sm text-blue-200/70">
                No classes scheduled for this date.
              </div>
            ) : null}
          </div>
        </section>
      </main>

      {isModalOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
          <form
            onSubmit={handleSave}
            className="w-full max-w-xl rounded-3xl border border-white/10 bg-[#0b1324] p-6 shadow-2xl"
          >
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-blue-300/60">Class Details</p>
                <h3 className="text-xl font-semibold text-white">
                  {editing ? 'Edit Class' : 'Schedule Class'}
                </h3>
              </div>
              <button
                type="button"
                className="rounded-full border border-white/10 px-3 py-1 text-xs text-blue-200"
                onClick={() => setIsModalOpen(false)}
              >
                Close
              </button>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="md:col-span-2">
                <label className="text-xs uppercase tracking-[0.2em] text-blue-200/70">Course</label>
                <div className="mt-2 grid gap-2 md:grid-cols-2">
                  <select
                    className="rounded-xl border border-white/10 bg-[#0a1629] px-3 py-2 text-sm text-white"
                    value={form.course_id}
                    onChange={(e) => setForm({ ...form, course_id: e.target.value })}
                  >
                    <option value="">Select existing</option>
                    {courses.map((course) => (
                      <option key={course.id} value={course.id}>
                        {course.name}
                      </option>
                    ))}
                  </select>
                  <input
                    className="rounded-xl border border-white/10 bg-[#0a1629] px-3 py-2 text-sm text-white"
                    placeholder="Or type new course name"
                    value={form.course_name}
                    onChange={(e) => setForm({ ...form, course_name: e.target.value })}
                  />
                </div>
              </div>

              <div>
                <label className="text-xs uppercase tracking-[0.2em] text-blue-200/70">Topic Name</label>
                <input
                  className="mt-2 w-full rounded-xl border border-white/10 bg-[#0a1629] px-3 py-2 text-sm text-white"
                  value={form.topic_name}
                  onChange={(e) => setForm({ ...form, topic_name: e.target.value })}
                  required
                />
              </div>

              <div>
                <label className="text-xs uppercase tracking-[0.2em] text-blue-200/70">Assignment (Optional)</label>
                <input
                  className="mt-2 w-full rounded-xl border border-white/10 bg-[#0a1629] px-3 py-2 text-sm text-white"
                  value={form.assignment_name}
                  onChange={(e) => setForm({ ...form, assignment_name: e.target.value })}
                />
              </div>

              <div>
                <label className="text-xs uppercase tracking-[0.2em] text-blue-200/70">Date</label>
                <div className="mt-2 grid gap-2">
                  <input
                    type="date"
                    className="w-full rounded-xl border border-white/10 bg-[#0a1629] px-3 py-2 text-sm text-white"
                    value={form.date}
                    onChange={(e) => setForm({ ...form, date: e.target.value })}
                    required
                  />
                  <div className="text-xs text-blue-200/70">
                    Selected: {formatDateDisplay(form.date)}
                  </div>
                </div>
              </div>

              <div>
                <label className="text-xs uppercase tracking-[0.2em] text-blue-200/70">Start Time</label>
                <input
                  type="time"
                  className="mt-2 w-full rounded-xl border border-white/10 bg-[#0a1629] px-3 py-2 text-sm text-white"
                  value={form.start_time}
                  onChange={(e) => setForm({ ...form, start_time: e.target.value })}
                  required
                />
              </div>

              <div className="md:col-span-2">
                <label className="text-xs uppercase tracking-[0.2em] text-blue-200/70">Timezone</label>
                <input
                  className="mt-2 w-full rounded-xl border border-white/10 bg-[#0a1629] px-3 py-2 text-sm text-white"
                  value={form.timezone}
                  onChange={(e) => setForm({ ...form, timezone: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
              <div className="text-xs text-blue-200/70">Duration: 90 minutes</div>
              <div className="flex items-center gap-2">
                {editing ? (
                  <button
                    type="button"
                    className="rounded-full border border-red-500/40 px-4 py-2 text-xs text-red-200 hover:border-red-400"
                    onClick={handleDelete}
                  >
                    Delete
                  </button>
                ) : null}
                <button
                  type="submit"
                  className="rounded-full bg-blue-500 px-5 py-2 text-xs font-semibold text-slate-900"
                >
                  {editing ? 'Update Class' : 'Create Class'}
                </button>
              </div>
            </div>
          </form>
        </div>
      ) : null}
    </div>
  )
}
