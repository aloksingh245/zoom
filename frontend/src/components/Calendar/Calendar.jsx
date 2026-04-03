import { ChevronLeft, ChevronRight, Clock, Plus } from 'lucide-react'
import { HOURS, DEFAULT_TIMEZONE } from '../../constants'
import { formatDate, dayLabel, formatHour } from '../../utils/dateUtils'
import { cn } from '../../utils/cn'
import { MeetingCard } from './MeetingCard'
import { motion } from 'framer-motion'

export function Calendar({ weekStart, weekAnchor, setWeekAnchor, classesByDate, openCreate, openEdit }) {
  const weekDays = Array.from({ length: 7 }, (_, idx) => {
    const d = new Date(weekStart)
    d.setDate(weekStart.getDate() + idx)
    return d
  })

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl rounded-[3rem] border border-white dark:border-slate-800 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-none overflow-hidden flex flex-col h-full transition-colors duration-500"
    >
      <div className="p-8 border-b border-slate-100/50 dark:border-slate-800/50 flex items-center justify-between bg-white/50 dark:bg-slate-900/50 sticky top-0 z-20 transition-colors">
        <div className="flex items-center gap-8">
          <div>
            <h2 className="text-3xl font-black text-slate-900 dark:text-slate-100 tracking-tight transition-colors">{new Date(weekStart).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</h2>
            <p className="text-sm font-bold text-slate-400 dark:text-slate-500 mt-1 transition-colors">Viewing Week: {dayLabel(weekStart)} - {dayLabel(new Date(weekStart.getTime() + 6 * 24 * 60 * 60 * 1000))}</p>
          </div>
          <div className="flex bg-slate-50/80 dark:bg-slate-800/80 p-1.5 rounded-2xl border border-slate-100/50 dark:border-slate-700/50 backdrop-blur-sm transition-colors">
            <button onClick={() => setWeekAnchor(new Date(weekAnchor.setDate(weekAnchor.getDate() - 7)))} className="p-2.5 hover:bg-white dark:hover:bg-slate-700 hover:shadow-sm rounded-xl transition-all text-slate-600 dark:text-slate-400 active:scale-95"><ChevronLeft size={20} /></button>
            <button onClick={() => setWeekAnchor(new Date())} className="px-6 py-2.5 text-xs font-black text-slate-700 dark:text-slate-200 hover:bg-white dark:hover:bg-slate-700 hover:shadow-sm rounded-xl transition-all uppercase tracking-widest active:scale-95">Today</button>
            <button onClick={() => setWeekAnchor(new Date(weekAnchor.setDate(weekAnchor.getDate() + 7)))} className="p-2.5 hover:bg-white dark:hover:bg-slate-700 hover:shadow-sm rounded-xl transition-all text-slate-600 dark:text-slate-400 active:scale-95"><ChevronRight size={20} /></button>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="px-5 py-3 bg-blue-50/80 dark:bg-blue-900/20 rounded-2xl border border-blue-100/50 dark:border-blue-800/50 transition-colors">
            <span className="text-[10px] font-black text-blue-700 dark:text-blue-400 uppercase tracking-widest flex items-center gap-2">
               <Clock size={14} /> {DEFAULT_TIMEZONE}
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-8 divide-x divide-slate-100/50 dark:divide-slate-800/50 bg-slate-50/30 dark:bg-slate-900/30 transition-colors">
        <div className="bg-transparent" />
        {weekDays.map(day => (
          <div key={day.toString()} className={cn("p-6 text-center border-b-2 border-transparent transition-all relative overflow-hidden", formatDate(day) === formatDate(new Date()) && "border-blue-600")}>
            {formatDate(day) === formatDate(new Date()) && <div className="absolute inset-0 bg-gradient-to-b from-blue-50/50 dark:from-blue-900/20 to-transparent -z-10" />}
            <p className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] transition-colors">{day.toLocaleDateString('en-US', { weekday: 'short' })}</p>
            <p className={cn("text-2xl font-black mt-2 inline-flex w-12 h-12 items-center justify-center rounded-[1.2rem] z-10 relative transition-all", formatDate(day) === formatDate(new Date()) ? "bg-blue-600 text-white shadow-lg shadow-blue-200/50" : "text-slate-800 dark:text-slate-200")}>
              {day.getDate()}
            </p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-8 divide-x divide-slate-100/50 dark:divide-slate-800/50 flex-1 overflow-y-auto bg-slate-50/10 dark:bg-slate-950/10 transition-colors">
        <div className="flex flex-col">
          {HOURS.map(h => (
            <div key={h} className="h-24 border-b border-slate-100/50 dark:border-slate-800/50 p-4 text-[10px] font-black text-slate-300 dark:text-slate-600 text-right pr-6 tracking-[0.2em] uppercase transition-colors">
              {formatHour(h)}
            </div>
          ))}
        </div>

        {weekDays.map(day => {
          const dateStr = formatDate(day)
          const dayClasses = classesByDate.get(dateStr) || []
          const isToday = dateStr === formatDate(new Date())

          return (
            <div key={dateStr} className={cn("relative group transition-colors", isToday && "bg-gradient-to-b from-blue-50/10 dark:from-blue-900/10 to-transparent")}>
              {HOURS.map(h => (
                <div 
                  key={h} 
                  className="h-24 border-b border-slate-100/50 dark:border-slate-800/50 cursor-pointer hover:bg-blue-50/30 dark:hover:bg-blue-900/20 transition-colors relative group/slot"
                  onClick={() => openCreate(dateStr, h)}
                >
                   <div className="absolute inset-0 opacity-0 group-hover/slot:opacity-100 flex items-center justify-center pointer-events-none scale-90 group-hover/slot:scale-100 transition-all duration-300">
                      <div className="w-8 h-8 rounded-full bg-blue-100/50 dark:bg-blue-900/50 flex items-center justify-center text-blue-500 dark:text-blue-400">
                        <Plus size={16} strokeWidth={3} />
                      </div>
                   </div>
                </div>
              ))}
              
              {dayClasses.map(c => (
                <MeetingCard key={c.id} item={c} onEdit={openEdit} />
              ))}
            </div>
          )
        })}
      </div>
    </motion.div>
  )
}
