import { useMemo } from 'react'
import { Calendar as CalendarIcon, ExternalLink, MoreVertical, Clock } from 'lucide-react'
import { StatCard } from './StatCard'
import { ClassItem } from './ClassItem'
import { dayLabel, formatDate, getClassStatus } from '../../utils/dateUtils'
import { motion } from 'framer-motion'

export function Dashboard({ classes, todayClasses, courses, setView, openEdit, openCreate }) {
  const upcomingClasses = useMemo(() => 
    classes
      .filter(c => getClassStatus(c) === 'upcoming')
      .sort((a, b) => `${a.date}T${a.start_time}`.localeCompare(`${b.date}T${b.start_time}`))
      .slice(0, 5)
  , [classes])

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
  }

  return (
    <motion.div 
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="space-y-10"
    >
      <motion.div variants={itemVariants} className="flex items-end justify-between">
        <div>
          <h1 className="text-4xl font-black text-slate-900 dark:text-slate-100 tracking-tight transition-colors">Overview</h1>
          <p className="text-slate-500 dark:text-slate-400 font-medium mt-2 transition-colors">Welcome back! Here's what's happening today.</p>
        </div>
      </motion.div>

      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        <StatCard 
          title="Today's Classes" 
          value={todayClasses.length} 
          icon={<CalendarIcon size={24} className="text-blue-600 dark:text-blue-400" />} 
          trend="Real-time"
          color="blue"
        />
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
        <motion.section variants={itemVariants} className="lg:col-span-2 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md rounded-[2.5rem] border border-white dark:border-slate-800 p-8 shadow-xl shadow-slate-200/20 dark:shadow-none transition-colors">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h3 className="font-black text-2xl text-slate-900 dark:text-slate-100 tracking-tight transition-colors">Today's Schedule</h3>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-1 transition-colors">{dayLabel(new Date())}</p>
            </div>
            <button className="bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 px-5 py-2.5 rounded-xl text-xs font-bold hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-all flex items-center gap-2" onClick={() => setView('calendar')}>
              Full Calendar
              <ExternalLink size={14} />
            </button>
          </div>
          <motion.div 
            variants={containerVariants}
            initial="hidden"
            animate="show"
            className="space-y-4"
          >
            {todayClasses.length > 0 ? todayClasses.map(c => (
              <ClassItem key={c.id} item={c} onEdit={openEdit} variants={itemVariants} />
            )) : (
              <div className="text-center py-20 bg-slate-50/50 rounded-[2rem] border-2 border-dashed border-slate-100">
                <CalendarIcon size={64} className="mx-auto mb-4 text-slate-200" />
                <p className="text-slate-400 font-bold">No classes scheduled for today.</p>
                <button onClick={() => openCreate()} className="mt-4 text-blue-600 font-black text-sm hover:underline underline-offset-4">Schedule one now</button>
              </div>
            )}
          </motion.div>
        </motion.section>

        <motion.section variants={itemVariants} className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md rounded-[2.5rem] border border-white dark:border-slate-800 p-8 shadow-xl shadow-slate-200/20 dark:shadow-none transition-colors">
          <div className="flex items-center justify-between mb-8">
            <h3 className="font-black text-2xl text-slate-900 dark:text-slate-100 tracking-tight transition-colors">Upcoming</h3>
            <div className="p-2 bg-slate-50 dark:bg-slate-800 rounded-xl text-slate-400 dark:text-slate-500 transition-colors"><MoreVertical size={20} /></div>
          </div>
          <div className="space-y-8">
            {upcomingClasses.map((c, i) => (
              <motion.div 
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1, type: "spring", stiffness: 300, damping: 24 }}
                key={c.id} 
                className="flex gap-5 group cursor-pointer" 
                onClick={() => openEdit(c)}
              >
                <div className="flex-shrink-0 w-16 h-16 bg-slate-50 dark:bg-slate-800 rounded-2xl flex flex-col items-center justify-center border border-slate-100 dark:border-slate-700 group-hover:bg-blue-50 dark:group-hover:bg-blue-900/30 group-hover:border-blue-200 dark:group-hover:border-blue-800 transition-all group-hover:scale-105">
                  <span className="text-[10px] uppercase font-black text-slate-400 dark:text-slate-500 group-hover:text-blue-500 dark:group-hover:text-blue-400 tracking-tighter transition-colors">{new Date(c.date).toLocaleDateString('en-US', { month: 'short' })}</span>
                  <span className="text-xl font-black text-slate-800 dark:text-slate-100 group-hover:text-blue-950 dark:group-hover:text-blue-50 transition-colors">{new Date(c.date).getDate()}</span>
                </div>
                <div className="flex-1 min-w-0 flex flex-col justify-center">
                  <h4 className="font-bold text-slate-800 dark:text-slate-200 truncate group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">{c.topic_name}</h4>
                  <div className="flex items-center gap-3 mt-1.5">
                    <span className="text-xs font-bold text-slate-400 dark:text-slate-500 flex items-center gap-1 transition-colors">
                      <Clock size={12} /> {c.start_time}
                    </span>
                    <span className="w-1 h-1 bg-slate-200 dark:bg-slate-700 rounded-full transition-colors"></span>
                    <span className="text-xs font-bold text-slate-400 dark:text-slate-500 truncate transition-colors">Course: {c.course_name}</span>
                  </div>
                </div>
              </motion.div>
            ))}
            {upcomingClasses.length === 0 && (
              <div className="text-center py-20">
                 <p className="text-slate-300 font-bold">No upcoming classes</p>
              </div>
            )}
          </div>
        </motion.section>
      </div>
    </motion.div>
  )
}
