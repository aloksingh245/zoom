import React, { useState, useRef } from 'react'
import { Mic, MicOff } from 'lucide-react'

/**
 * VoiceButton — Voice recording component that uses MediaRecorder API
 * to capture audio WebM blobs and pass them to the chat loop.
 */
export function VoiceButton({ onAudioBlob, loading }) {
  const [isRecording, setIsRecording] = useState(false)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])

  const startRecording = async () => {
    audioChunksRef.current = []
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      // Choose WebM or standard audio format supported by the browser
      let mimeType = 'audio/webm'
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = 'audio/ogg'
      }
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = '' // default
      }

      const mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType || 'audio/webm' })
        if (onAudioBlob) {
          onAudioBlob(audioBlob)
        }
        // Release the microphone track resources
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorderRef.current = mediaRecorder
      mediaRecorder.start()
      setIsRecording(true)
    } catch (err) {
      console.error("Failed to start audio recording:", err)
      alert("Could not access your microphone. Please check your browser mic permissions.")
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const toggleRecording = () => {
    if (loading) return
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  return (
    <button
      type="button"
      onClick={toggleRecording}
      disabled={loading}
      title={isRecording ? "Stop and send" : "Record voice message"}
      className={`p-3 rounded-2xl flex items-center justify-center transition-all duration-300 relative group cursor-pointer ${
        isRecording
          ? 'bg-rose-500 text-white animate-pulse hover:bg-rose-600 scale-105 shadow-lg shadow-rose-100'
          : 'bg-indigo-50 text-indigo-600 hover:bg-indigo-100 hover:scale-105 active:scale-95 disabled:opacity-50'
      }`}
    >
      {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
      <span className="absolute bottom-full mb-2 scale-0 group-hover:scale-100 transition-all duration-200 bg-slate-800 text-white text-[10px] font-bold px-2 py-1 rounded shadow-lg whitespace-nowrap z-50">
        {isRecording ? "Stop & Send" : "Record Voice Message"}
      </span>
    </button>
  )
}

export default VoiceButton
