import { useState, useMemo, useEffect } from 'react'
import { Sidebar } from './components/Layout/Sidebar'
import { TopBar } from './components/Layout/TopBar'
import { Dashboard } from './components/Dashboard/Dashboard'
import { Calendar } from './components/Calendar/Calendar'
import { CourseList } from './components/Courses/CourseList'
import { ClassModal } from './components/Modals/ClassModal'
import { AlertCircle, X } from 'lucide-react'
import { useClasses } from './hooks/useClasses'
import { useCourses } from './hooks/useCourses'
import { formatDate, isPastLocal, startOfWeek } from './utils/dateUtils'
import { DEFAULT_TIMEZONE } from './constants'

function emptyForm(date) {
  return {
    course_id: '',
    course_name: '',
    topic_name: '',
    assignment_name: '',
    date: date,
    start_time: '09:00',
    timezone: DEFAULT_TIMEZONE,
  }
}

export default function App() {
  const [view, setView] = useState('dashboard')
  const [searchTerm, setSearchTerm] = useState('')
  const [weekAnchor, setWeekAnchor] = useState(new Date())
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(emptyForm(formatDate(new Date())))
  const [localError, setLocalError] = useState('')

  const { 
    classes, 
    loading: classesLoading, 
    error: classesError, 
    addClass, 
    editClass, 
    removeClass,
    classesByDate 
  } = useClasses()

  const { 
    courses, 
    loading: coursesLoading, 
    addCourse 
  } = useCourses()

  const weekStart = useMemo(() => startOfWeek(weekAnchor), [weekAnchor])

  const filteredClasses = useMemo(() => {
    if (!searchTerm) return classes
    const low = searchTerm.toLowerCase()
    return classes.filter(c => 
      c.course_name.toLowerCase().includes(low) || 
      c.topic_name.toLowerCase().includes(low) ||
      (c.assignment_name && c.assignment_name.toLowerCase().includes(low))
    )
  }, [classes, searchTerm])

  const todayClasses = useMemo(() => 
    classes.filter(c => c.date === formatDate(new Date()))
  , [classes])

  function openCreate(date = formatDate(new Date()), hour = 9) {
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
    setLocalError('')
    
    if (isPastLocal(form.date, form.start_time, form.timezone)) {
      setLocalError('Start time must be in the future (Asia/Kolkata).')
      return
    }

    try {
      let payload = { ...form }
      if (!payload.course_id && payload.course_name) {
        const existing = courses.find(c => c.name.toLowerCase() === payload.course_name.toLowerCase())
        if (!existing) {
          const created = await addCourse({ name: payload.course_name })
          payload.course_id = created.id
        } else {
          payload.course_id = existing.id
        }
        delete payload.course_name
      }

      if (editing) {
        await editClass(editing.id, payload)
      } else {
        await addClass(payload)
      }
      setIsModalOpen(false)
    } catch (err) {
      setLocalError(err.message || 'Failed to save class')
    }
  }

  async function handleDelete() {
    if (!editing) return
    if (!window.confirm('Are you sure you want to delete this class? This will also remove the Zoom meeting.')) return
    
    try {
      await removeClass(editing.id)
      setIsModalOpen(false)
    } catch (err) {
      setLocalError(err.message || 'Failed to delete class')
    }
  }

  const error = classesError || localError

  return (
    <div className="flex h-screen bg-[#F8FAFC] text-slate-900 overflow-hidden font-sans select-none">
      <Sidebar view={view} setView={setView} />
      
      <main className="flex-1 flex flex-col overflow-hidden">
        <TopBar 
          searchTerm={searchTerm} 
          setSearchTerm={setSearchTerm} 
          openCreate={() => openCreate()} 
        />

        <div className="flex-1 overflow-y-auto p-10 bg-slate-50/30">
          {error && (
            <div className="mb-8 p-5 bg-red-50 border border-red-100 rounded-[1.5rem] flex items-center gap-4 text-red-700 animate-in fade-in slide-in-from-top-6 duration-300">
              <div className="p-2 bg-red-100 rounded-xl"><AlertCircle size={24} /></div>
              <div>
                <p className="text-sm font-black">Something went wrong</p>
                <p className="text-xs font-medium opacity-80">{error}</p>
              </div>
              <button onClick={() => setLocalError('')} className="ml-auto p-2 hover:bg-red-100 rounded-xl transition-colors"><X size={20} /></button>
            </div>
          )}

          {view === 'dashboard' && (
            <Dashboard 
              classes={filteredClasses} 
              todayClasses={todayClasses}
              courses={courses}
              setView={setView}
              openEdit={openEdit}
              openCreate={openCreate}
            />
          )}

          {view === 'calendar' && (
            <Calendar 
              weekStart={weekStart}
              weekAnchor={weekAnchor}
              setWeekAnchor={setWeekAnchor}
              classesByDate={classesByDate}
              openCreate={openCreate}
              openEdit={openEdit}
            />
          )}

          {view === 'courses' && (
            <CourseList courses={courses} />
          )}
        </div>
      </main>

      <ClassModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSave}
        onDelete={handleDelete}
        editing={editing}
        form={form}
        setForm={setForm}
        courses={courses}
        loading={classesLoading || coursesLoading}
      />
    </div>
  )
}
