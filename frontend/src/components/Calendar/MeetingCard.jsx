import { Video } from 'lucide-react'
import { cn } from '../../utils/cn'
import { getClassStatus, getEndTime } from '../../utils/dateUtils'

export function MeetingCard({ item, onEdit }) {
  const status = getClassStatus(item)
  const duration = item.duration_minutes || 90
  const endTime = getEndTime(item.start_time, duration)

  const hoverInfo = `Meeting: ${item.topic_name}\nCourse: ${item.course_name}\nTime: ${item.start_time} - ${endTime}\nAssignment: ${item.assignment_name || 'None'}`

  return (
    <div
      title={hoverInfo}
      className={cn(
        "absolute left-1.5 right-1.5 rounded-2xl p-4 border shadow-xl transition-all hover:scale-[1.03] hover:z-10 cursor-pointer overflow-hidden group/item",
        status === 'completed' ? "bg-slate-100 border-slate-200 opacity-60 grayscale-[0.3]" :
        "bg-red-600 border-red-700 shadow-red-200/40 text-white"
      )}
      style={{
        top: `${(parseInt(item.start_time.split(':')[0]) * 96) + (parseInt(item.start_time.split(':')[1]) / 60 * 96)}px`,
        height: `${(duration / 60 * 96)}px`
      }}      onClick={(e) => { e.stopPropagation(); onEdit(item); }}
    >
      <div className="flex items-center justify-between mb-2">
        <span className={cn("text-[10px] font-black uppercase tracking-widest", status === 'completed' ? "text-slate-400" : "text-red-100")}>{item.start_time} - {endTime}</span>
        {status === 'live' && (
          <span className="flex items-center gap-1 text-[9px] font-black text-red-600 bg-white px-2 py-0.5 rounded-full uppercase tracking-tighter shadow-sm animate-bounce">
            <span className="w-1.5 h-1.5 bg-red-600 rounded-full animate-pulse" /> Live Now
          </span>
        )}
      </div>
      <p className={cn("text-[13px] font-black leading-tight mb-1 line-clamp-2", status === 'completed' ? "text-slate-900" : "text-white")}>{item.topic_name}</p>
      <p className={cn("text-[11px] font-bold truncate", status === 'completed' ? "text-slate-500" : "text-red-100")}>Course: {item.course_name}</p>
      
      <div className="absolute bottom-3 right-3 opacity-0 group-hover/item:opacity-100 transition-opacity flex gap-2">
        <div className={cn("p-1.5 rounded-lg shadow-lg", status === 'completed' ? "bg-slate-400 text-white" : "bg-white text-red-600 shadow-red-900/20")}>
          <Video size={14} />
        </div>
      </div>
    </div>
  )
}
