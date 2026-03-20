import { ChevronLeft, ChevronRight, Clock, Plus } from 'lucide-react'
import { HOURS, DEFAULT_TIMEZONE } from '../../constants'
import { formatDate, dayLabel, formatHour } from '../../utils/dateUtils'
import { cn } from '../../utils/cn'
import { MeetingCard } from './MeetingCard'

export function Calendar({ weekStart, weekAnchor, setWeekAnchor, classesByDate, openCreate, openEdit }) {
  const weekDays = Array.from({ length: 7 }, (_, idx) => {
    const d = new Date(weekStart)
    d.setDate(weekStart.getDate() + idx)
    return d
  })

  return (
    <div className="bg-white rounded-[2.5rem] border border-slate-100 shadow-2xl shadow-slate-200/40 overflow-hidden animate-in fade-in duration-700">
      <div className="p-10 border-b border-slate-50 flex items-center justify-between bg-white sticky top-0 z-20">
        <div className="flex items-center gap-8">
          <div>
            <h2 className="text-3xl font-black text-slate-900 tracking-tight">{new Date(weekStart).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</h2>
            <p className="text-sm font-bold text-slate-400 mt-1">Viewing Week: {dayLabel(weekStart)} - {dayLabel(new Date(weekStart.getTime() + 6 * 24 * 60 * 60 * 1000))}</p>
          </div>
          <div className="flex bg-slate-50 p-1.5 rounded-2xl border border-slate-100">
            <button onClick={() => setWeekAnchor(new Date(weekAnchor.setDate(weekAnchor.getDate() - 7)))} className="p-2.5 hover:bg-white hover:shadow-sm rounded-xl transition-all text-slate-600"><ChevronLeft size={20} /></button>
            <button onClick={() => setWeekAnchor(new Date())} className="px-6 py-2.5 text-xs font-black text-slate-700 hover:bg-white hover:shadow-sm rounded-xl transition-all uppercase tracking-widest">Today</button>
            <button onClick={() => setWeekAnchor(new Date(weekAnchor.setDate(weekAnchor.getDate() + 7)))} className="p-2.5 hover:bg-white hover:shadow-sm rounded-xl transition-all text-slate-600"><ChevronRight size={20} /></button>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="px-4 py-2 bg-indigo-50 rounded-xl border border-indigo-100">
            <span className="text-[10px] font-black text-indigo-700 uppercase tracking-widest flex items-center gap-2">
               <Clock size={12} /> {DEFAULT_TIMEZONE}
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-8 divide-x divide-slate-50 bg-slate-50/30">
        <div className="bg-white" />
        {weekDays.map(day => (
          <div key={day.toString()} className={cn("p-6 text-center bg-white border-b-2 border-transparent transition-all", formatDate(day) === formatDate(new Date()) && "bg-indigo-50/20 border-indigo-600")}>
            <p className="text-xs font-black text-slate-400 uppercase tracking-[0.2em]">{day.toLocaleDateString('en-US', { weekday: 'short' })}</p>
            <p className={cn("text-2xl font-black mt-2 inline-flex w-12 h-12 items-center justify-center rounded-2xl", formatDate(day) === formatDate(new Date()) ? "bg-indigo-600 text-white shadow-lg shadow-indigo-100" : "text-slate-800")}>
              {day.getDate()}
            </p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-8 divide-x divide-slate-50 h-[700px] overflow-y-auto">
        <div className="flex flex-col bg-white">
          {HOURS.map(h => (
            <div key={h} className="h-24 border-b border-slate-50/50 p-4 text-[10px] font-black text-slate-300 text-right pr-6 tracking-widest uppercase">
              {formatHour(h)}
            </div>
          ))}
        </div>

        {weekDays.map(day => {
          const dateStr = formatDate(day)
          const dayClasses = classesByDate.get(dateStr) || []
          const isToday = dateStr === formatDate(new Date())

          return (
            <div key={dateStr} className={cn("relative group bg-white/50", isToday && "bg-indigo-50/10")}>
              {HOURS.map(h => (
                <div 
                  key={h} 
                  className="h-24 border-b border-slate-50/50 cursor-pointer hover:bg-white transition-colors relative"
                  onClick={() => openCreate(dateStr, h)}
                >
                   <div className="absolute inset-0 opacity-0 group-hover:opacity-100 flex items-center justify-center pointer-events-none">
                      <Plus size={16} className="text-indigo-200" />
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
    </div>
  )
}
