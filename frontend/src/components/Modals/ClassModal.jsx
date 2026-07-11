import { X, Plus, Clock, ChevronRight, Trash2, Mail, Video, ExternalLink } from 'lucide-react'

export function ClassModal({ 
  isOpen, 
  onClose, 
  onSave, 
  onDelete, 
  editing, 
  form, 
  setForm, 
  courses, 
  loading,
  userRole = 'admin'
}) {
  if (!isOpen) return null

  const isReadOnly = userRole !== 'admin'

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
      <div className="absolute inset-0 bg-slate-950/40 backdrop-blur-md animate-in fade-in duration-500" onClick={onClose} />
      
      <form 
        onSubmit={onSave}
        className="relative w-full max-w-3xl bg-white rounded-[3rem] shadow-2xl overflow-hidden animate-in zoom-in-95 slide-in-from-bottom-10 duration-500"
      >
        <div className="px-12 py-10 border-b border-slate-50 flex items-center justify-between bg-white">
          <div>
            <div className="flex items-center gap-3 mb-1">
               <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
                 <Video size={20} />
               </div>
               <h3 className="text-2xl font-black text-slate-900 tracking-tight">
                 {isReadOnly ? 'Session Details' : (editing ? 'Edit Class Session' : 'Schedule New Session')}
               </h3>
            </div>
            <p className="text-sm font-medium text-slate-400">
              {isReadOnly ? 'View meeting details and active links.' : 'Manage meeting details and Zoom synchronization.'}
            </p>
          </div>
          <button 
            type="button" 
            onClick={onClose}
            className="p-3 hover:bg-slate-100 rounded-2xl transition-colors text-slate-400 active:scale-90"
          >
            <X size={24} />
          </button>
        </div>

        <div className="px-12 py-10 space-y-8 max-h-[60vh] overflow-y-auto">

          {/* Zoom Connection Card for Students and Mentors */}
          {isReadOnly && editing && (
            <div className="p-6 bg-gradient-to-r from-indigo-900 to-indigo-950 rounded-3xl text-white shadow-xl shadow-indigo-900/10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 border border-indigo-800/30">
              <div className="space-y-1">
                <span className="text-[10px] font-black uppercase text-indigo-300 tracking-widest">Active Zoom Link</span>
                <p className="text-lg font-black">{editing.topic_name}</p>
                <p className="text-xs font-semibold text-indigo-200">Scheduled Date: {editing.date} at {editing.start_time}</p>
              </div>
              <div className="flex gap-3 w-full md:w-auto shrink-0">
                {editing.zoom_join_url && (
                  <button
                    type="button"
                    onClick={() => window.open(editing.zoom_join_url, '_blank')}
                    className="w-full md:w-auto px-6 py-3.5 bg-red-600 hover:bg-red-700 text-white rounded-2xl text-xs font-bold transition-all active:scale-95 flex items-center justify-center gap-2 shadow-lg shadow-red-600/20"
                  >
                    <Video size={16} />
                    Join Session
                  </button>
                )}
                {editing.zoom_start_url && (userRole === 'mentor' || userRole === 'admin') && (
                  <button
                    type="button"
                    onClick={() => window.open(editing.zoom_start_url, '_blank')}
                    className="w-full md:w-auto px-6 py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl text-xs font-bold transition-all active:scale-95 flex items-center justify-center gap-2 border border-indigo-500/30 shadow-lg shadow-indigo-600/20"
                  >
                    <ExternalLink size={16} />
                    Start (Host)
                  </button>
                )}
              </div>
            </div>
          )}

          <div className="space-y-3">
            <label className="text-xs font-black text-slate-400 uppercase tracking-[0.2em]">Course / Batch Track</label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="relative">
                <select
                  disabled={isReadOnly}
                  className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-6 py-4 text-sm font-bold text-slate-700 focus:bg-white focus:border-indigo-100 focus:ring-4 focus:ring-indigo-500/5 transition-all outline-none appearance-none disabled:opacity-75 disabled:cursor-not-allowed"
                  value={form.course_id}
                  onChange={(e) => setForm({ ...form, course_id: e.target.value })}
                >
                  <option value="">Select Existing Batch</option>
                  {courses.map((course) => (
                    <option key={course.id} value={course.id}>{course.name}</option>
                  ))}
                </select>
                <ChevronRight size={18} className="absolute right-6 top-1/2 -translate-y-1/2 text-slate-300 rotate-90 pointer-events-none" />
              </div>
              <div className="relative">
                <input
                  disabled={isReadOnly}
                  className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-6 py-4 text-sm font-bold text-slate-700 focus:bg-white focus:border-indigo-100 focus:ring-4 focus:ring-indigo-500/5 transition-all outline-none disabled:opacity-75 disabled:cursor-not-allowed"
                  placeholder={isReadOnly ? "No custom course name" : "Or enter new course name..."}
                  value={form.course_name}
                  onChange={(e) => setForm({ ...form, course_name: e.target.value })}
                />
                {!isReadOnly && <Plus size={18} className="absolute right-6 top-1/2 -translate-y-1/2 text-slate-300" />}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-3">
              <label className="text-xs font-black text-slate-400 uppercase tracking-[0.2em]">Session Topic</label>
              <input
                disabled={isReadOnly}
                className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-6 py-4 text-sm font-bold text-slate-700 focus:bg-white focus:border-indigo-100 focus:ring-4 focus:ring-indigo-500/5 transition-all outline-none disabled:opacity-75 disabled:cursor-not-allowed"
                placeholder="e.g. Masterclass on Advanced React Hooks"
                value={form.topic_name}
                onChange={(e) => setForm({ ...form, topic_name: e.target.value })}
                required
              />
            </div>
            <div className="space-y-3">
              <label className="text-xs font-black text-slate-400 uppercase tracking-[0.2em]">Mentor Email (for Calendar)</label>
              <div className="relative">
                <input
                  disabled={isReadOnly}
                  type="email"
                  className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-6 py-4 text-sm font-bold text-slate-700 focus:bg-white focus:border-indigo-100 focus:ring-4 focus:ring-indigo-500/5 transition-all outline-none disabled:opacity-75 disabled:cursor-not-allowed"
                  placeholder="mentor@example.com"
                  value={form.mentor_email || ''}
                  onChange={(e) => setForm({ ...form, mentor_email: e.target.value })}
                />
                <Mail size={18} className="absolute right-6 top-1/2 -translate-y-1/2 text-slate-300" />
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <label className="text-xs font-black text-slate-400 uppercase tracking-[0.2em]">Assignment Context</label>
            <input
              disabled={isReadOnly}
              className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-6 py-4 text-sm font-bold text-slate-700 focus:bg-white focus:border-indigo-100 focus:ring-4 focus:ring-indigo-500/5 transition-all outline-none disabled:opacity-75 disabled:cursor-not-allowed"
              placeholder={isReadOnly ? "No assignment context details" : "Project 4 submission details..."}
              value={form.assignment_name}
              onChange={(e) => setForm({ ...form, assignment_name: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="space-y-3">
              <label className="text-xs font-black text-slate-400 uppercase tracking-[0.2em]">Scheduled Date</label>
              <input
                disabled={isReadOnly}
                type="date"
                className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-6 py-4 text-sm font-bold text-slate-700 focus:bg-white focus:border-indigo-100 focus:ring-4 focus:ring-indigo-500/5 transition-all outline-none disabled:opacity-75 disabled:cursor-not-allowed"
                value={form.date}
                onChange={(e) => setForm({ ...form, date: e.target.value })}
                required
              />
            </div>
            <div className="space-y-3">
              <label className="text-xs font-black text-slate-400 uppercase tracking-[0.2em]">Start Time (24h)</label>
              <div className="relative">
                <input
                  disabled={isReadOnly}
                  type="time"
                  className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-6 py-4 text-sm font-bold text-slate-700 focus:bg-white focus:border-indigo-100 focus:ring-4 focus:ring-indigo-500/5 transition-all outline-none disabled:opacity-75 disabled:cursor-not-allowed"
                  value={form.start_time}
                  onChange={(e) => setForm({ ...form, start_time: e.target.value })}
                  required
                />
                <Clock size={18} className="absolute right-6 top-1/2 -translate-y-1/2 text-slate-300 pointer-events-none" />
              </div>
            </div>
            <div className="space-y-3">
              <label className="text-xs font-black text-slate-400 uppercase tracking-[0.2em]">Duration (Mins)</label>
              <input
                disabled={isReadOnly}
                type="number"
                min="15"
                step="15"
                className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-6 py-4 text-sm font-bold text-slate-700 focus:bg-white focus:border-indigo-100 focus:ring-4 focus:ring-indigo-500/5 transition-all outline-none disabled:opacity-75 disabled:cursor-not-allowed"
                value={form.duration_minutes || 90}
                onChange={(e) => setForm({ ...form, duration_minutes: parseInt(e.target.value) || 90 })}
                required
              />
            </div>
          </div>

          <div className="p-6 bg-indigo-50/50 rounded-3xl flex items-center gap-4 text-indigo-700 border border-indigo-50">
            <div className="p-3 bg-white rounded-2xl shadow-sm text-indigo-600"><Clock size={24} /></div>
            <div>
               <p className="text-sm font-black">Flexible Session Window</p>
               <p className="text-xs font-medium opacity-80">Adjust duration as needed. Default is 90 minutes for standard batches.</p>
            </div>
          </div>
        </div>

        <div className="px-12 py-10 bg-slate-50/50 border-t border-slate-50 flex items-center justify-between">
          {!isReadOnly ? (
            <>
              {editing ? (
                <button
                  type="button"
                  onClick={() => onDelete()}
                  className="flex items-center gap-2 text-red-600 font-black text-sm hover:bg-red-50 px-6 py-3 rounded-2xl transition-all active:scale-95"
                >
                  <Trash2 size={20} />
                  Remove Class
                </button>
              ) : <div />}
              
              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-8 py-4 text-sm font-black text-slate-500 hover:text-slate-700 transition-colors uppercase tracking-widest"
                >
                  Discard
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-10 py-4 rounded-2xl text-sm font-black transition-all shadow-2xl shadow-indigo-100 active:scale-95 flex items-center gap-2"
                >
                  {loading && <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />}
                  {editing ? 'Sync Changes' : 'Confirm & Schedule'}
                </button>
              </div>
            </>
          ) : (
            <div className="ml-auto">
              <button
                type="button"
                onClick={onClose}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-10 py-4 rounded-2xl text-sm font-black transition-all active:scale-95 flex items-center gap-2"
              >
                Close View
              </button>
            </div>
          )}
        </div>
      </form>
    </div>
  )
}
