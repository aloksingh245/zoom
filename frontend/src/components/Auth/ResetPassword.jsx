import { useState, useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'
import { Lock, ArrowRight, CheckCircle, AlertCircle, ArrowLeft, Calendar } from 'lucide-react'

export function ResetPassword() {
  const { resetPassword } = useAuth()
  const [token, setToken] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('input') // 'input' | 'success' | 'error'
  const [errorMsg, setErrorMsg] = useState('')

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const tok = params.get('token')
    if (!tok) {
      setStatus('error')
      setErrorMsg('Invalid or missing password reset token.')
    } else {
      setToken(tok)
    }
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrorMsg('')

    if (newPassword !== confirmPassword) {
      setErrorMsg('Passwords do not match.')
      return
    }

    if (newPassword.length < 6) {
      setErrorMsg('Password must be at least 6 characters long.')
      return
    }

    setLoading(true)
    try {
      await resetPassword(token, newPassword)
      setStatus('success')
    } catch (err) {
      setStatus('error')
      setErrorMsg(err.message || 'Failed to reset password. The link may have expired.')
    } finally {
      setLoading(false)
    }
  }

  const handleBackToLogin = () => {
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

        {status === 'input' && (
          <div className="space-y-6 text-left">
            <div className="text-center">
              <h2 className="text-2xl font-black text-white">Reset Password</h2>
              <p className="text-slate-400 text-sm font-medium mt-2">
                Enter your new password below to update your account access credentials.
              </p>
            </div>

            {errorMsg && (
              <div className="p-4 bg-red-950/50 border border-red-900/50 rounded-2xl flex items-start gap-3 text-red-300 animate-in fade-in duration-300">
                <AlertCircle className="shrink-0 mt-0.5" size={18} />
                <div className="text-xs font-semibold leading-relaxed">{errorMsg}</div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-4">
                <div>
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">
                    New Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                    <input
                      type="password"
                      required
                      placeholder="••••••••••••"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className="w-full pl-12 pr-4 py-3.5 bg-slate-900/60 border border-slate-800 rounded-2xl text-sm text-slate-100 placeholder-slate-600 focus:bg-slate-900 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 outline-none transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">
                    Confirm New Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                    <input
                      type="password"
                      required
                      placeholder="••••••••••••"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="w-full pl-12 pr-4 py-3.5 bg-slate-900/60 border border-slate-800 rounded-2xl text-sm text-slate-100 placeholder-slate-600 focus:bg-slate-900 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 outline-none transition-all"
                    />
                  </div>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-800 text-white rounded-2xl text-sm font-bold flex items-center justify-center gap-2 transition-all cursor-pointer select-none active:scale-[0.98] shadow-lg shadow-indigo-600/10 border border-indigo-500/30"
              >
                {loading ? 'Updating Password...' : 'Reset Password'}
                {!loading && <ArrowRight size={16} />}
              </button>
            </form>
          </div>
        )}

        {status === 'success' && (
          <div className="space-y-6 animate-in zoom-in duration-300">
            <div className="flex justify-center">
              <div className="p-4 bg-emerald-500/10 rounded-full border border-emerald-500/20 text-emerald-400">
                <CheckCircle size={36} />
              </div>
            </div>
            <h2 className="text-2xl font-black text-white">Password Reset Successful!</h2>
            <p className="text-slate-400 text-sm font-medium leading-relaxed">
              Your password has been successfully updated. You can now use your new password to sign in to your dashboard.
            </p>
            <button
              onClick={handleBackToLogin}
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
            <h2 className="text-2xl font-black text-white">Reset Failed</h2>
            <p className="text-red-300 text-sm font-semibold leading-relaxed">
              {errorMsg}
            </p>
            <p className="text-slate-400 text-xs font-medium leading-relaxed">
              The reset token may have expired or is invalid. Please request a new password reset link.
            </p>
            <button
              onClick={handleBackToLogin}
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
