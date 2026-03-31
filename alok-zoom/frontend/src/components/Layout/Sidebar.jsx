import { 
  Calendar as CalendarIcon, 
  LayoutDashboard, 
  BookOpen
} from 'lucide-react'
import { NavItem } from '../UI/NavItem'
import { motion } from 'framer-motion'

export function Sidebar({ view, setView, theme }) {
  return (
    <aside className="w-[280px] bg-white dark:bg-slate-900 rounded-[2.5rem] flex flex-col shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-none border border-slate-100 dark:border-slate-800 overflow-hidden relative z-10 transition-colors duration-500">
      <div className="p-8 flex items-center gap-4">
        <motion.div 
          whileHover={{ rotate: 10, scale: 1.05 }}
          className="w-12 h-12 bg-blue-600 rounded-[1.2rem] flex items-center justify-center text-white shadow-lg shadow-blue-200/50"
        >
          <CalendarIcon size={24} strokeWidth={2.5} />
        </motion.div>
        <div>
          <span className="font-black text-2xl tracking-tighter text-blue-950 dark:text-slate-100 block leading-none transition-colors">ZOOM</span>
          <span className="text-[10px] font-bold text-blue-500 dark:text-blue-400 uppercase tracking-[0.2em] transition-colors">Scheduler CRM</span>
        </div>
      </div>

      <nav className="flex-1 px-6 py-4 space-y-3 relative z-10">
        <NavItem 
          icon={<LayoutDashboard size={20} />} 
          label="Dashboard" 
          active={view === 'dashboard'} 
          onClick={() => setView('dashboard')} 
        />
        <NavItem 
          icon={<CalendarIcon size={20} />} 
          label="Class Calendar" 
          active={view === 'calendar'} 
          onClick={() => setView('calendar')} 
        />
        <NavItem 
          icon={<BookOpen size={20} />} 
          label="Courses & Batches" 
          active={view === 'courses'} 
          onClick={() => setView('courses')} 
        />
      </nav>

      <div className="p-6 relative z-10">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="p-6 bg-blue-50/50 dark:bg-blue-900/20 rounded-[2rem] border border-blue-100/50 dark:border-blue-800/50 backdrop-blur-sm transition-colors"
        >
          <p className="text-[10px] font-black text-blue-900 dark:text-blue-300 uppercase tracking-[0.2em] mb-3 opacity-50">System Status</p>
          <div className="flex items-center gap-3">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
            <span className="text-xs font-bold text-blue-950 dark:text-blue-100 tracking-wide">Zoom Connected</span>
          </div>
        </motion.div>
      </div>
      
      {/* Decorative background blob */}
      <div className="absolute bottom-0 left-0 w-full h-48 bg-gradient-to-t from-blue-50/50 dark:from-blue-900/10 to-transparent pointer-events-none transition-colors" />
    </aside>
  )
}
