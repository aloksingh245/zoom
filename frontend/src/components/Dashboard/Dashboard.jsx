import { useMemo } from 'react'
import { Calendar as CalendarIcon, Users, CheckCircle2, BookOpen, ExternalLink, MoreVertical } from 'lucide-react'
import { StatCard } from './StatCard'
import { ClassItem } from './ClassItem'
import { dayLabel, formatDate, getClassStatus } from '../../utils/dateUtils'

export function Dashboard({ classes, todayClasses, courses, setView, openEdit, openCreate }) {
  const upcomingClasses = useMemo(() => 
    classes
      .filter(c => getClassStatus(c) === 'upcoming')
      .sort((a, b) => `${a.date}T${a.start_time}`.localeCompare(`${b.date}T${b.start_time}`))
      .slice(0, 5)
  , [classes])

  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Overview</h1>
          <p className="text-slate-500 font-medium mt-1">Welcome back! Here's what's happening today.</p>
        </div>
        <div className="flex bg-white p-1.5 rounded-2xl shadow-sm border border-slate-100">
          <button className="px-4 py-2 text-xs font-bold text-indigo-600 bg-indigo-50 rounded-xl">Today</button>
          <button className="px-4 py-2 text-xs font-bold text-slate-400 hover:text-slate-600 transition-colors">Week</button>
          <button className="px-4 py-2 text-xs font-bold text-slate-400 hover:text-slate-600 transition-colors">Month</button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        <StatCard 
          title="Today's Classes" 
          value={todayClasses.length} 
          icon={<CalendarIcon size={24} className="text-indigo-600" />} 
          trend="+2 New"
          color="indigo"
        />
        <StatCard 
          title="Total Students" 
          value="1,284" 
          icon={<Users size={24} className="text-blue-600" />} 
          trend="+12%"
          color="blue"
        />
        <StatCard 
          title="Avg. Attendance" 
          value="94%" 
          icon={<CheckCircle2 size={24} className="text-emerald-600" />} 
          trend="+3%"
          color="emerald"
        />
        <StatCard 
          title="Total Revenue" 
          value="$14.2k" 
          icon={<BookOpen size={24} className="text-orange-600" />} 
          trend="+8%"
          color="orange"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
        <section className="lg:col-span-2 bg-white rounded-[2.5rem] border border-slate-100 p-8 shadow-xl shadow-slate-200/40">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h3 className="font-black text-xl text-slate-900 tracking-tight">Today's Schedule</h3>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-1">{dayLabel(new Date())}</p>
            </div>
            <button className="bg-indigo-50 text-indigo-700 px-4 py-2 rounded-xl text-xs font-bold hover:bg-indigo-100 transition-all flex items-center gap-2" onClick={() => setView('calendar')}>
              Full Calendar
              <ExternalLink size={14} />
            </button>
          </div>
          <div className="space-y-4">
            {todayClasses.length > 0 ? todayClasses.map(c => (
              <ClassItem key={c.id} item={c} onEdit={openEdit} />
            )) : (
              <div className="text-center py-20 bg-slate-50/50 rounded-[2rem] border-2 border-dashed border-slate-100">
                <CalendarIcon size={64} className="mx-auto mb-4 text-slate-200" />
                <p className="text-slate-400 font-bold">No classes scheduled for today.</p>
                <button onClick={() => openCreate()} className="mt-4 text-indigo-600 font-black text-sm hover:underline underline-offset-4">Schedule one now</button>
              </div>
            )}
          </div>
        </section>

        <section className="bg-white rounded-[2.5rem] border border-slate-100 p-8 shadow-xl shadow-slate-200/40">
          <div className="flex items-center justify-between mb-8">
            <h3 className="font-black text-xl text-slate-900 tracking-tight">Upcoming</h3>
            <div className="p-2 bg-slate-50 rounded-xl text-slate-400"><MoreVertical size={20} /></div>
          </div>
          <div className="space-y-8">
            {upcomingClasses.map(c => (
              <div key={c.id} className="flex gap-5 group cursor-pointer" onClick={() => openEdit(c)}>
                <div className="flex-shrink-0 w-14 h-14 bg-slate-50 rounded-2xl flex flex-col items-center justify-center border border-slate-100 group-hover:bg-indigo-50 group-hover:border-indigo-100 transition-all">
                  <span className="text-[10px] uppercase font-black text-slate-400 group-hover:text-indigo-400 tracking-tighter">{new Date(c.date).toLocaleDateString('en-US', { month: 'short' })}</span>
                  <span className="text-lg font-black text-slate-800 group-hover:text-indigo-950">{new Date(c.date).getDate()}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-bold text-slate-800 truncate group-hover:text-red-600 transition-colors">{c.topic_name}</h4>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-xs font-bold text-slate-400 flex items-center gap-1">
                      <Clock size={12} /> {c.start_time}
                    </span>
                    <span className="w-1 h-1 bg-slate-200 rounded-full"></span>
                    <span className="text-xs font-bold text-red-500/70 truncate">Course: {c.course_name}</span>
                  </div>
                </div>
              </div>
            ))}
            {upcomingClasses.length === 0 && (
              <div className="text-center py-20">
                 <p className="text-slate-300 font-bold">No upcoming classes</p>
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  )
}
