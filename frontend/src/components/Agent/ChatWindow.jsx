import React, { useEffect, useRef, useState } from 'react'
import { X, Send, RotateCcw, Bot, Volume2, VolumeX } from 'lucide-react'
import ChatMessage from './ChatMessage'
import VoiceButton from './VoiceButton'

/**
 * ChatWindow — The main dialogue UI panel for interacting with the AI Agent.
 * 
 * FEATURES:
 *   - Auto-Scroll: Tracks message counts/content changes and automatically scrolls
 *     to keep the latest tokens in view.
 *   - Reset Action: Allows clearing the in-memory chat session.
 *   - Responsive Textbox: Auto-focuses on open, handles ENTER key to submit.
 *   - Server-Side Voice: Records user mic blobs, transcribes them on the server using Gemini,
 *     and plays back the generated server-side MP3 voice bytes.
 */
export function ChatWindow({ isOpen, onClose, chatHook, user }) {
  const { messages, loading, sendMessage, sendVoiceMessage, clearChat } = chatHook
  const [input, setInput] = useState('')
  const [ttsEnabled, setTtsEnabled] = useState(true)
  const threadEndRef = useRef(null)
  
  const spokenIndexRef = useRef(0)
  const activeSpeechMessageIdRef = useRef(null)
  const activeAudioPlayerRef = useRef(null)
  const displayName = user?.email ? user.email.split('@')[0] : 'User'

  // Auto-scroll to the bottom of the message thread whenever a new chunk is rendered
  useEffect(() => {
    if (threadEndRef.current) {
      threadEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  // Stop speaking and clear players when window closes
  useEffect(() => {
    return () => {
      stopAllSpeech()
    }
  }, [isOpen])

  // Streaming speech synthesis (TTS) fallback for typed text messages
  useEffect(() => {
    if (!ttsEnabled || !('speechSynthesis' in window)) return

    const lastMessage = messages[messages.length - 1]
    if (!lastMessage || lastMessage.role !== 'agent') return

    // If it's a voice message response, it will be played via HTML5 Audio base64 play,
    // so we skip the browser's speechSynthesis engine for voice transactions.
    if (lastMessage.content === 'Thinking...' || activeAudioPlayerRef.current) return

    // If it's a new text message, reset speaking pointer and halt any active voice
    if (activeSpeechMessageIdRef.current !== lastMessage.id) {
      window.speechSynthesis.cancel()
      spokenIndexRef.current = 0
      activeSpeechMessageIdRef.current = lastMessage.id
    }

    const text = lastMessage.content
    const status = lastMessage.status

    if (status === 'streaming') {
      const pendingText = text.slice(spokenIndexRef.current)
      const sentenceEndMatch = /[.!?\n]/.exec(pendingText)
      if (sentenceEndMatch) {
        const endIdx = sentenceEndMatch.index + 1
        const sentence = pendingText.slice(0, endIdx).trim()
        if (sentence) {
          speakBrowserTTS(sentence)
        }
        spokenIndexRef.current += endIdx
      }
    } else if (status === 'complete' || status === 'error') {
      const remainingText = text.slice(spokenIndexRef.current).trim()
      if (remainingText) {
        speakBrowserTTS(remainingText)
      }
      spokenIndexRef.current = 0
      activeSpeechMessageIdRef.current = null
    }
  }, [messages, ttsEnabled])

  const speakBrowserTTS = (sentence) => {
    const scrubbed = sentence
      .replace(/\[HOST LINK HIDDEN[^\]]*\]/g, "Host Link Hidden")
      .replace(/\[SECRET REDACTED\]/g, "Secret Redacted")
      .replace(/[*_`#]/g, "")
      
    const utterance = new SpeechSynthesisUtterance(scrubbed)
    utterance.lang = 'en-US'
    const voices = window.speechSynthesis.getVoices()
    const preferredVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Google') || v.name.includes('Natural'))) || voices.find(v => v.lang.startsWith('en'))
    if (preferredVoice) {
      utterance.voice = preferredVoice
    }
    window.speechSynthesis.speak(utterance)
  }

  const stopAllSpeech = () => {
    // 1. Halt browser SpeechSynthesis
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
    }
    // 2. Halt standard audio player playback
    if (activeAudioPlayerRef.current) {
      activeAudioPlayerRef.current.pause()
      activeAudioPlayerRef.current = null
    }
  }

  const playBase64Audio = (base64Audio) => {
    if (!base64Audio) return
    try {
      stopAllSpeech()
      const audioUrl = `data:audio/mp3;base64,${base64Audio}`
      const audio = new Audio(audioUrl)
      activeAudioPlayerRef.current = audio
      audio.play().catch(err => {
        console.error("Server-side audio playback failed:", err)
      })
    } catch (err) {
      console.warn("Could not initialize audio player:", err)
    }
  }

  const handleAudioBlob = async (blob) => {
    stopAllSpeech()
    // Upload microphone WebM blob to server-side router
    const audioBase64 = await sendVoiceMessage(blob)
    if (audioBase64 && ttsEnabled) {
      playBase64Audio(audioBase64)
    }
  }

  const handleSend = (e) => {
    if (e) e.preventDefault()
    if (!input.trim() || loading) return
    
    stopAllSpeech()
    sendMessage(input)
    setInput('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleClearChat = () => {
    stopAllSpeech()
    spokenIndexRef.current = 0
    activeSpeechMessageIdRef.current = null
    clearChat()
  }

  if (!isOpen) return null

  return (
    <div className="fixed bottom-24 right-8 w-[400px] h-[580px] bg-white border border-slate-100 rounded-[2.5rem] shadow-2xl flex flex-col overflow-hidden z-[90] animate-in slide-in-from-bottom-8 fade-in-50 duration-300">
      
      {/* Title Bar Header */}
      <header className="px-6 py-5 border-b border-slate-50 bg-[#fafafa] flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-indigo-600 text-white flex items-center justify-center shadow-lg shadow-indigo-100">
            <Bot size={22} className="animate-pulse" />
          </div>
          <div>
            <h3 className="font-black text-sm text-slate-800 tracking-tight">ZoomBot Assistant</h3>
            <span className="text-[10px] font-bold text-indigo-500 uppercase tracking-widest">
              Active • {user?.role || 'member'}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => {
              if (ttsEnabled) {
                stopAllSpeech()
              }
              setTtsEnabled(!ttsEnabled)
            }}
            title={ttsEnabled ? "Mute Voice Replies" : "Unmute Voice Replies"}
            className={`p-2 rounded-xl transition-all cursor-pointer ${
              ttsEnabled ? 'text-indigo-600 hover:bg-indigo-50' : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100'
            }`}
          >
            {ttsEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
          </button>
          
          <button
            onClick={handleClearChat}
            title="Clear Chat Session"
            className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl transition-all cursor-pointer"
          >
            <RotateCcw size={16} />
          </button>
          
          <button
            onClick={onClose}
            title="Close Assistant"
            className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl transition-all cursor-pointer"
          >
            <X size={18} />
          </button>
        </div>
      </header>

      {/* Messages Stream Thread Container */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6 bg-slate-50/20">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center px-6">
            <div className="w-16 h-16 rounded-[1.5rem] bg-indigo-50 text-indigo-600 flex items-center justify-center mb-4">
              <Bot size={32} />
            </div>
            <p className="text-slate-800 font-black text-base">Hi, {displayName}!</p>
            <p className="text-slate-400 text-xs font-semibold mt-1">
              Ask me to show your schedule, get Zoom links, or organize classes.
            </p>
          </div>
        ) : (
          messages.map(msg => (
            <ChatMessage key={msg.id} message={msg} />
          ))
        )}
        <div ref={threadEndRef} />
      </div>

      {/* Message Input Footer Form */}
      <form onSubmit={handleSend} className="px-6 py-5 border-t border-slate-50 bg-[#fafafa] flex items-center gap-3">
        <VoiceButton 
          onAudioBlob={handleAudioBlob} 
          loading={loading} 
        />
        
        <div className="flex-1 relative flex items-center">
          <input
            type="text"
            placeholder="Type a message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            className="w-full bg-slate-100 border border-transparent rounded-[1.5rem] pl-5 pr-12 py-3.5 text-xs font-bold text-slate-700 outline-none focus:bg-white focus:border-indigo-100 focus:ring-4 focus:ring-indigo-500/5 transition-all disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="absolute right-2 p-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl transition-all shadow-md shadow-indigo-100 active:scale-95 cursor-pointer"
          >
            <Send size={14} />
          </button>
        </div>
      </form>
    </div>
  )
}
export default ChatWindow
