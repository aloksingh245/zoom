import { X, Plus, Clock, ChevronRight, Trash2, Mail } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export function ClassModal({ 
  isOpen, 
  onClose, 
  onSave, 
  onDelete, 
  editing, 
  form, 
  setForm, 
  courses, 
  loading 
}) {
  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-slate-950/20 backdrop-blur-md" 
            onClick={onClose} 
          />
          
          <motion.form 
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: "spring", duration: 0.5, bounce: 0.3 }}
            onSubmit={onSave}
            className="relative w-full max-w-3xl bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl rounded-[3rem] shadow-[0_20px_60px_rgb(0,0,0,0.08)] border border-white dark:border-slate-800 overflow-hidden"
          >
            <div className="px-12 py-10 border-b border-slate-100/50 dark:border-slate-800/50 flex items-center justify-between bg-white/50 dark:bg-slate-900/50">
              <div>
                <div className="flex items-center gap-4 mb-2">
                   <div className="p-2.5 bg-blue-600 text-white rounded-[1.2rem] shadow-lg shadow-blue-200"><Plus size={20} strokeWidth={3} /></div>
                   <h3 className="text-3xl font-black text-slate-900 dark:text-slate-100 tracking-tight transition-colors">{editing ? 'Edit Session' : 'Schedule Session'}</h3>
                </div>
                <p className="text-sm font-bold text-slate-500 dark:text-slate-400">Manage meeting details and Zoom synchronization.</p>
              </div>
              <button 
                type="button" 
                onClick={onClose}
                className="p-3 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-[1.2rem] transition-colors text-slate-400 dark:text-slate-500 active:scale-90"
              >
                <X size={24} strokeWidth={2.5} />
              </button>
            </div>

            <div className="px-12 py-10 space-y-8 max-h-[60vh] overflow-y-auto custom-scrollbar">
              <div className="space-y-3">
                <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] ml-1">Course / Batch Track</label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="relative group">
                    <select
                      className="w-full bg-slate-50/50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60 rounded-[1.5rem] px-6 py-4 text-sm font-bold text-slate-700 dark:text-slate-200 focus:bg-white dark:focus:bg-slate-800 focus:border-blue-300 dark:focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all outline-none appearance-none hover:bg-slate-50 dark:hover:bg-slate-800"
                      value={form.course_id}
                      onChange={(e) => setForm({ ...form, course_id: e.target.value })}
                    >
                      <option value="">Select Existing Batch</option>
                      {courses.map((course) => (
                        <option key={course.id} value={course.id}>{course.name}</option>
                      ))}
                    </select>
                    <ChevronRight size={18} className="absolute right-6 top-1/2 -translate-y-1/2 text-slate-400 rotate-90 pointer-events-none group-hover:text-blue-500 transition-colors" />
                  </div>
                  <div className="relative group">
                    <input
                      className="w-full bg-slate-50/50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60 rounded-[1.5rem] px-6 py-4 text-sm font-bold text-slate-700 dark:text-slate-200 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:bg-white dark:focus:bg-slate-800 focus:border-blue-300 dark:focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all outline-none hover:bg-slate-50 dark:hover:bg-slate-800"
                      placeholder="Or enter new course name..."
                      value={form.course_name}
                      onChange={(e) => setForm({ ...form, course_name: e.target.value })}
                    />
                    <Plus size={18} className="absolute right-6 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-3">
                  <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] ml-1">Session Topic</label>
                  <input
                    className="w-full bg-slate-50/50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60 rounded-[1.5rem] px-6 py-4 text-sm font-bold text-slate-700 dark:text-slate-200 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:bg-white dark:focus:bg-slate-800 focus:border-blue-300 dark:focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all outline-none hover:bg-slate-50 dark:hover:bg-slate-800"
                    placeholder="e.g. Masterclass on Advanced React"
                    value={form.topic_name}
                    onChange={(e) => setForm({ ...form, topic_name: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-3">
                  <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] ml-1">Mentor Email (for Calendar)</label>
                  <div className="relative group">
                    <input
                      type="email"
                      className="w-full bg-slate-50/50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60 rounded-[1.5rem] px-6 py-4 text-sm font-bold text-slate-700 dark:text-slate-200 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:bg-white dark:focus:bg-slate-800 focus:border-blue-300 dark:focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all outline-none hover:bg-slate-50 dark:hover:bg-slate-800"
                      placeholder="mentor@example.com"
                      value={form.mentor_email || ''}
                      onChange={(e) => setForm({ ...form, mentor_email: e.target.value })}
                    />
                    <Mail size={18} className="absolute right-6 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] ml-1">Assignment Context</label>
                <input
                  className="w-full bg-slate-50/50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60 rounded-[1.5rem] px-6 py-4 text-sm font-bold text-slate-700 dark:text-slate-200 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:bg-white dark:focus:bg-slate-800 focus:border-blue-300 dark:focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all outline-none hover:bg-slate-50 dark:hover:bg-slate-800"
                  placeholder="Project 4 submission details..."
                  value={form.assignment_name}
                  onChange={(e) => setForm({ ...form, assignment_name: e.target.value })}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="space-y-3">
                  <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] ml-1">Scheduled Date</label>
                  <input
                    type="date"
                    className="w-full bg-slate-50/50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60 rounded-[1.5rem] px-6 py-4 text-sm font-bold text-slate-700 dark:text-slate-200 focus:bg-white dark:focus:bg-slate-800 focus:border-blue-300 dark:focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all outline-none hover:bg-slate-50 dark:hover:bg-slate-800"
                    value={form.date}
                    onChange={(e) => setForm({ ...form, date: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-3">
                  <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] ml-1">Start Time (24h)</label>
                  <div className="relative group">
                    <input
                      type="time"
                      className="w-full bg-slate-50/50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60 rounded-[1.5rem] px-6 py-4 text-sm font-bold text-slate-700 dark:text-slate-200 focus:bg-white dark:focus:bg-slate-800 focus:border-blue-300 dark:focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all outline-none hover:bg-slate-50 dark:hover:bg-slate-800"
                      value={form.start_time}
                      onChange={(e) => setForm({ ...form, start_time: e.target.value })}
                      required
                    />
                    <Clock size={18} className="absolute right-6 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
                  </div>
                </div>
                <div className="space-y-3">
                  <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] ml-1">Duration (Mins)</label>
                  <input
                    type="number"
                    min="15"
                    step="15"
                    className="w-full bg-slate-50/50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60 rounded-[1.5rem] px-6 py-4 text-sm font-bold text-slate-700 dark:text-slate-200 focus:bg-white dark:focus:bg-slate-800 focus:border-blue-300 dark:focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all outline-none hover:bg-slate-50 dark:hover:bg-slate-800"
                    value={form.duration_minutes || 90}
                    onChange={(e) => setForm({ ...form, duration_minutes: parseInt(e.target.value) || 90 })}
                    required
                  />
                </div>
              </div>

              <div className="p-6 bg-gradient-to-r from-blue-50 to-blue-50/30 dark:from-blue-900/20 dark:to-blue-900/10 rounded-[2rem] flex items-center gap-5 text-blue-800 dark:text-blue-300 border border-blue-100/50 dark:border-blue-800/50 transition-colors">
                <div className="p-3 bg-white dark:bg-slate-800 rounded-2xl shadow-sm text-blue-600 dark:text-blue-400"><Clock size={24} strokeWidth={2.5} /></div>
                <div>
                   <p className="text-sm font-black">Automatic Session Window</p>
                   <p className="text-xs font-bold opacity-70 mt-0.5">Duration and timezones are synced with Zoom and Google Calendar.</p>
                </div>
              </div>
            </div>

            <div className="px-12 py-8 bg-slate-50/50 dark:bg-slate-950/50 border-t border-slate-100/50 dark:border-slate-800/50 flex items-center justify-between transition-colors">
              {editing ? (
                <button
                  type="button"
                  onClick={() => onDelete()}
                  className="flex items-center gap-2 text-red-600 font-black text-sm hover:bg-red-50 dark:hover:bg-red-900/20 px-6 py-3.5 rounded-[1.2rem] transition-all active:scale-95"
                >
                  <Trash2 size={20} strokeWidth={2.5} />
                  Remove Class
                </button>
              ) : <div />}
              
              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-8 py-3.5 text-xs font-black text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-[1.2rem] transition-all uppercase tracking-[0.15em]"
                >
                  Discard
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-10 py-3.5 rounded-[1.2rem] text-sm font-black transition-all shadow-lg shadow-blue-200/50 dark:shadow-none active:scale-95 flex items-center gap-2"
                >
                  {loading && <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />}
                  {editing ? 'Sync Changes' : 'Confirm & Schedule'}
                </button>
              </div>
            </div>
          </motion.form>
        </div>
      )}
    </AnimatePresence>
  )
}
