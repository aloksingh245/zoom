import { Video } from 'lucide-react'
import { cn } from '../../utils/cn'
import { getClassStatus, getEndTime } from '../../utils/dateUtils'
import { motion } from 'framer-motion'

export function MeetingCard({ item, onEdit }) {
  const status = getClassStatus(item)
  const duration = item.duration_minutes || 90
  const endTime = getEndTime(item.start_time, duration)

  const hoverInfo = `Meeting: ${item.topic_name}\nCourse: ${item.course_name}\nTime: ${item.start_time} - ${endTime}\nAssignment: ${item.assignment_name || 'None'}`

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02, zIndex: 10 }}
      title={hoverInfo}
      className={cn(
        "absolute left-1.5 right-1.5 rounded-2xl p-4 border shadow-md transition-shadow cursor-pointer overflow-hidden group/item backdrop-blur-md",
        status === 'completed' ? "bg-slate-50/80 dark:bg-slate-800/80 border-slate-200/60 dark:border-slate-700/60 opacity-70 grayscale-[0.2] hover:shadow-lg" :
        "bg-gradient-to-br from-red-600 to-red-700 border-red-500 shadow-red-500/30 text-white hover:shadow-xl hover:shadow-red-500/40"
      )}
      style={{
        top: `${(parseInt(item.start_time.split(':')[0]) * 96) + (parseInt(item.start_time.split(':')[1]) / 60 * 96)}px`,
        height: `${(duration / 60 * 96)}px`
      }}      
      onClick={(e) => { e.stopPropagation(); onEdit(item); }}
    >
      <div className="flex items-center justify-between mb-2">
        <span className={cn("text-[10px] font-black uppercase tracking-widest", status === 'completed' ? "text-slate-500 dark:text-slate-400" : "text-red-100")}>{item.start_time} - {endTime}</span>
        {status === 'live' && (
          <span className="flex items-center gap-1.5 text-[9px] font-black text-red-600 bg-white px-2.5 py-0.5 rounded-full uppercase tracking-tighter shadow-sm animate-pulse">
            <span className="w-1.5 h-1.5 bg-red-600 rounded-full" /> Live
          </span>
        )}
      </div>
      <p className={cn("text-[13px] font-black leading-tight mb-1 line-clamp-2", status === 'completed' ? "text-slate-800 dark:text-slate-100" : "text-white")}>{item.topic_name}</p>
      <p className={cn("text-[11px] font-bold truncate opacity-90", status === 'completed' ? "text-slate-500 dark:text-slate-400" : "text-red-100")}>{item.course_name}</p>
      
      <div className="absolute bottom-3 right-3 opacity-0 group-hover/item:opacity-100 transition-opacity flex gap-2">
        <div className={cn("p-2 rounded-xl shadow-lg backdrop-blur-md", status === 'completed' ? "bg-white/80 dark:bg-slate-700 text-slate-600 dark:text-slate-200" : "bg-white/20 text-white border border-white/30")}>
          <Video size={14} strokeWidth={2.5} />
        </div>
      </div>
    </motion.div>
  )
}
