import { ChevronRight } from 'lucide-react'
import { cn } from '../../utils/cn'
import { motion } from 'framer-motion'

export function NavItem({ icon, label, active, onClick }) {
  return (
    <motion.button
      whileHover={{ x: 4 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={cn(
        "w-full flex items-center gap-3 px-5 py-4 rounded-[1.2rem] text-sm font-black transition-colors relative group",
        active 
          ? "text-blue-700 dark:text-blue-400" 
          : "text-slate-400 dark:text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
      )}
    >
      {active && (
        <motion.div
          layoutId="activeNav"
          className="absolute inset-0 bg-blue-50/80 dark:bg-blue-900/30 backdrop-blur-sm border border-blue-100/50 dark:border-blue-800/50 rounded-[1.2rem] shadow-sm z-0"
          initial={false}
          transition={{ type: "spring", stiffness: 400, damping: 30 }}
        />
      )}
      <span className={cn("relative z-10 transition-transform duration-300", active && "scale-110")}>{icon}</span>
      <span className="flex-1 text-left relative z-10">{label}</span>
      
      {active && (
        <motion.div 
          layoutId="activeNavIndicator"
          className="w-1.5 h-6 bg-blue-600 dark:bg-blue-400 rounded-full absolute right-3 z-10 shadow-sm shadow-blue-400/50" 
          initial={false}
          transition={{ type: "spring", stiffness: 400, damping: 30 }}
        />
      )}
      {!active && <ChevronRight size={14} className="opacity-0 group-hover:opacity-100 -translate-x-2 group-hover:translate-x-0 transition-all relative z-10" />}
    </motion.button>
  )
}
