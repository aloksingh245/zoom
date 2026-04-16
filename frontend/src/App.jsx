import { useState, useMemo, useEffect } from 'react'
import { Sidebar } from './components/Layout/Sidebar'
import { TopBar } from './components/Layout/TopBar'
import { Dashboard } from './components/Dashboard/Dashboard'
import { Calendar } from './components/Calendar/Calendar'
import { CourseList } from './components/Courses/CourseList'
import { ClassModal } from './components/Modals/ClassModal'
import { AIAssistant } from './components/AI/AIAssistant'
import { AuthPage } from './components/Auth/AuthPage'
import { AlertCircle, X } from 'lucide-react'
import { useClasses } from './hooks/useClasses'
import { useCourses } from './hooks/useCourses'
import { formatDate, isPastLocal, startOfWeek } from './utils/dateUtils'
import { DEFAULT_TIMEZONE } from './constants'
import { AnimatePresence, motion } from 'framer-motion'

function emptyForm(date) {
  return {
    course_id: '',
    course_name: '',
    topic_name: '',
    assignment_name: '',
    mentor_email: '',
    date: date,
    start_time: '09:00',
    duration_minutes: 90,
    timezone: DEFAULT_TIMEZONE,
  }
}

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light')

  useEffect(() => {
    const root = window.document.documentElement
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    localStorage.setItem('theme', theme)
  }, [theme])

  const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light')

  const handleLogin = (newToken) => {
    localStorage.setItem('token', newToken)
    setToken(newToken)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setToken(null)
  }

  if (!token) {
    return <AuthPage onLogin={handleLogin} theme={theme} />
  }

  return <MainApp theme={theme} toggleTheme={toggleTheme} onLogout={handleLogout} token={token} />
}

