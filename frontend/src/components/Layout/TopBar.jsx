import { useState } from 'react'
import { Search, Plus, RotateCw, Sun, Moon } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export function TopBar({ searchTerm, setSearchTerm, openCreate, syncClasses, loading, theme, toggleTheme }) {
  const [isSyncing, setIsSyncing] = useState(false)
  const [isSearchFocused, setIsSearchFocused] = useState(false)

  const handleSync = async () => {
    setIsSyncing(true)
    try {
      const result = await syncClasses()
      // Use a custom toast or notification in a real app, keeping alert simple for now
      alert(`Sync complete! Checked ${result.total_checked} classes, removed ${result.removed} broken links.`)
    } catch (err) {
      alert('Sync failed: ' + err.message)
    } finally {
      setIsSyncing(false)
    }
  }

  return (
    <header className="h-24 border-b border-slate-100/50 dark:border-slate-800/50 bg-white/50 dark:bg-slate-900/50 backdrop-blur-xl flex items-center justify-between px-10 z-20 sticky top-0 transition-colors duration-500">
      <div className="flex items-center flex-1 max-w-2xl relative">
        <motion.div 
          animate={{ scale: isSearchFocused ? 1.02 : 1 }}
          transition={{ type: "spring", stiffness: 400, damping: 30 }}
          className="relative w-full group"
        >
          <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-600 transition-colors z-10" size={20} />
          <input 
            type="text" 
            placeholder="Search classes, topics, or batches..." 
            className="w-full pl-14 pr-6 py-4 bg-white dark:bg-slate-800 border border-slate-200/60 dark:border-slate-700/60 rounded-[1.5rem] text-sm font-medium text-slate-700 dark:text-slate-200 placeholder:text-slate-400 focus:bg-white dark:focus:bg-slate-800 focus:border-blue-200 dark:focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all outline-none shadow-sm"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onFocus={() => setIsSearchFocused(true)}
            onBlur={() => setIsSearchFocused(false)}
          />
        </motion.div>
      </div>
      
      <div className="flex items-center gap-6 pl-8">
        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={toggleTheme}
          className="p-3 bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 rounded-2xl transition-all shadow-sm hover:shadow-md"
        >
          {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
        </motion.button>

        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleSync}
          disabled={isSyncing || loading}
          title="Sync with Zoom"
          className="relative p-3 bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:border-blue-100 dark:hover:border-blue-900 hover:shadow-md hover:shadow-blue-100/50 rounded-2xl transition-all group"
        >
          <RotateCw size={20} className={isSyncing ? 'animate-spin text-blue-600' : 'group-hover:rotate-180 transition-transform duration-500'} />
          {(isSyncing || loading) && (
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
            </span>
          )}
        </motion.button>
        
        <motion.button 
          whileHover={{ scale: 1.02, y: -2 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => openCreate()}
          className="bg-blue-600 hover:bg-blue-700 text-white px-7 py-3.5 rounded-[1.2rem] text-sm font-black flex items-center gap-2 transition-colors shadow-lg shadow-blue-200/50"
        >
          <Plus size={20} strokeWidth={3} />
          <span className="hidden md:inline">New Session</span>
        </motion.button>
        
        <div className="w-px h-10 bg-slate-200/60 dark:bg-slate-700/60" />
        
        <motion.div 
          whileHover={{ scale: 1.02 }}
          className="flex items-center gap-4 cursor-pointer group"
        >
          <div className="text-right hidden sm:block">
            <span className="text-sm font-black text-slate-800 dark:text-slate-100 block leading-none group-hover:text-blue-900 dark:group-hover:text-blue-400 transition-colors">Vipul Pawar</span>
            <span className="text-[10px] font-bold text-blue-500 uppercase tracking-widest mt-1 block">Administrator</span>
          </div>
          <div className="w-12 h-12 rounded-[1.2rem] bg-gradient-to-br from-blue-50 to-blue-100 dark:from-slate-800 dark:to-slate-700 text-blue-700 dark:text-blue-400 flex items-center justify-center text-sm font-black border-2 border-white dark:border-slate-600 shadow-sm group-hover:shadow-md transition-all">VP</div>
        </motion.div>
      </div>
    </header>
  )
}
