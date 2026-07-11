import { Video, Clock, Edit3, Eye } from 'lucide-react'
import { cn } from '../../utils/cn'
import { getClassStatus } from '../../utils/dateUtils'

export function ClassItem({ item, onEdit, userRole = 'admin' }) {
  const status = getClassStatus(item)
  const isReadOnly = userRole !== 'admin'
  
  return (
    <div className="group flex items-center gap-6 p-6 rounded-[2rem] border border-slate-50 bg-white hover:border-indigo-100 hover:shadow-lg hover:shadow-indigo-100/10 transition-all">
      <div className={cn(
        "flex-shrink-0 w-16 h-16 rounded-2xl flex items-center justify-center transition-all group-hover:rotate-3",
        status === 'live' || status === 'upcoming' ? "bg-indigo-50 text-indigo-500 ring-4 ring-indigo-500/5" :
        "bg-slate-50 text-slate-400 opacity-60"
      )}>
        {status === 'live' ? <Video size={32} className="animate-pulse" /> : <Clock size={32} />}
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-3 mb-1">
          <h4 className="font-black text-lg text-slate-900 truncate tracking-tight">{item.topic_name}</h4>
          {status === 'live' && (
            <span className="text-[9px] font-black uppercase text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full tracking-[0.15em] border border-indigo-100 animate-bounce">Live Now</span>
          )}
        </div>
        <div className="flex items-center gap-3">
           <p className="text-sm font-bold text-slate-400 truncate">Course: {item.course_name}</p>
           <span className="w-1 h-1 bg-slate-200 rounded-full"></span>
           <p className="text-sm font-black text-indigo-600/70">{item.start_time}</p>
        </div>
      </div>

      <div className="flex items-center gap-3 opacity-0 group-hover:opacity-100 transition-all translate-x-4 group-hover:translate-x-0">
        <button 
          onClick={() => onEdit(item)} 
          className="p-3 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-xl transition-all active:scale-90 cursor-pointer"
          title={isReadOnly ? "View Details" : "Edit Details"}
        >
          {isReadOnly ? <Eye size={20} /> : <Edit3 size={20} />}
        </button>
        {item.zoom_join_url && (
          <button 
            onClick={() => window.open(item.zoom_join_url, '_blank')}
            className="p-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 shadow-xl shadow-indigo-200 transition-all active:scale-90 cursor-pointer"
            title="Join Session"
          >
            <Video size={20} />
          </button>
        )}
      </div>
    </div>
  )
}
