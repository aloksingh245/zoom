import { useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import { Calendar, Mail, Lock, Shield, ArrowRight, CheckCircle, AlertCircle, ArrowLeft } from 'lucide-react'
import authBanner from '../../assets/auth_banner.jpg'

export function AuthPage() {
  const { login, signup, forgotPassword, error, setError } = useAuth()
  const [mode, setMode] = useState('login') // 'login' | 'signup' | 'forgot'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('admin')
  const [loading, setLoading] = useState(false)
  const [successMsg, setSuccessMsg] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setSuccessMsg('')
    setLoading(true)

    try {
      if (mode === 'login') {
        await login(email, password)
      } else if (mode === 'signup') {
        await signup(email, password, role)
        setSuccessMsg(
          'Registration successful! We have sent a verification email to your address. Please click the link to activate your account.'
        )
        // Reset fields
        setEmail('')
        setPassword('')
        setRole('admin')
      } else if (mode === 'forgot') {
        await forgotPassword(email)
        setSuccessMsg(
          'If your email is registered in our system, we have sent a reset password link to it. Please check your email inbox.'
        )
        // Reset email
        setEmail('')
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getFormTitle = () => {
    if (mode === 'login') return 'Welcome back'
    if (mode === 'signup') return 'Create an account'
    return 'Reset password'
  }

  const getFormSubtitle = () => {
    if (mode === 'login') return 'Sign in to access your scheduling dashboard'
    if (mode === 'signup') return 'Register a new profile to manage classes and syncing'
    return 'Enter your email to receive a password reset link'
  }

  return (
    <div className="flex h-screen bg-[#0b0f19] text-slate-100 overflow-hidden font-sans select-none">
      {/* Left side banner - Visual Showcase */}
      <div className="hidden lg:flex lg:w-1/2 relative flex-col justify-between p-16 overflow-hidden">
        {/* Background Image with elegant overlay */}
        <div className="absolute inset-0 z-0">
          <img 
            src={authBanner} 
            alt="Workspace Illustration" 
            className="w-full h-full object-cover opacity-60 scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-950/90 via-slate-950/70 to-indigo-950/90 mix-blend-multiply" />
          <div className="absolute inset-0 bg-radial-gradient from-transparent to-slate-950/50" />
        </div>

        {/* Top Header */}
        <div className="relative z-10 flex items-center gap-3">
          <div className="w-12 h-12 bg-indigo-600 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-indigo-500/20 rotate-3 border border-indigo-500/30">
            <Calendar size={26} />
          </div>
          <div>
            <span className="font-black text-2xl tracking-tighter text-white block leading-none">ZOOM</span>
            <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-[0.2em]">Scheduler CRM</span>
          </div>
        </div>

        {/* Content */}
        <div className="relative z-10 space-y-6 max-w-lg mb-12">
          <h1 className="text-4xl font-extrabold tracking-tight text-white leading-tight">
            Schedule meetings, manage batches, and sync integrations <span className="text-indigo-400">effortlessly</span>.
          </h1>
          <p className="text-slate-400 text-sm leading-relaxed font-medium">
            Connect and orchestrate classes in real-time. Instantly provision Zoom meetings, coordinate Google Calendar events, log entries to Google Sheets, and update CRM records.
          </p>
          <div className="flex items-center gap-6 pt-4">
            <div className="flex -space-x-3">
              <span className="w-9 h-9 rounded-full bg-slate-800 border-2 border-indigo-900 flex items-center justify-center text-xs font-black text-indigo-400">Z</span>
              <span className="w-9 h-9 rounded-full bg-slate-800 border-2 border-indigo-900 flex items-center justify-center text-xs font-black text-indigo-400">G</span>
              <span className="w-9 h-9 rounded-full bg-slate-800 border-2 border-indigo-900 flex items-center justify-center text-xs font-black text-indigo-400">S</span>
              <span className="w-9 h-9 rounded-full bg-slate-800 border-2 border-indigo-900 flex items-center justify-center text-xs font-black text-indigo-400">C</span>
            </div>
            <span className="text-xs font-bold text-slate-400">All key workspace tools connected</span>
          </div>
        </div>

        {/* Footer */}
        <div className="relative z-10 text-xs font-medium text-slate-500">
          &copy; {new Date().getFullYear()} Alok Kumar Singh. All rights reserved.
        </div>
      </div>

      {/* Right side form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-[#0b0f19] relative">
        {/* Glow effect behind form */}
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-[100px] pointer-events-none" />
        <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-indigo-800/10 rounded-full blur-[100px] pointer-events-none" />

        <div className="w-full max-w-md space-y-8 z-10">
          <div className="text-center lg:text-left">
            <h2 className="text-3xl font-black tracking-tight text-white">
              {getFormTitle()}
            </h2>
            <p className="text-slate-400 mt-2 text-sm font-medium">
              {getFormSubtitle()}
            </p>
          </div>

          {/* Messages */}
          {error && (
            <div className="p-4 bg-red-950/50 border border-red-900/50 rounded-2xl flex items-start gap-3 text-red-300 animate-in fade-in duration-300">
              <AlertCircle className="shrink-0 mt-0.5" size={18} />
              <div className="text-xs font-semibold leading-relaxed">{error}</div>
            </div>
          )}

          {successMsg && (
            <div className="p-4 bg-emerald-950/50 border border-emerald-900/50 rounded-2xl flex items-start gap-3 text-emerald-300 animate-in fade-in duration-300">
              <CheckCircle className="shrink-0 mt-0.5" size={18} />
              <div className="text-xs font-semibold leading-relaxed">{successMsg}</div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <div>
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">
                  Username or Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                  <input
                    type="text"
                    required
                    placeholder="Alok007 or name@organization.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-12 pr-4 py-3.5 bg-slate-900/60 border border-slate-800 rounded-2xl text-sm text-slate-100 placeholder-slate-600 focus:bg-slate-900 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 outline-none transition-all"
                  />
                </div>
              </div>

              {mode !== 'forgot' && (
                <div>
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">
                    Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                    <input
                      type="password"
                      required
                      placeholder="••••••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full pl-12 pr-4 py-3.5 bg-slate-900/60 border border-slate-800 rounded-2xl text-sm text-slate-100 placeholder-slate-600 focus:bg-slate-900 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 outline-none transition-all"
                    />
                  </div>
                  {mode === 'login' && (
                    <div className="text-right mt-2">
                      <button
                        type="button"
                        onClick={() => {
                          setMode('forgot')
                          setError(null)
                          setSuccessMsg('')
                        }}
                        className="text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors cursor-pointer"
                      >
                        Forgot Password?
                      </button>
                    </div>
                  )}
                </div>
              )}

              {mode === 'signup' && (
                <div>
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">
                    Account Role (Authorization)
                  </label>
                  <div className="relative">
                    <Shield className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                    <select
                      value={role}
                      onChange={(e) => setRole(e.target.value)}
                      className="w-full pl-12 pr-4 py-3.5 bg-slate-900/60 border border-slate-800 rounded-2xl text-sm text-slate-100 placeholder-slate-600 focus:bg-slate-900 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 outline-none transition-all appearance-none cursor-pointer"
                    >
                      <option value="admin" className="bg-[#0b0f19]">Administrator (Full Access)</option>
                      <option value="mentor" className="bg-[#0b0f19]">Mentor (View-Only & Zoom Links)</option>
                      <option value="student" className="bg-[#0b0f19]">Student (Limited Access)</option>
                    </select>
                  </div>
                </div>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-800 text-white rounded-2xl text-sm font-bold flex items-center justify-center gap-2 transition-all cursor-pointer select-none active:scale-[0.98] shadow-lg shadow-indigo-600/10 border border-indigo-500/30"
            >
              {loading 
                ? 'Processing...' 
                : (mode === 'login' ? 'Sign In' : (mode === 'signup' ? 'Sign Up' : 'Send Reset Link'))}
              {!loading && <ArrowRight size={16} />}
            </button>
          </form>

          <div className="text-center pt-2">
            {mode === 'forgot' ? (
              <button
                onClick={() => {
                  setMode('login')
                  setError(null)
                  setSuccessMsg('')
                }}
                className="text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors flex items-center justify-center gap-2 mx-auto cursor-pointer"
              >
                <ArrowLeft size={14} />
                Back to Sign In
              </button>
            ) : (
              <button
                onClick={() => {
                  setMode(mode === 'login' ? 'signup' : 'login')
                  setError(null)
                  setSuccessMsg('')
                }}
                className="text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors cursor-pointer"
              >
                {mode === 'login' ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
