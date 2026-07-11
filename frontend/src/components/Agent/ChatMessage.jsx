import React, { useMemo } from 'react'
import { Bot, User, ArrowUpRight } from 'lucide-react'

/**
 * ChatMessage — Renders a single message in the chat thread.
 * 
 * DESIGN SPECIFICATIONS:
 *   - User messages: Sleek indigo bubble on the right, matches original theme.
 *   - Agent messages: White bubble with light slate borders, Bot avatar, on the left.
 *   - Markdown Helper: Surgically converts **bold**, newlines, and URLs to HTML tags
 *     so that links and action outputs are readable and clickable.
 */
export function ChatMessage({ message }) {
  const isAgent = message.role === 'agent'

  // Format helper to parse simple markdown bold and format URLs into clickable links.
  // Using useMemo ensures we only run this regex parsing when message content changes.
  const formattedContent = useMemo(() => {
    let text = message.content || ''
    
    // 1. Escape HTML to prevent XSS injection attacks
    text = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')

    // 2. Bold tags: **bold text** -> <strong>bold text</strong>
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')

    // 3. Link conversion: Parse zoom, google calendar, sheets or web urls and make them clickable
    const urlPattern = /(https?:\/\/[^\s]+)/g
    text = text.replace(urlPattern, (url) => {
      const isZoom = url.includes('zoom.us')
      const label = isZoom ? 'Join Zoom Meeting' : 'Open Link'
      const btnClass = isZoom
        ? 'inline-flex items-center gap-1 bg-red-50 text-red-600 border border-red-100 hover:bg-red-100/50 px-2 py-0.5 rounded-lg text-xs font-bold transition-all mx-1'
        : 'inline-flex items-center gap-1 text-indigo-600 hover:underline font-bold text-xs mx-1'
      
      return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="${btnClass}">${label} <span class="align-middle">&nearr;</span></a>`
    })

    // 4. Line breaks: \n -> <br/>
    text = text.replace(/\n/g, '<br/>')

    return text
  }, [message.content])

  return (
    <div className={`flex gap-4 w-full ${isAgent ? 'justify-start' : 'justify-end animate-in slide-in-from-right-4 duration-300'}`}>
      {/* Bot Avatar on Left */}
      {isAgent && (
        <div className="w-9 h-9 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 shrink-0">
          <Bot size={18} />
        </div>
      )}

      {/* Message Bubble */}
      <div
        className={`max-w-[75%] rounded-2xl px-5 py-3.5 text-sm shadow-sm leading-relaxed ${
          isAgent
            ? 'bg-white border border-slate-100 text-slate-800 rounded-tl-sm'
            : 'bg-indigo-600 text-white font-medium rounded-tr-sm'
        }`}
      >
        <div 
          dangerouslySetInnerHTML={{ __html: formattedContent }} 
          className="space-y-1 break-words"
        />
        {message.status === 'streaming' && (
          <span className="inline-flex gap-0.5 ml-1 select-none">
            <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce delay-100" />
            <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce delay-200" />
            <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce delay-300" />
          </span>
        )}
      </div>

      {/* User Initials or Avatar on Right */}
      {!isAgent && (
        <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center text-white text-xs font-bold shrink-0">
          <User size={18} />
        </div>
      )}
    </div>
  )
}
export default ChatMessage
