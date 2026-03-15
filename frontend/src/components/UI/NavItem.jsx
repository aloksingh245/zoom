import { ChevronRight } from 'lucide-react'
import { cn } from '../../utils/cn'

export function NavItem({ icon, label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full flex items-center gap-3 px-5 py-4 rounded-2xl text-sm font-black transition-all relative group",
        active 
          ? "bg-indigo-50 text-indigo-700 shadow-sm" 
          : "text-slate-400 hover:bg-slate-50 hover:text-slate-800"
      )}
    >
      <span className={cn("transition-transform duration-300", active && "scale-110")}>{icon}</span>
      <span className="flex-1 text-left">{label}</span>
      {active && <div className="w-1.5 h-6 bg-indigo-600 rounded-full absolute right-2" />}
      {!active && <ChevronRight size={14} className="opacity-0 group-hover:opacity-100 -translate-x-2 group-hover:translate-x-0 transition-all" />}
    </button>
  )
}
