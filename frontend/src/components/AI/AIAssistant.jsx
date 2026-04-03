import { useState, useRef, useEffect } from 'react'
import { MessageSquare, X, Send, Sparkles, Plus, Loader2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { chatWithAI } from '../../services/api'

export function AIAssistant({ onSuggestAction }) {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hi Vipul! I am your Zoom Scheduler AI. I can help you check for session conflicts, suggest time slots, or even draft a new session for you. How can I help today?' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const scrollRef = useRef(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMsg = { role: 'user', content: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const history = messages.map(m => ({ role: m.role, content: m.content }))
      const data = await chatWithAI({ message: input, history })
      
      const assistantMsg = { 
        role: 'assistant', 
        content: data.response,
        action: data.suggested_action 
      }
      setMessages(prev => [...prev, assistantMsg])

      // Auto-schedule if AI is confident
      if (data.force_execute && data.suggested_action) {
        setMessages(prev => [...prev, { role: 'assistant', content: '✨ Automatically scheduling that for you now...' }])
        setTimeout(() => {
          onSuggestAction(data.suggested_action, true) // Pass true to auto-save
          setIsOpen(false)
        }, 1000)
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I am having trouble connecting to my brain right now.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* Floating Button */}
      <motion.button
        whileHover={{ scale: 1.1, rotate: 5 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsOpen(true)}
        className="fixed bottom-10 right-10 w-16 h-16 bg-blue-600 text-white rounded-full shadow-2xl flex items-center justify-center z-50 hover:bg-blue-700 transition-colors"
      >
        <Sparkles size={28} />
      </motion.button>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 100, scale: 0.8, x: 20 }}
            animate={{ opacity: 1, y: 0, scale: 1, x: 0 }}
            exit={{ opacity: 0, y: 100, scale: 0.8, x: 20 }}
            className="fixed bottom-32 right-10 w-[400px] h-[600px] bg-white dark:bg-slate-900 rounded-[2.5rem] shadow-[0_20px_60px_rgb(0,0,0,0.15)] border border-slate-100 dark:border-slate-800 flex flex-col overflow-hidden z-50 transition-colors duration-500"
          >
            {/* Header */}
            <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-blue-600 text-white">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-white/20 rounded-xl"><Sparkles size={20} /></div>
                <div>
                  <h3 className="font-black text-sm tracking-tight">AI Scheduler</h3>
                  <p className="text-[10px] font-bold opacity-80 uppercase tracking-widest">Always Active</p>
                </div>
              </div>
              <button onClick={() => setIsOpen(false)} className="p-2 hover:bg-white/20 rounded-xl transition-colors">
                <X size={20} />
              </button>
            </div>

            {/* Messages */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] p-4 rounded-2xl text-sm font-medium shadow-sm ${
                    msg.role === 'user' 
                      ? 'bg-blue-600 text-white rounded-tr-none' 
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-tl-none'
                  }`}>
                    {msg.content}
                    
                    {msg.action && (
                      <button 
                        onClick={() => {
                          onSuggestAction(msg.action)
                          setIsOpen(false)
                        }}
                        className="mt-4 w-full flex items-center justify-center gap-2 py-2 bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 rounded-xl font-black text-xs border border-blue-100 dark:border-blue-900/50 hover:bg-blue-50 transition-all shadow-sm"
                      >
                        <Plus size={14} strokeWidth={3} />
                        Fill Session Form
                      </button>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-slate-100 dark:bg-slate-800 p-4 rounded-2xl rounded-tl-none">
                    <Loader2 size={18} className="animate-spin text-blue-600" />
                  </div>
                </div>
              )}
            </div>

            {/* Input */}
            <form onSubmit={handleSend} className="p-6 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
              <div className="relative group">
                <input 
                  type="text"
                  placeholder="Ask me to schedule a session..."
                  className="w-full pl-5 pr-14 py-4 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl text-sm font-medium outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all dark:text-slate-100"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                />
                <button 
                  type="submit"
                  disabled={!input.trim() || loading}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50 shadow-lg shadow-blue-200"
                >
                  <Send size={18} />
                </button>
              </div>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
