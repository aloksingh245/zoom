import { useEffect, useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import { CheckCircle, AlertCircle, Loader, Calendar, ArrowLeft } from 'lucide-react'

export function VerifyEmail() {
  const { verifyEmail } = useAuth()
  const [status, setStatus] = useState('verifying') // 'verifying' | 'success' | 'error'
  const [errorMsg, setErrorMsg] = useState('')

  useEffect(() => {
    async function performVerification() {
      const params = new URLSearchParams(window.location.search)
      const token = params.get('token')

      if (!token) {
        setStatus('error')
        setErrorMsg('Invalid verification link. Token is missing.')
        return
      }

      try {
        await verifyEmail(token)
        setStatus('success')
      } catch (err) {
        setStatus('error')
        setErrorMsg(err.message || 'Verification failed. The token may be expired or invalid.')
      }
    }

    performVerification()
  }, [verifyEmail])

  const handleGoToLogin = () => {
    // Navigate back to home/login page
    window.location.href = '/'
  }

  return (
    <div className="flex min-h-screen bg-[#0b0f19] text-slate-100 items-center justify-center p-8 relative">
      {/* Background neon glows */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-800/10 rounded-full blur-[100px] pointer-events-none" />

      <div className="w-full max-w-md bg-slate-900/40 border border-slate-800 rounded-[2.5rem] p-10 text-center relative z-10 backdrop-blur-xl shadow-2xl">
        {/* Brand Header */}
        <div className="flex justify-center items-center gap-3 mb-8">
          <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white rotate-3 border border-indigo-500/30">
            <Calendar size={22} />
          </div>
          <div>
            <span className="font-black text-xl tracking-tighter text-white block leading-none">ZOOM</span>
            <span className="text-[9px] font-bold text-indigo-400 uppercase tracking-[0.2em]">Scheduler CRM</span>
          </div>
        </div>

        {status === 'verifying' && (
          <div className="space-y-6">
            <div className="flex justify-center">
              <div className="p-4 bg-indigo-500/10 rounded-full border border-indigo-500/20 text-indigo-400 animate-spin">
                <Loader size={36} />
              </div>
            </div>
            <h2 className="text-2xl font-black text-white">Verifying Account</h2>
            <p className="text-slate-400 text-sm font-medium leading-relaxed">
              We are connecting with the secure backend to activate your account. This will only take a moment.
            </p>
          </div>
        )}

        {status === 'success' && (
          <div className="space-y-6 animate-in zoom-in duration-300">
            <div className="flex justify-center">
              <div className="p-4 bg-emerald-500/10 rounded-full border border-emerald-500/20 text-emerald-400">
                <CheckCircle size={36} />
              </div>
            </div>
            <h2 className="text-2xl font-black text-white">Account Verified!</h2>
            <p className="text-slate-400 text-sm font-medium leading-relaxed">
              Congratulations! Your email has been verified and your account is now fully active. You can proceed to sign in.
            </p>
            <button
              onClick={handleGoToLogin}
              className="mt-4 w-full py-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl text-sm font-bold flex items-center justify-center gap-2 transition-all active:scale-[0.98] cursor-pointer"
            >
              <ArrowLeft size={16} />
              Go to Sign In
            </button>
          </div>
        )}

        {status === 'error' && (
          <div className="space-y-6 animate-in zoom-in duration-300">
            <div className="flex justify-center">
              <div className="p-4 bg-red-500/10 rounded-full border border-red-500/20 text-red-400">
                <AlertCircle size={36} />
              </div>
            </div>
            <h2 className="text-2xl font-black text-white">Verification Failed</h2>
            <p className="text-red-300 text-sm font-semibold leading-relaxed">
              {errorMsg}
            </p>
            <p className="text-slate-400 text-xs font-medium leading-relaxed">
              Please double-check the verification link you received, or try registering again.
            </p>
            <button
              onClick={handleGoToLogin}
              className="mt-4 w-full py-4 bg-slate-800 hover:bg-slate-700 text-slate-100 rounded-2xl text-sm font-bold flex items-center justify-center gap-2 transition-all active:scale-[0.98] cursor-pointer border border-slate-700"
            >
              <ArrowLeft size={16} />
              Back to Sign In
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
