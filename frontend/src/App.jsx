import { useState, useMemo, useEffect } from 'react'
import { Sidebar } from './components/Layout/Sidebar'
import { TopBar } from './components/Layout/TopBar'
import { Dashboard } from './components/Dashboard/Dashboard'
import { Calendar } from './components/Calendar/Calendar'
import { CourseList } from './components/Courses/CourseList'
import { ClassModal } from './components/Modals/ClassModal'
import { AlertCircle, X, CheckCircle } from 'lucide-react'
import { useClasses } from './hooks/useClasses'
import { useCourses } from './hooks/useCourses'
import { useUsersStats } from './hooks/useUsersStats'
import { formatDate, isPastLocal, startOfWeek } from './utils/dateUtils'
import { DEFAULT_TIMEZONE } from './constants'
import { useAuth } from './context/AuthContext'
import { AuthPage } from './components/Auth/AuthPage'
import { VerifyEmail } from './components/Auth/VerifyEmail'
import { ResetPassword } from './components/Auth/ResetPassword'
import { SettingsPanel } from './components/Settings/SettingsPanel'
import { ChatBubble } from './components/Agent/ChatBubble'



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
  const { user, loading, logout } = useAuth()
  const [view, setView] = useState('dashboard')
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('zoom_scheduler_theme') || 'light'
  })

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
      document.body.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
      document.body.classList.remove('dark')
    }
    localStorage.setItem('zoom_scheduler_theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
  }
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
    setError: setClassesError,
    addClass, 
    editClass, 
    removeClass,
    syncWithZoom,
    syncWithCalendar,
    calendarConnected,
    connectCalendar,
    classesByDate 
  } = useClasses(!!user)

  const [success, setSuccess] = useState('')

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    if (params.get('gcal_success') === 'true') {
      setSuccess('Google Calendar was successfully connected! You can now sync classes.')
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }, [])

  const { 
    courses, 
    loading: coursesLoading, 
    addCourse 
  } = useCourses(!!user)

  const {
    stats: userStats
  } = useUsersStats(!!user)

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
    if (user?.role !== 'admin') return
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
    setClassesError(null)
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

  async function handleSave(e) {
    e.preventDefault()
    if (user?.role !== 'admin') {
      setLocalError('Unauthorized action. Only administrators can schedule sessions.')
      return
    }
    setLocalError('')
    setClassesError(null)

    if (isPastLocal(form.date, form.start_time, form.timezone)) {
      setLocalError(`Start time must be in the future (${form.timezone}).`)
      return
    }

    try {
      if (editing) {
        await editClass(editing.id, form)
      } else {
        await addClass(form)
      }
      setIsModalOpen(false)
    } catch (err) {
      setLocalError(err.message || 'Failed to save class')
    }
  }

  async function handleDelete() {
    if (user?.role !== 'admin') {
      setLocalError('Unauthorized action. Only administrators can delete sessions.')
      return
    }
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

  const isVerifyEmailPage = window.location.pathname === '/verify-email'
  const isResetPasswordPage = window.location.pathname === '/reset-password'

  if (isVerifyEmailPage) {
    return <VerifyEmail />
  }

  if (isResetPasswordPage) {
    return <ResetPassword />
  }

  if (loading) {
    return (
      <div className="flex h-screen bg-[#0b0f19] items-center justify-center font-sans">
        <div className="space-y-4 text-center animate-in fade-in duration-300">
          <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-slate-400 text-sm font-bold tracking-wider">Verifying session...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return <AuthPage />
  }

  return (
    <div className="flex h-screen bg-[#F8FAFC] text-slate-900 overflow-hidden font-sans select-none">
      <Sidebar 
        view={view} 
        setView={setView} 
        user={user} 
        onLogout={logout} 
        onSyncCalendar={syncWithCalendar}
        calendarConnected={calendarConnected}
        onConnectCalendar={connectCalendar}
      />

      <main className="flex-1 flex flex-col overflow-hidden">
        <TopBar 
          searchTerm={searchTerm} 
          setSearchTerm={setSearchTerm} 
          openCreate={() => openCreate()} 
          syncClasses={syncWithZoom}
          syncCalendar={syncWithCalendar}
          loading={classesLoading}
          user={user}
          theme={theme}
          toggleTheme={toggleTheme}
        />

        <div className="flex-1 overflow-y-auto p-10 bg-slate-50/30">
          {success && (
            <div className="mb-8 p-5 bg-emerald-50 border border-emerald-100 rounded-[1.5rem] flex items-center gap-4 text-emerald-700 animate-in fade-in slide-in-from-top-6 duration-300">
              <div className="p-2 bg-emerald-100 rounded-xl"><CheckCircle size={24} /></div>
              <div>
                <p className="text-sm font-black">Success</p>
                <p className="text-xs font-medium opacity-80">{success}</p>
              </div>
              <button onClick={() => setSuccess('')} className="ml-auto p-2 hover:bg-emerald-100 rounded-xl transition-colors"><X size={20} /></button>
            </div>
          )}

          {error && (
            <div className="mb-8 p-5 bg-red-50 border border-red-100 rounded-[1.5rem] flex items-center gap-4 text-red-700 animate-in fade-in slide-in-from-top-6 duration-300">
              <div className="p-2 bg-red-100 rounded-xl"><AlertCircle size={24} /></div>
              <div>
                <p className="text-sm font-black">Something went wrong</p>
                <p className="text-xs font-medium opacity-80">{error}</p>
              </div>
              <button onClick={() => { setLocalError(''); setClassesError(null); }} className="ml-auto p-2 hover:bg-red-100 rounded-xl transition-colors"><X size={20} /></button>
            </div>
          )}

          {view === 'dashboard' && (
            <Dashboard 
              classes={filteredClasses} 
              todayClasses={todayClasses}
              courses={courses}
              userStats={userStats}
              setView={setView}
              openEdit={openEdit}
              openCreate={openCreate}
              userRole={user?.role}
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
              userRole={user?.role}
            />
          )}

          {view === 'courses' && (
            <CourseList courses={courses} />
          )}

          {view === 'settings' && (
            <SettingsPanel />
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
        userRole={user?.role}
      />
      <ChatBubble user={user} />
    </div>
  )
}
