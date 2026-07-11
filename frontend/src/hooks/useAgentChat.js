import { useState, useCallback } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

/**
 * useAgentChat — Hook for managing the streaming connection to the ADK AI Agent.
 * 
 * WHY USE A CUSTOM HOOK FOR STREAMING?
 *   Streaming responses require handling raw chunk readers from the Fetch API
 *   and decoding them. Putting this inside a custom hook:
 *   1. Keeps the React UI components completely clean of fetch/stream parsing logic.
 *   2. Provides reusable states: `messages` (history), `loading` (active stream), `error`.
 *   3. Enforces session state constraints (e.g. keeping the last 20 messages).
 * 
 * STREAM PARSING STRATEGY:
 *   The server sends Server-Sent Events (SSE) where each data payload is a JSON-encoded string:
 *     data: "hello"\n\n
 *     data: " world"\n\n
 *     data: "[DONE]"\n\n
 * 
 *   We read the stream reader line-by-line, parse the JSON, and concatenate the text
 *   to the agent's message in real time to create the "typing" effect.
 */
export function useAgentChat() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const clearChat = useCallback(() => {
    setMessages([])
    setError(null)
    setLoading(false)
  }, [])

  const sendMessage = useCallback(async (text) => {
    if (!text.trim()) return

    const token = localStorage.getItem('zoom_scheduler_token')
    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date()
    }

    // Append the user's message to the state
    setMessages(prev => {
      const next = [...prev, userMessage]
      // Enforce the 20 messages limit in UI view
      if (next.length > 20) {
        return next.slice(next.length - 20)
      }
      return next
    })

    setLoading(true)
    setError(null)

    const agentMessageId = `agent-${Date.now()}`
    const agentPlaceholder = {
      id: agentMessageId,
      role: 'agent',
      content: '',
      status: 'streaming',
      timestamp: new Date()
    }

    // Insert a blank agent response placeholder
    setMessages(prev => [...prev, agentPlaceholder])

    try {
      const response = await fetch(`${API_BASE}/api/agent/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: text })
      })

      if (!response.ok) {
        const errorText = await response.text()
        let errMsg = errorText
        try {
          errMsg = JSON.parse(errorText).detail || errorText
        } catch (e) {}
        throw new Error(errMsg || `Server error: ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        
        // SSE packets are separated by double newlines (\n\n)
        const lines = buffer.split('\n\n')
        
        // Keep the last incomplete chunk in the buffer
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.trim()) continue
          if (line.startsWith('data: ')) {
            const rawData = line.slice(6).trim()
            if (rawData === '"[DONE]"') {
              // Terminal packet received — stream is finished
              break
            }
            
            try {
              // The server JSON-encodes each token. Parse it to get the string chunk.
              const parsedToken = JSON.parse(rawData)
              
              // Append token to the streaming agent message in state
              setMessages(prev => 
                prev.map(msg => 
                  msg.id === agentMessageId 
                    ? { ...msg, content: msg.content + parsedToken }
                    : msg
                )
              )
            } catch (err) {
              console.warn('Failed to parse SSE JSON chunk:', rawData, err)
            }
          }
        }
      }

      // Mark the message stream as complete
      setMessages(prev => 
        prev.map(msg => 
          msg.id === agentMessageId 
            ? { ...msg, status: 'complete' }
            : msg
        )
      )

    } catch (err) {
      console.error('Agent chat stream error:', err)
      setError(err.message)
      setMessages(prev => 
        prev.map(msg => 
          msg.id === agentMessageId 
            ? { ...msg, content: 'Failed to retrieve response from assistant.', status: 'error' }
            : msg
        )
      )
    } finally {
      setLoading(false)
    }
  }, [])

  const sendVoiceMessage = useCallback(async (audioBlob) => {
    if (!audioBlob) return null

    const token = localStorage.getItem('zoom_scheduler_token')
    setLoading(true)
    setError(null)

    const agentMessageId = `agent-${Date.now()}`
    const agentPlaceholder = {
      id: agentMessageId,
      role: 'agent',
      content: 'Thinking...',
      status: 'streaming',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, agentPlaceholder])

    try {
      const formData = new FormData()
      formData.append('file', audioBlob, 'voice.webm')

      const response = await fetch(`${API_BASE}/api/agent/chat/voice`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`)
      }

      const data = await response.json()
      
      const userMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: data.user_text || "Voice message (empty)",
        timestamp: new Date()
      }

      setMessages(prev => {
        const list = [...prev]
        const idx = list.findIndex(m => m.id === agentMessageId)
        if (idx !== -1) {
          list.splice(idx, 0, userMessage)
        } else {
          list.push(userMessage)
        }
        return list
      })

      setMessages(prev =>
        prev.map(msg =>
          msg.id === agentMessageId
            ? { ...msg, content: data.agent_text, status: 'complete' }
            : msg
        )
      )

      return data.audio

    } catch (err) {
      console.error('Agent chat voice error:', err)
      setError(err.message)
      setMessages(prev =>
        prev.map(msg =>
          msg.id === agentMessageId
            ? { ...msg, content: 'Failed to process voice response.', status: 'error' }
            : msg
        )
      )
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  return { messages, loading, error, sendMessage, sendVoiceMessage, clearChat }
}
