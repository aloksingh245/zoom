import { BookOpen, Plus, PlusCircle } from 'lucide-react'

export function CourseList({ courses }) {
  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Courses & Batches</h1>
          <p className="text-slate-500 font-medium mt-1">Manage all educational tracks in one place.</p>
        </div>
        <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-[1.2rem] text-sm font-bold flex items-center gap-2 transition-all shadow-xl shadow-indigo-100">
          <Plus size={20} />
          Add Course
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {courses.map(course => (
          <div key={course.id} className="bg-white rounded-[2.5rem] border border-slate-100 p-8 shadow-xl shadow-slate-200/40 hover:border-indigo-200 transition-all group relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-50/50 rounded-bl-[100%] -mr-10 -mt-10 group-hover:bg-indigo-600 transition-colors duration-500 -z-0" />
            
            <div className="relative z-10">
              <div className="w-16 h-16 bg-indigo-50 rounded-[1.5rem] flex items-center justify-center text-indigo-600 mb-6 group-hover:bg-white group-hover:shadow-lg transition-all">
                <BookOpen size={32} />
              </div>
              <h3 className="font-black text-2xl text-slate-900 mb-2 group-hover:text-slate-800 transition-colors">{course.name}</h3>
              <p className="text-sm font-bold text-slate-400 mb-6 uppercase tracking-widest">ID: {course.id.slice(0, 8)}</p>
              
              <div className="flex items-center gap-6 pt-6 border-t border-slate-50">
                <div className="flex flex-col">
                   <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Students</span>
                   <span className="text-lg font-black text-slate-800">42</span>
                </div>
                <div className="flex flex-col">
                   <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Status</span>
                   <span className="text-xs font-black text-emerald-500 bg-emerald-50 px-2 py-1 rounded-lg mt-1">Active</span>
                </div>
              </div>
            </div>
          </div>
        ))}
        {courses.length === 0 && (
          <div className="lg:col-span-3 text-center py-40 bg-white rounded-[3rem] border border-slate-100 border-dashed">
             <BookOpen size={64} className="mx-auto text-slate-100 mb-4" />
             <p className="text-slate-300 font-black text-xl">No courses found</p>
          </div>
        )}
      </div>
    </div>
  )
}
