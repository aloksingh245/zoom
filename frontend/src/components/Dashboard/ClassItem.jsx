import { Video, Clock, Edit3 } from 'lucide-react'
import { cn } from '../../utils/cn'
import { getClassStatus } from '../../utils/dateUtils'
import { motion } from 'framer-motion'

export function ClassItem({ item, onEdit, variants }) {
  const status = getClassStatus(item)
  
  return (
    <motion.div 
      variants={variants}
      whileHover={{ scale: 1.01 }}
      className="group flex items-center gap-6 p-6 rounded-[2rem] border border-white dark:border-slate-800 bg-white/60 dark:bg-slate-800/60 hover:bg-white dark:hover:bg-slate-800 shadow-[0_4px_20px_rgb(0,0,0,0.02)] hover:shadow-xl hover:shadow-slate-200/40 transition-all duration-500"
    >
      <div className={cn(
        "flex-shrink-0 w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-500 group-hover:rotate-6",
        status === 'live' || status === 'upcoming' 
          ? "bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-900/40 text-red-600 dark:text-red-400 shadow-inner" 
          : "bg-slate-50 dark:bg-slate-900 text-slate-400 dark:text-slate-500 opacity-60"
      )}>
        {status === 'live' ? <Video size={32} className="animate-pulse" strokeWidth={2.5} /> : <Clock size={32} strokeWidth={2.5} />}
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-3 mb-1.5">
          <h4 className="font-black text-xl text-slate-900 dark:text-slate-100 truncate tracking-tight transition-colors">{item.topic_name}</h4>
          {status === 'live' && (
            <span className="text-[10px] font-black uppercase text-red-600 dark:text-red-400 bg-red-50/80 dark:bg-red-900/30 px-2.5 py-1 rounded-full tracking-[0.15em] border border-red-100/50 dark:border-red-900/50 animate-bounce">Live Now</span>
          )}
        </div>
        <div className="flex items-center gap-3">
           <p className="text-sm font-bold text-slate-500 dark:text-slate-400 truncate transition-colors">Course: <span className="text-slate-700 dark:text-slate-200">{item.course_name}</span></p>
           <span className="w-1.5 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full transition-colors"></span>
           <p className="text-sm font-black text-red-600 dark:text-red-400 transition-colors">{item.start_time}</p>
        </div>
      </div>

      <div className="flex items-center gap-3 opacity-0 group-hover:opacity-100 transition-all duration-300 translate-x-4 group-hover:translate-x-0">
        <button 
          onClick={() => onEdit(item)} 
          className="p-3.5 text-slate-400 dark:text-slate-500 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-[1.2rem] transition-all active:scale-90"
          title="Edit Details"
        >
          <Edit3 size={20} strokeWidth={2.5} />
        </button>
        <a 
          href={item.zoom_join_url} 
          target="_blank" 
          rel="noreferrer"
          className="p-3.5 bg-blue-600 text-white rounded-[1.2rem] hover:bg-blue-700 shadow-lg shadow-blue-200/50 dark:shadow-none transition-all active:scale-90 flex items-center gap-2"
          title="Join Session"
        >
          <Video size={20} strokeWidth={2.5} />
          <span className="text-sm font-black hidden lg:block">Join</span>
        </a>
      </div>
    </motion.div>
  )
}
