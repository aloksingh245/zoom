import { BookOpen } from 'lucide-react'
import { motion } from 'framer-motion'

export function CourseList({ courses }) {
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  }

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
  }

  return (
    <motion.div 
      variants={container}
      initial="hidden"
      animate="show"
      className="space-y-10"
    >
      <motion.div variants={item} className="flex items-end justify-between">
        <div>
          <h1 className="text-4xl font-black text-slate-900 dark:text-slate-100 tracking-tight transition-colors">Courses & Batches</h1>
          <p className="text-slate-500 dark:text-slate-400 font-medium mt-2 transition-colors">Manage all educational tracks in one place.</p>
        </div>
      </motion.div>
      <motion.div variants={container} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {courses.map(course => (
          <motion.div 
            variants={item}
            whileHover={{ y: -4, scale: 1.01 }}
            key={course.id} 
            className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md rounded-[2.5rem] border border-white dark:border-slate-800 p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-none hover:shadow-xl dark:hover:border-slate-700 transition-all group relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-bl from-blue-50 to-transparent dark:from-blue-900/20 rounded-bl-[100%] -mr-10 -mt-10 group-hover:from-blue-100 dark:group-hover:from-blue-900/40 transition-colors duration-500 -z-0" />
            
            <div className="relative z-10">
              <div className="w-16 h-16 bg-blue-50/80 dark:bg-blue-900/30 rounded-[1.5rem] flex items-center justify-center text-blue-600 dark:text-blue-400 mb-6 group-hover:bg-white dark:group-hover:bg-slate-800 group-hover:shadow-lg group-hover:scale-110 transition-all">
                <BookOpen size={32} strokeWidth={2.5} />
              </div>
              <h3 className="font-black text-2xl text-slate-900 dark:text-slate-100 mb-2 group-hover:text-blue-900 dark:group-hover:text-blue-400 transition-colors">{course.name}</h3>
              <p className="text-sm font-bold text-slate-400 dark:text-slate-500 mb-2 uppercase tracking-widest transition-colors">ID: <span className="text-slate-500 dark:text-slate-400">{course.id.slice(0, 8)}</span></p>
            </div>
          </motion.div>
        ))}
        {courses.length === 0 && (
          <motion.div variants={item} className="lg:col-span-3 text-center py-40 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm rounded-[3rem] border-2 border-white dark:border-slate-800 border-dashed transition-colors">
             <BookOpen size={64} className="mx-auto text-slate-200 dark:text-slate-700 mb-4" strokeWidth={1.5} />
             <p className="text-slate-400 dark:text-slate-500 font-black text-xl">No courses found</p>
          </motion.div>
        )}
      </motion.div>
    </motion.div>
  )
}
