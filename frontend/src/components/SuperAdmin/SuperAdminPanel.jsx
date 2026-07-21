import { useState, useEffect } from 'react'
import { 
  Users, 
  Shield, 
  Trash2, 
  Power, 
  PowerOff, 
  Check, 
  AlertCircle, 
  Eye, 
  EyeOff, 
  Key, 
  Mail, 
  Video, 
  Database,
  Calendar,
  Sparkles
} from 'lucide-react'
import { listTenants, toggleTenantActive, deleteTenant } from '../../services/api'

export function SuperAdminPanel() {
  const [tenants, setTenants] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [expandedTenantId, setExpandedTenantId] = useState(null)
  const [showSecretId, setShowSecretId] = useState({})

  useEffect(() => {
    fetchTenants()
  }, [])

  const fetchTenants = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await listTenants()
      setTenants(data)
    } catch (err) {
      setError(err.message || 'Failed to fetch tenants list.')
    } finally {
      setLoading(false)
    }
  }

  const handleToggleActive = async (tenantId) => {
    setError('')
    setSuccess('')
    try {
      const res = await toggleTenantActive(tenantId)
      setSuccess(res.message)
      setTenants(prev => prev.map(t => t.id === tenantId ? { ...t, is_active: res.is_active } : t))
      setTimeout(() => setSuccess(''), 4000)
    } catch (err) {
      setError(err.message || 'Failed to toggle tenant active status.')
    }
  }

  const handleDeleteTenant = async (tenantId, email) => {
    if (!window.confirm(`WARNING: Are you sure you want to permanently delete tenant admin "${email}"? This will cascadingly delete all their settings, classes, courses, and users, and cancel their subscription.`)) {
      return
    }
    setError('')
    setSuccess('')
    try {
      const res = await deleteTenant(tenantId)
      setSuccess(res.message)
      setTenants(prev => prev.filter(t => t.id !== tenantId))
      setTimeout(() => setSuccess(''), 4000)
    } catch (err) {
      setError(err.message || 'Failed to delete tenant.')
    }
  }

  const toggleShowSecret = (tenantId, field) => {
    const key = `${tenantId}-${field}`
    setShowSecretId(prev => ({ ...prev, [key]: !prev[key] }))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="space-y-4 text-center">
          <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-slate-400 text-xs font-bold tracking-wider">Loading tenants data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500 max-w-7xl mx-auto">
      {/* Premium Header Card */}
      <div className="relative overflow-hidden bg-slate-900 text-white rounded-[2rem] p-8 md:p-10 shadow-2xl shadow-slate-950/20">
        <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-indigo-600/10 rounded-full blur-3xl -ml-20 -mb-20 pointer-events-none" />
        
        <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full text-xs font-black text-indigo-400 uppercase tracking-widest">
              <Shield size={12} /> Master Admin Controls
            </div>
            <h1 className="text-3xl md:text-4xl font-black tracking-tight">SaaS Tenant Management</h1>
            <p className="text-slate-400 text-sm max-w-2xl font-medium leading-relaxed">
              Deactivate subscription accounts instantly, view configured Zoom & SMTP integrations, or delete inactive organizations.
            </p>
          </div>
          
          <div className="flex gap-4">
            <div className="p-4 bg-slate-800/50 border border-slate-700/30 rounded-2xl text-center min-w-[100px]">
              <span className="block text-2xl font-black text-white">{tenants.length}</span>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Total Tenants</span>
            </div>
            <div className="p-4 bg-slate-800/50 border border-slate-700/30 rounded-2xl text-center min-w-[100px]">
              <span className="block text-2xl font-black text-emerald-400">
                {tenants.filter(t => t.is_active).length}
              </span>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Active SaaS</span>
            </div>
          </div>
        </div>
      </div>

      {/* Action alerts */}
      {success && (
        <div className="p-5 bg-emerald-50 border border-emerald-100 rounded-[1.5rem] flex items-center gap-4 text-emerald-700 animate-in slide-in-from-top-6 duration-300">
          <div className="p-2 bg-emerald-100 rounded-xl"><Check size={20} /></div>
          <div>
            <p className="text-sm font-black">Success</p>
            <p className="text-xs font-medium opacity-90">{success}</p>
          </div>
        </div>
      )}

      {error && (
        <div className="p-5 bg-red-50 border border-red-100 rounded-[1.5rem] flex items-center gap-4 text-red-700 animate-in slide-in-from-top-6 duration-300">
          <div className="p-2 bg-red-100 rounded-xl"><AlertCircle size={20} /></div>
          <div>
            <p className="text-sm font-black">Error</p>
            <p className="text-xs font-medium opacity-90">{error}</p>
          </div>
        </div>
      )}

      {/* Tenants Table Grid */}
      <div className="bg-white border border-slate-100 rounded-[2rem] overflow-hidden shadow-sm">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <h3 className="font-black text-lg text-slate-900">Registered SaaS Organizations</h3>
          <button 
            onClick={fetchTenants}
            className="px-4 py-2 bg-slate-50 hover:bg-slate-100 text-slate-700 rounded-xl text-xs font-black transition-colors"
          >
            Refresh List
          </button>
        </div>

        {tenants.length === 0 ? (
          <div className="text-center py-20 text-slate-400 space-y-2">
            <Users size={40} className="mx-auto text-slate-300" />
            <p className="text-sm font-bold">No tenants found</p>
            <p className="text-xs">Once users register admin accounts, they will appear here.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/50 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                  <th className="py-4 px-6">Tenant Email</th>
                  <th className="py-4 px-6">Active Status</th>
                  <th className="py-4 px-6 text-center">Courses</th>
                  <th className="py-4 px-6 text-center">Classes</th>
                  <th className="py-4 px-6">Integrations Status</th>
                  <th className="py-4 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm font-semibold text-slate-700">
                {tenants.map(tenant => {
                  const isExpanded = expandedTenantId === tenant.id
                  return (
                    <>
                      <tr 
                        key={tenant.id}
                        className={`hover:bg-slate-50/30 transition-all ${isExpanded ? 'bg-slate-50/30' : ''}`}
                      >
                        <td 
                          onClick={() => setExpandedTenantId(isExpanded ? null : tenant.id)}
                          className="py-5 px-6 cursor-pointer"
                        >
                          <div className="font-black text-slate-950">{tenant.email}</div>
                          <div className="text-[10px] text-slate-400 font-bold mt-1">ID: {tenant.id}</div>
                        </td>
                        
                        <td className="py-5 px-6">
                          <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-black uppercase tracking-wider ${
                            tenant.is_active 
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' 
                              : 'bg-red-50 text-red-600 border border-red-100'
                          }`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${tenant.is_active ? 'bg-emerald-500' : 'bg-red-500'}`} />
                            {tenant.is_active ? 'Active' : 'Deactivated'}
                          </span>
                        </td>
                        
                        <td className="py-5 px-6 text-center font-black text-indigo-600">
                          {tenant.courses_count}
                        </td>
                        
                        <td className="py-5 px-6 text-center font-black text-indigo-600">
                          {tenant.classes_count}
                        </td>
                        
                        <td className="py-5 px-6">
                          <div className="flex gap-2">
                            <span title="Zoom Configured" className={`p-1.5 rounded-lg border ${
                              tenant.settings.zoom_configured
                                ? 'bg-indigo-50 border-indigo-100 text-indigo-600'
                                : 'bg-slate-50 border-slate-100 text-slate-300'
                            }`}><Video size={16} /></span>
                            <span title="SMTP Configured" className={`p-1.5 rounded-lg border ${
                              tenant.settings.smtp_configured
                                ? 'bg-indigo-50 border-indigo-100 text-indigo-600'
                                : 'bg-slate-50 border-slate-100 text-slate-300'
                            }`}><Mail size={16} /></span>
                            <span title="Google Sheet Active" className={`p-1.5 rounded-lg border ${
                              tenant.settings.google_sheet_id
                                ? 'bg-indigo-50 border-indigo-100 text-indigo-600'
                                : 'bg-slate-50 border-slate-100 text-slate-300'
                            }`}><Database size={16} /></span>
                            <span title="Gemini Active" className={`p-1.5 rounded-lg border ${
                              tenant.settings.gemini_configured
                                ? 'bg-indigo-50 border-indigo-100 text-indigo-600'
                                : 'bg-slate-50 border-slate-100 text-slate-300'
                            }`}><Sparkles size={16} /></span>
                          </div>
                        </td>

                        <td className="py-5 px-6 text-right">
                          <div className="flex justify-end gap-2">
                            <button
                              onClick={() => setExpandedTenantId(isExpanded ? null : tenant.id)}
                              className="px-3.5 py-2 bg-slate-50 hover:bg-slate-100 border border-slate-200/50 text-slate-700 rounded-xl text-xs font-black transition-colors"
                            >
                              {isExpanded ? 'Hide Credentials' : 'View Configs'}
                            </button>
                            <button
                              onClick={() => handleToggleActive(tenant.id)}
                              className={`p-2 border rounded-xl transition-all cursor-pointer ${
                                tenant.is_active
                                  ? 'bg-amber-50 hover:bg-amber-100 border-amber-200 text-amber-600'
                                  : 'bg-emerald-50 hover:bg-emerald-100 border-emerald-200 text-emerald-700'
                              }`}
                              title={tenant.is_active ? 'Cancel Subscription (Deactivate)' : 'Restore Subscription (Activate)'}
                            >
                              {tenant.is_active ? <PowerOff size={16} /> : <Power size={16} />}
                            </button>
                            <button
                              onClick={() => handleDeleteTenant(tenant.id, tenant.email)}
                              className="p-2 bg-red-50 hover:bg-red-100 border border-red-200 text-red-600 rounded-xl transition-all cursor-pointer"
                              title="Delete Tenant and All Data"
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        </td>
                      </tr>

                      {/* Expanded Credentials View */}
                      {isExpanded && (
                        <tr className="bg-slate-50/20">
                          <td colSpan="6" className="p-6 border-t border-b border-slate-100">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-slate-600">
                              
                              {/* Zoom Configs */}
                              <div className="bg-white p-5 border border-slate-100 rounded-2xl shadow-sm space-y-4">
                                <div className="flex items-center gap-2 border-b border-slate-50 pb-2">
                                  <Video size={16} className="text-indigo-600" />
                                  <h4 className="font-black text-slate-900">Zoom API Integrations</h4>
                                </div>
                                <div className="space-y-2">
                                  <div className="flex justify-between">
                                    <span className="font-bold text-slate-400">Account ID:</span>
                                    <span className="font-bold text-slate-800">{tenant.settings.zoom_user_id || 'Not configured'}</span>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="font-bold text-slate-400">Client ID:</span>
                                    <span className="font-bold text-slate-800">{tenant.settings.zoom_configured ? 'Configured' : 'Not configured'}</span>
                                  </div>
                                </div>
                              </div>

                              {/* SMTP Configs */}
                              <div className="bg-white p-5 border border-slate-100 rounded-2xl shadow-sm space-y-4">
                                <div className="flex items-center gap-2 border-b border-slate-50 pb-2">
                                  <Mail size={16} className="text-indigo-600" />
                                  <h4 className="font-black text-slate-900">SMTP Notification Config</h4>
                                </div>
                                <div className="space-y-2">
                                  <div className="flex justify-between">
                                    <span className="font-bold text-slate-400">SMTP Host:</span>
                                    <span className="font-bold text-slate-800">{tenant.settings.smtp_host || 'Not configured'}</span>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="font-bold text-slate-400">Sender Email:</span>
                                    <span className="font-bold text-slate-800">{tenant.settings.smtp_from || 'Not configured'}</span>
                                  </div>
                                </div>
                              </div>

                              {/* Google Drive Configs */}
                              <div className="bg-white p-5 border border-slate-100 rounded-2xl shadow-sm space-y-4 md:col-span-2">
                                <div className="flex items-center gap-2 border-b border-slate-50 pb-2">
                                  <Database size={16} className="text-indigo-600" />
                                  <h4 className="font-black text-slate-900">Google Sheet Sync Configuration</h4>
                                </div>
                                <div className="space-y-2">
                                  <div className="flex flex-col gap-1">
                                    <span className="font-bold text-slate-400">Active Google Sheet ID:</span>
                                    <span className="font-bold text-slate-800 block break-all font-mono py-1 px-2 bg-slate-50 rounded border border-slate-100">
                                      {tenant.settings.google_sheet_id || 'Not configured'}
                                    </span>
                                  </div>
                                  <div className="flex flex-col gap-1 mt-2">
                                    <span className="font-bold text-slate-400">Google Calendar Event Sync Target:</span>
                                    <span className="font-bold text-slate-800 block break-all font-mono py-1 px-2 bg-slate-50 rounded border border-slate-100">
                                      {tenant.settings.google_calendar_id || 'Not configured'}
                                    </span>
                                  </div>
                                </div>
                              </div>

                            </div>
                          </td>
                        </tr>
                      )}
                    </>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
