import { useState, useEffect } from 'react'
import { getSettings, updateSettings } from '../../services/api'
import { Video, Calendar, Table, Mail, Shield, Save, RefreshCw, AlertCircle, CheckCircle, Globe, Sparkles } from 'lucide-react'

export function SettingsPanel() {
  const [loading, setLoading] = useState(true)
  const [saveLoading, setSaveLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [touched, setTouched] = useState({})
  const [validationErrors, setValidationErrors] = useState({})
  
  const [form, setForm] = useState({
    zoom_account_id: '',
    zoom_client_id: '',
    zoom_client_secret: '',
    zoom_user_id: '',
    google_calendar_id: '',
    google_sheet_id: '',
    smtp_host: '',
    smtp_port: 587,
    smtp_username: '',
    smtp_password: '',
    smtp_from: '',
    app_url: '',
    timezone_default: 'Asia/Kolkata',
    gemini_api_key: '',
  })

  const validateEmail = (email) => {
    if (!email) return false
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  }

  const validateTimezone = (tz) => {
    try {
      if (!tz) return false
      Intl.DateTimeFormat(undefined, { timeZone: tz })
      return true
    } catch (e) {
      return false
    }
  }

  const validatePort = (port) => {
    const p = parseInt(port, 10)
    return !isNaN(p) && p > 0 && p <= 65535
  }

  const validateUrl = (url) => {
    if (!url) return false
    try {
      new URL(url)
      return true
    } catch (e) {
      return false
    }
  }

  const runValidation = (field, value) => {
    let err = ""
    const valStr = value !== undefined && value !== null ? String(value).trim() : ""
    
    switch (field) {
      case 'zoom_account_id':
        if (!valStr) err = "Zoom Account ID is required"
        break
      case 'zoom_client_id':
        if (!valStr) err = "Zoom Client ID is required"
        break
      case 'zoom_client_secret':
        if (!value) err = "Zoom Client Secret is required"
        break
      case 'zoom_user_id':
        if (!valStr) err = "Zoom Host Email is required"
        else if (!validateEmail(valStr)) err = "Please enter a valid email address for Zoom Host"
        break
      case 'google_calendar_id':
        if (!valStr) {
          err = "Google Calendar ID is required"
        } else if (valStr !== 'primary' && !validateEmail(valStr)) {
          err = "Google Calendar ID must be 'primary' or a valid email address"
        }
        break
      case 'google_sheet_id':
        if (!valStr) err = "Google Sheets Spreadsheet ID is required"
        break
      case 'smtp_host':
        if (!valStr) err = "SMTP Host is required"
        break
      case 'smtp_port':
        if (!validatePort(value)) err = "SMTP port must be a positive integer between 1 and 65535"
        break
      case 'smtp_username':
        if (!valStr) err = "SMTP Username is required"
        break
      case 'smtp_password':
        if (!value) err = "SMTP Password is required"
        break
      case 'smtp_from':
        if (!valStr) err = "SMTP Sender Email is required"
        else if (!validateEmail(valStr)) err = "Please enter a valid email address for SMTP Sender"
        break
      case 'app_url':
        if (!valStr) err = "App Host URL is required"
        else if (!validateUrl(valStr)) err = "Please enter a valid URL (e.g. http://localhost:5173)"
        break
      case 'timezone_default':
        if (!valStr) err = "Default Timezone is required"
        else if (!validateTimezone(valStr)) err = "Please enter a valid IANA timezone (e.g. Asia/Kolkata, UTC)"
        break
      default:
        break
    }
    return err
  }

  const handleBlur = (field) => {
    setTouched(prev => ({ ...prev, [field]: true }))
    const err = runValidation(field, form[field])
    setValidationErrors(prev => ({ ...prev, [field]: err }))
  }

  const handleChange = (field, val) => {
    setForm(prev => ({ ...prev, [field]: val }))
    if (touched[field]) {
      const err = runValidation(field, val)
      setValidationErrors(prev => ({ ...prev, [field]: err }))
    }
  }

  const loadSettings = async () => {
    setLoading(true)
    setError('')
    setSuccess('')
    setTouched({})
    setValidationErrors({})
    try {
      const data = await getSettings()
      setForm({
        zoom_account_id: data.zoom_account_id || '',
        zoom_client_id: data.zoom_client_id || '',
        zoom_client_secret: data.zoom_client_secret_set ? '••••••••' : '',
        zoom_user_id: data.zoom_user_id || '',
        google_calendar_id: data.google_calendar_id || '',
        google_sheet_id: data.google_sheet_id || '',
        smtp_host: data.smtp_host || '',
        smtp_port: data.smtp_port || 587,
        smtp_username: data.smtp_username || '',
        smtp_password: data.smtp_password_set ? '••••••••' : '',
        smtp_from: data.smtp_from || '',
        app_url: data.app_url || '',
        timezone_default: data.timezone_default || 'Asia/Kolkata',
        gemini_api_key: data.gemini_api_key_set ? '••••••••' : '',
      })
    } catch (err) {
      setError(err.message || 'Failed to load system settings.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSettings()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    // Validate all fields
    const errors = {}
    Object.keys(form).forEach(key => {
      const err = runValidation(key, form[key])
      if (err) errors[key] = err
    })

    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors)
      const touchedFields = {}
      Object.keys(form).forEach(key => {
        touchedFields[key] = true
      })
      setTouched(touchedFields)
      setError("Please fix the validation errors on the form before submitting.")
      return
    }

    setSaveLoading(true)

    try {
      const payload = {
        ...form,
        smtp_port: parseInt(form.smtp_port, 10)
      }
      const res = await updateSettings(payload)
      setSuccess(res.message || 'System configurations successfully updated! Restarting server to apply.')
      // Refresh settings shortly
      setTimeout(() => {
        loadSettings()
      }, 1500)
    } catch (err) {
      setError(err.message || 'Failed to update system settings.')
    } finally {
      setSaveLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <div className="space-y-4 text-center">
          <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-slate-400 text-sm font-bold tracking-wider">Loading settings panel...</p>
        </div>
      </div>
    )
  }

  const renderInputField = ({ label, field, type = "text", placeholder = "", helper = "", colSpan = "" }) => {
    const isInvalid = touched[field] && validationErrors[field]
    return (
      <div className={`space-y-2 ${colSpan}`}>
        <label className="text-xs font-black text-slate-400 uppercase tracking-wider">{label}</label>
        {helper && <p className="text-[11px] text-slate-400 font-medium -mt-1">{helper}</p>}
        <input
          type={type}
          placeholder={placeholder}
          value={form[field]}
          onBlur={() => handleBlur(field)}
          onChange={(e) => handleChange(field, type === "number" ? parseInt(e.target.value, 10) || "" : e.target.value)}
          className={`w-full bg-slate-50 border rounded-2xl px-6 py-4 text-sm font-bold transition-all outline-none ${
            isInvalid
              ? 'border-red-300 bg-red-50/30 text-red-900 focus:border-red-500 focus:ring-4 focus:ring-red-500/5'
              : 'border-slate-100 text-slate-700 focus:bg-white focus:border-indigo-100 focus:ring-4 focus:ring-indigo-500/5'
          }`}
        />
        {isInvalid && (
          <p className="text-xs font-medium text-red-500 mt-1 flex items-center gap-1">
            <AlertCircle size={12} /> {validationErrors[field]}
          </p>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-10 animate-in fade-in duration-700 max-w-5xl">
      <div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">System Settings</h1>
        <p className="text-slate-500 font-medium mt-1">Configure Zoom API, Google Calendars, email verification, and system parameters.</p>
      </div>

      {error && (
        <div className="p-5 bg-red-50 border border-red-100 rounded-[1.5rem] flex items-center gap-4 text-red-700 animate-in fade-in slide-in-from-top-6 duration-300">
          <div className="p-2 bg-red-100 rounded-xl"><AlertCircle size={24} /></div>
          <div>
            <p className="text-sm font-black">Something went wrong</p>
            <p className="text-xs font-medium opacity-80">{error}</p>
          </div>
        </div>
      )}

      {success && (
        <div className="p-5 bg-emerald-50 border border-emerald-100 rounded-[1.5rem] flex items-center gap-4 text-emerald-700 animate-in fade-in slide-in-from-top-6 duration-300">
          <div className="p-2 bg-emerald-100 rounded-xl"><CheckCircle size={24} /></div>
          <div>
            <p className="text-sm font-black">Success</p>
            <p className="text-xs font-medium opacity-80">{success}</p>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-10 pb-20">
        {/* Section 1: Zoom */}
        <section className="bg-white rounded-[2.5rem] border border-slate-100 p-8 shadow-xl shadow-slate-200/40 space-y-6">
          <div className="flex items-center gap-3 pb-4 border-b border-slate-50">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl"><Video size={20} /></div>
            <div>
              <h3 className="font-black text-lg text-slate-900 tracking-tight">Zoom Server-to-Server OAuth</h3>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-0.5">Integration Credentials</p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {renderInputField({
              label: "Account ID",
              field: "zoom_account_id"
            })}
            {renderInputField({
              label: "Client ID",
              field: "zoom_client_id"
            })}
            {renderInputField({
              label: "Client Secret",
              field: "zoom_client_secret",
              type: "password",
              placeholder: form.zoom_client_secret === '••••••••' ? '••••••••' : 'Enter Secret'
            })}
            {renderInputField({
              label: "Host User Email (Host ID)",
              field: "zoom_user_id",
              type: "email"
            })}
          </div>
        </section>

        {/* Section 2: Google Integrations */}
        <section className="bg-white rounded-[2.5rem] border border-slate-100 p-8 shadow-xl shadow-slate-200/40 space-y-6">
          <div className="flex items-center gap-3 pb-4 border-b border-slate-50">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl"><Calendar size={20} /></div>
            <div>
              <h3 className="font-black text-lg text-slate-900 tracking-tight">Google Calendar & Sheets</h3>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-0.5">Resource Identifiers</p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {renderInputField({
              label: "Target Calendar ID (Email or 'primary')",
              field: "google_calendar_id"
            })}
            {renderInputField({
              label: "Google Sheets Spreadsheet ID",
              field: "google_sheet_id"
            })}
          </div>
        </section>

        {/* Section 3: SMTP Credentials */}
        <section className="bg-white rounded-[2.5rem] border border-slate-100 p-8 shadow-xl shadow-slate-200/40 space-y-6">
          <div className="flex items-center gap-3 pb-4 border-b border-slate-50">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl"><Mail size={20} /></div>
            <div>
              <h3 className="font-black text-lg text-slate-900 tracking-tight">SMTP Mail Server (Verification & Password Resets)</h3>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-0.5">Email Delivery configuration</p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {renderInputField({
              label: "SMTP Host",
              field: "smtp_host"
            })}
            {renderInputField({
              label: "SMTP Port",
              field: "smtp_port",
              type: "number"
            })}
            {renderInputField({
              label: "SMTP Sender Email Address (From)",
              field: "smtp_from",
              type: "email"
            })}
            {renderInputField({
              label: "SMTP Username (Login)",
              field: "smtp_username",
              colSpan: "md:col-span-2"
            })}
            {renderInputField({
              label: "SMTP Password (App Password)",
              field: "smtp_password",
              type: "password",
              placeholder: form.smtp_password === '••••••••' ? '••••••••' : 'Enter Password'
            })}
          </div>
        </section>

        {/* Section 4: General Systems */}
        <section className="bg-white rounded-[2.5rem] border border-slate-100 p-8 shadow-xl shadow-slate-200/40 space-y-6">
          <div className="flex items-center gap-3 pb-4 border-b border-slate-50">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl"><Globe size={20} /></div>
            <div>
              <h3 className="font-black text-lg text-slate-900 tracking-tight">System Environment</h3>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-0.5">Parameters & Links</p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {renderInputField({
              label: "Application Host URL (Client URL)",
              field: "app_url",
              helper: "Must match the URL clients visit (e.g. http://localhost:5173)"
            })}
            {renderInputField({
              label: "Default Core Timezone",
              field: "timezone_default",
              helper: "Valid IANA timezone format (e.g. Asia/Kolkata, UTC, America/New_York)"
            })}
          </div>
        </section>

        {/* Section 5: Gemini AI */}
        <section className="bg-white rounded-[2.5rem] border border-slate-100 p-8 shadow-xl shadow-slate-200/40 space-y-6">
          <div className="flex items-center gap-3 pb-4 border-b border-slate-50">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl"><Sparkles size={20} /></div>
            <div>
              <h3 className="font-black text-lg text-slate-900 tracking-tight">Gemini Generative AI</h3>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-0.5">Google AI Integrations</p>
            </div>
          </div>
          <div className="grid grid-cols-1 gap-6">
            {renderInputField({
              label: "Google Gemini API Key",
              field: "gemini_api_key",
              type: "password",
              placeholder: form.gemini_api_key === '••••••••' ? '••••••••' : 'Enter Gemini API Key',
              helper: "Used for Natural Language Smart Scheduling and the AI Floating Learning Assistant."
            })}
          </div>
        </section>

        {/* Action Bottom */}
        <div className="flex justify-end gap-4">
          <button
            type="button"
            onClick={loadSettings}
            disabled={saveLoading}
            className="flex items-center gap-2 px-8 py-4 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-2xl text-sm font-black transition-all active:scale-95 cursor-pointer"
          >
            <RefreshCw size={16} />
            Discard Changes
          </button>
          <button
            type="submit"
            disabled={saveLoading}
            className="flex items-center gap-2 px-10 py-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl text-sm font-black transition-all shadow-xl shadow-indigo-600/10 active:scale-95 cursor-pointer"
          >
            {saveLoading ? 'Saving...' : (
              <>
                <Save size={16} />
                Save Configurations
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
