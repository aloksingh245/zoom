import React, { useState } from 'react'
import { MessageSquare, Bot } from 'lucide-react'
import ChatWindow from './ChatWindow'
import { useAgentChat } from '../../hooks/useAgentChat'

/**
 * ChatBubble — The entry point floating button for the AI Agent.
 * 
 * DESIGN FEATURES:
 *   - Encapsulation: Mounts the useAgentChat hook directly here so that
 *     the chat history state is preserved even if the window is closed and reopened.
 *   - Pulse Indicator: An elegant indigo glowing ring surrounding the button to
 *     indicate the system has an active AI assistant.
 *   - Positioned fixed in the bottom-right corner so it overlays on top of the dashboard,
 *     calendar, or settings cleanly.
 */
export function ChatBubble({ user }) {
  const [isOpen, setIsOpen] = useState(false)
  const chatHook = useAgentChat()

  if (!user) return null // Only show when user is logged in

  return (
    <div className="font-sans">
      {/* Floating Action Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        title="Chat with ZoomBot Assistant"
        className={`fixed bottom-8 right-8 w-14 h-14 rounded-full flex items-center justify-center text-white transition-all duration-300 shadow-2xl z-[99] active:scale-95 group cursor-pointer ${
          isOpen
            ? 'bg-slate-800 hover:bg-slate-900 rotate-90'
            : 'bg-indigo-600 hover:bg-indigo-700 hover:scale-105'
        }`}
      >
        {isOpen ? (
          <Bot size={24} />
        ) : (
          <div className="relative">
            <MessageSquare size={24} />
            {/* Pulsing indicator ring when closed */}
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-500 rounded-full border-2 border-indigo-600 animate-ping" />
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-500 rounded-full border-2 border-indigo-600" />
          </div>
        )}
      </button>

      {/* Glow effect behind the button */}
      {!isOpen && (
        <div className="fixed bottom-8 right-8 w-14 h-14 rounded-full bg-indigo-500/30 -z-10 blur-md animate-pulse pointer-events-none" />
      )}

      {/* The Chat Window overlay */}
      <ChatWindow
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        chatHook={chatHook}
        user={user}
      />
    </div>
  )
}
export default ChatBubble
