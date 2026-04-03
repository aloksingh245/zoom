import { cn } from '../../utils/cn'
import { motion } from 'framer-motion'

export function StatCard({ title, value, icon, trend, color, variants }) {
  const colors = {
    blue: "bg-blue-50 text-blue-600",
    emerald: "bg-emerald-50 text-emerald-600",
    orange: "bg-orange-50 text-orange-600",
  }
  
  return (
    <motion.div 
      variants={variants}
      whileHover={{ y: -4, scale: 1.02 }}
      className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md p-8 rounded-[2.5rem] border border-white dark:border-slate-800 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-none hover:shadow-xl dark:hover:border-slate-700 transition-all group"
    >
      <div className="flex items-center justify-between mb-6">
        <div className={cn("p-4 rounded-[1.2rem] group-hover:scale-110 transition-transform", colors[color])}>{icon}</div>
        <div className="text-right">
           <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] block mb-1">Status</span>
           <span className="text-xs font-black text-emerald-600 bg-emerald-50/80 dark:bg-emerald-900/20 px-3 py-1.5 rounded-xl border border-emerald-100/50 dark:border-emerald-800/50">{trend}</span>
        </div>
      </div>
      <div>
        <p className="text-xs font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest transition-colors">{title}</p>
        <p className="text-5xl font-black text-slate-900 dark:text-slate-100 mt-3 tracking-tighter transition-colors">{value}</p>
      </div>
    </motion.div>
  )
}