function MainApp({ theme, toggleTheme, onLogout, token }) {
  const [view, setView] = useState('dashboard')
  const [searchTerm, setSearchTerm] = useState('')
  const [weekAnchor, setWeekAnchor] = useState(new Date())
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(emptyForm(formatDate(new Date())))
  const [localError, setLocalError] = useState('')

  const currentUser = useMemo(() => {
    if (!token) return null;
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));
      return JSON.parse(jsonPayload);
    } catch (e) {
      console.error("Failed to parse token", e);
      return null;
    }
  }, [token])

  const { 
    classes, 
    loading: classesLoading, 
    error: classesError, 
    addClass, 
    editClass, 
    removeClass,
    syncWithZoom,
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
    setLocalError('')
    setForm({
      course_id: item.course_id,
      course_name: item.course_name,
      topic_name: item.topic_name,
      assignment_name: item.assignment_name || '',
      mentor_email: item.mentor_email || '',
      date: item.date,
      start_time: item.start_time,
      duration_minutes: item.duration_minutes || 90,
      timezone: item.timezone,
    })
    setIsModalOpen(true)
  }

  async function handleAISuggestion(action, autoSave = false) {
    setEditing(null)
    setLocalError('')
    
    // Find course_id if course_name is provided
    let cid = ''
    if (action.course_name) {
      const match = courses.find(c => c.name.toLowerCase() === action.course_name.toLowerCase())
      if (match) cid = match.id
    }

    const newForm = {
      ...emptyForm(action.date || formatDate(new Date())),
      course_id: cid,
      course_name: cid ? '' : (action.course_name || ''),
      topic_name: action.topic_name || '',
      start_time: action.start_time || '09:00',
      duration_minutes: action.duration_minutes || 90,
      mentor_email: action.mentor_email || '',
    }

    setForm(newForm)
    
    if (autoSave) {
      try {
        if (!newForm.course_id?.trim() && !newForm.course_name?.trim()) {
          throw new Error('Course is required.')
        }
        if (!newForm.topic_name?.trim()) {
          throw new Error('Topic name is required.')
        }

        let payload = { ...newForm }
        if (!payload.assignment_name?.trim()) delete payload.assignment_name;
        if (!payload.mentor_email?.trim()) delete payload.mentor_email;

        if (!payload.course_id && payload.course_name) {
          const created = await addCourse({ name: payload.course_name.trim() })
          payload.course_id = created.id
          delete payload.course_name
        }
        
        if (payload.course_id) {
          delete payload.course_name;
        }

        await addClass(payload)
      } catch (err) {
        setLocalError('AI Auto-schedule failed: ' + err.message)
        setIsModalOpen(true) // Open to show error and let user fix
      }
    } else {
      setIsModalOpen(true)
    }
  }

  async function handleSave(e) {
    e.preventDefault()
    setLocalError('')

    if (!form.course_id?.trim() && !form.course_name?.trim()) {
      setLocalError('Please select a course or enter a new course name.')
      return
    }

    if (!form.topic_name?.trim()) {
      setLocalError('Please enter a session topic.')
      return
    }

    if (isPastLocal(form.date, form.start_time, form.timezone)) {
      setLocalError(`Start time must be in the future (${form.timezone}).`)
      return
    }

    try {
      let payload = { ...form }

      // Clean up empty strings for optional fields
      if (!payload.assignment_name?.trim()) delete payload.assignment_name;
      if (!payload.mentor_email?.trim()) delete payload.mentor_email;

      if (!payload.course_id && payload.course_name) {
        const existing = courses.find(c => c.name.toLowerCase() === payload.course_name.trim().toLowerCase())
        if (!existing) {
          const created = await addCourse({ name: payload.course_name.trim() })
          payload.course_id = created.id
        } else {
          payload.course_id = existing.id
        }
        delete payload.course_name
      }

      // If course_id is set, ensure course_name is deleted just in case
      if (payload.course_id) {
        delete payload.course_name;
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

  const pageVariants = {
    initial: { opacity: 0, y: 10, scale: 0.98 },
    in: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] } },
    out: { opacity: 0, y: -10, scale: 0.98, transition: { duration: 0.3, ease: [0.22, 1, 0.36, 1] } }
  }

  return (
    <div className="flex h-screen bg-[#F0F4F8] dark:bg-slate-950 text-slate-900 dark:text-slate-100 overflow-hidden font-sans select-none p-4 gap-4 transition-colors duration-500">
      <Sidebar view={view} setView={setView} theme={theme} />
      
      <main className="flex-1 flex flex-col overflow-hidden bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl rounded-[2.5rem] shadow-sm border border-white/50 dark:border-slate-800/50 relative">
        <TopBar 
          searchTerm={searchTerm} 
          setSearchTerm={setSearchTerm} 
          openCreate={() => openCreate()} 
          syncClasses={syncWithZoom}
          loading={classesLoading}
          theme={theme}
          toggleTheme={toggleTheme}
          onLogout={onLogout}
          currentUser={currentUser}
        />

        <div className="flex-1 overflow-y-auto p-10 relative">
          {error && (
            <motion.div 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mb-8 p-5 bg-red-50/80 backdrop-blur-sm border border-red-100 rounded-[1.5rem] flex items-center gap-4 text-red-700"
            >
              <div className="p-2 bg-red-100 rounded-xl"><AlertCircle size={24} /></div>
              <div>
                <p className="text-sm font-black">Something went wrong</p>
                <p className="text-xs font-medium opacity-80">{error}</p>
              </div>
              <button onClick={() => setLocalError('')} className="ml-auto p-2 hover:bg-red-100 rounded-xl transition-colors"><X size={20} /></button>
            </motion.div>
          )}

          <AnimatePresence mode="wait">
            <motion.div
              key={view}
              variants={pageVariants}
              initial="initial"
              animate="in"
              exit="out"
              className="h-full"
            >
              {view === 'dashboard' && (
                <Dashboard 
                  classes={filteredClasses} 
                  todayClasses={todayClasses}
                  courses={courses}
                  setView={setView}
                  openEdit={openEdit}
                  openCreate={openCreate}
                  currentUser={currentUser}
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
                  currentUser={currentUser}
                />
              )}

              {view === 'courses' && (
                <CourseList courses={courses} />
              )}
            </motion.div>
          </AnimatePresence>
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
        currentUser={currentUser}
      />

      <AIAssistant onSuggestAction={handleAISuggestion} />
    </div>
  )
}
