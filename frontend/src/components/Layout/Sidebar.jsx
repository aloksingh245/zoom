import { 
  Calendar as CalendarIcon, 
  LayoutDashboard, 
  BookOpen, 
  Users, 
  Settings, 
  LogOut, 
  Bell 
} from 'lucide-react'
import { NavItem } from '../UI/NavItem'

export function Sidebar({ view, setView }) {
  return (
    <aside className="w-72 border-r border-slate-200 bg-white flex flex-col shadow-sm">
      <div className="p-8 flex items-center gap-3">
        <div className="w-12 h-12 bg-indigo-600 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-indigo-100 rotate-3">
          <CalendarIcon size={28} />
        </div>
        <div>
          <span className="font-black text-2xl tracking-tighter text-indigo-950 block leading-none">ZOOM</span>
          <span className="text-[10px] font-bold text-indigo-500 uppercase tracking-[0.2em]">Scheduler CRM</span>
        </div>
      </div>

      <nav className="flex-1 px-6 py-4 space-y-2">
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
        <div className="pt-4 mt-4 border-t border-slate-100">
          <p className="px-4 text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">Management</p>
          <NavItem 
            icon={<Users size={20} />} 
            label="Students" 
            active={false} 
            onClick={() => {}} 
          />
          <NavItem 
            icon={<Settings size={20} />} 
            label="Settings" 
            active={false} 
            onClick={() => {}} 
          />
        </div>
      </nav>

      <div className="p-6">
        <div className="p-5 bg-gradient-to-br from-indigo-600 to-indigo-800 rounded-[2rem] text-white shadow-lg shadow-indigo-200">
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-white/20 rounded-xl"><Bell size={18} /></div>
            <span className="text-[10px] font-bold bg-white/20 px-2 py-1 rounded-full uppercase">Update</span>
          </div>
          <p className="text-sm font-bold leading-tight">Sync your calendar with Google Calendar</p>
          <button className="mt-4 w-full py-2 bg-white text-indigo-700 text-xs font-bold rounded-xl hover:bg-indigo-50 transition-colors">Connect Now</button>
        </div>
        
        <button className="mt-6 w-full flex items-center gap-3 px-4 py-3 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-2xl transition-all text-sm font-bold">
          <LogOut size={20} />
          Sign Out
        </button>
      </div>
    </aside>
  )
}
