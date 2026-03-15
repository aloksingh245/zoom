import { cn } from '../../utils/cn'

export function StatCard({ title, value, icon, trend, color }) {
  const colors = {
    indigo: "bg-indigo-50 text-indigo-600",
    blue: "bg-blue-50 text-blue-600",
    emerald: "bg-emerald-50 text-emerald-600",
    orange: "bg-orange-50 text-orange-600",
  }
  
  return (
    <div className="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm hover:shadow-xl hover:shadow-slate-200/40 transition-all group">
      <div className="flex items-center justify-between mb-6">
        <div className={cn("p-4 rounded-2xl group-hover:scale-110 transition-transform", colors[color])}>{icon}</div>
        <div className="text-right">
           <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] block mb-1">Status</span>
           <span className="text-xs font-black text-emerald-500 bg-emerald-50 px-2.5 py-1 rounded-lg">{trend}</span>
        </div>
      </div>
      <div>
        <p className="text-xs font-black text-slate-400 uppercase tracking-widest">{title}</p>
        <p className="text-4xl font-black text-slate-900 mt-2 tracking-tighter">{value}</p>
      </div>
    </div>
  )
}
