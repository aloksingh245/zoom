import { Search, Plus, Bell } from 'lucide-react'

export function TopBar({ searchTerm, setSearchTerm, openCreate }) {
  return (
    <header className="h-20 border-b border-slate-100 bg-white flex items-center justify-between px-10 z-10 shadow-sm">
      <div className="flex items-center flex-1 max-w-2xl">
        <div className="relative w-full group">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-indigo-600 transition-colors" size={20} />
          <input 
            type="text" 
            placeholder="Search classes, topics, or batches..." 
            className="w-full pl-12 pr-6 py-3 bg-slate-50 border border-transparent rounded-[1.5rem] text-sm focus:bg-white focus:border-indigo-100 focus:ring-4 focus:ring-indigo-500/5 transition-all outline-none"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
           <div className="relative">
             <button className="p-2.5 bg-slate-50 text-slate-500 hover:bg-slate-100 rounded-xl transition-all"><Bell size={20} /></button>
             <span className="absolute top-2 right-2 w-2 h-2 bg-indigo-600 rounded-full border-2 border-white"></span>
           </div>
        </div>
        <button 
          onClick={() => openCreate()}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-[1.2rem] text-sm font-bold flex items-center gap-2 transition-all shadow-xl shadow-indigo-100 active:scale-95"
        >
          <Plus size={20} />
          New Session
        </button>
        <div className="w-px h-8 bg-slate-100" />
        <div className="flex items-center gap-3 cursor-pointer group">
          <div className="text-right">
            <span className="text-sm font-bold text-slate-800 block leading-none">Alok Singh</span>
            <span className="text-[10px] font-bold text-indigo-500 uppercase tracking-wider">Administrator</span>
          </div>
          <div className="w-12 h-12 rounded-[1.2rem] bg-indigo-50 text-indigo-700 flex items-center justify-center text-sm font-black border-2 border-transparent group-hover:border-indigo-200 transition-all">AS</div>
        </div>
      </div>
    </header>
  )
}
