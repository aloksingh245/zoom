import { useState } from 'react'
import { requestOtp, signup, login } from '../../services/api'
import { AlertCircle, Lock, Mail, User, ShieldCheck } from 'lucide-react'

export function AuthPage({ onLogin, theme }) {
  const [isLogin, setIsLogin] = useState(true)
  const [step, setStep] = useState(1) // 1: Info/Login, 2: OTP
  const [form, setForm] = useState({ name: '', email: '', password: '', otp: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isLogin) {
        const res = await login({ email: form.email, password: form.password })
        onLogin(res.access_token)
      } else {
        if (step === 1) {
          await requestOtp({ name: form.name, email: form.email })
          setStep(2)
        } else {
          await signup({ name: form.name, email: form.email, password: form.password, otp: form.otp })
          setIsLogin(true)
          setStep(1)
          alert('Signup successful! You can now log in.')
          setForm({ ...form, password: '', otp: '' })
        }
      }
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={`min-h-screen flex items-center justify-center bg-[#F0F4F8] dark:bg-slate-950 p-4 ${theme === 'dark' ? 'dark' : ''}`}>
      <div className="w-full max-w-md bg-white dark:bg-slate-900 rounded-3xl shadow-xl p-8 border border-slate-100 dark:border-slate-800 transition-colors">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-black text-slate-900 dark:text-white mb-2">
            {isLogin ? 'Welcome Back' : step === 1 ? 'Create Account' : 'Verify Email'}
          </h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">
            {isLogin ? 'Sign in to continue scheduling classes' : step === 1 ? 'Sign up to get started' : 'Enter the 6-digit OTP sent to your email'}
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm font-medium rounded-xl flex items-center gap-3">
            <AlertCircle size={18} />
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {!isLogin && step === 1 && (
            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">Name</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
                  <User size={18} />
                </div>
                <input 
                  type="text" required
                  value={form.name} onChange={e => setForm({...form, name: e.target.value})}
                  className="w-full pl-11 pr-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-medium focus:ring-2 focus:ring-blue-500 outline-none transition-all dark:text-white"
                  placeholder="John Doe"
                />
              </div>
            </div>
          )}

          {(isLogin || step === 1) && (
            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">Email</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
                  <Mail size={18} />
                </div>
                <input 
                  type="email" required
                  value={form.email} onChange={e => setForm({...form, email: e.target.value})}
                  className="w-full pl-11 pr-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-medium focus:ring-2 focus:ring-blue-500 outline-none transition-all dark:text-white"
                  placeholder="you@example.com"
                />
              </div>
            </div>
          )}

          {(isLogin || (!isLogin && step === 2)) && (
            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
                  <Lock size={18} />
                </div>
                <input 
                  type="password" required minLength={6}
                  value={form.password} onChange={e => setForm({...form, password: e.target.value})}
                  className="w-full pl-11 pr-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-medium focus:ring-2 focus:ring-blue-500 outline-none transition-all dark:text-white"
                  placeholder="••••••••"
                />
              </div>
            </div>
          )}

          {!isLogin && step === 2 && (
            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">OTP Code</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
                  <ShieldCheck size={18} />
                </div>
                <input 
                  type="text" required maxLength={6} minLength={6}
                  value={form.otp} onChange={e => setForm({...form, otp: e.target.value})}
                  className="w-full pl-11 pr-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-medium focus:ring-2 focus:ring-blue-500 outline-none transition-all dark:text-white tracking-widest text-center"
                  placeholder="123456"
                />
              </div>
            </div>
          )}

          <button 
            type="submit" disabled={loading}
            className="w-full py-3.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-black rounded-xl shadow-lg shadow-blue-200 dark:shadow-none transition-all active:scale-95 disabled:opacity-70 disabled:active:scale-100"
          >
            {loading ? 'Please wait...' : isLogin ? 'Sign In' : step === 1 ? 'Continue' : 'Verify & Sign Up'}
          </button>
        </form>

        <div className="mt-8 text-center">
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button 
              type="button"
              onClick={() => { setIsLogin(!isLogin); setStep(1); setError(''); setForm({name:'',email:'',password:'',otp:''}) }}
              className="text-blue-600 dark:text-blue-400 font-bold hover:underline"
            >
              {isLogin ? 'Sign up' : 'Sign in'}
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}
