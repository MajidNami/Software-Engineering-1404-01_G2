import { useState } from 'react'
import { useAuth } from '../../hooks/useAuth'

function AuthModal({ mode = 'login', onClose }) {
  const [activeTab, setActiveTab] = useState(mode)
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { login, register } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      if (activeTab === 'login') {
        await login({ username: form.username, password: form.password })
      } else {
        await register({ username: form.username, email: form.email, password: form.password })
      }
      onClose()
    } catch (err) {
      const msg = err?.response?.data?.error || 'خطا در احراز هویت'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(4,10,20,0.76)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 20, padding: 16 }}>
      <div className="glass" style={{ width: '100%', maxWidth: 420, padding: 24 }}>
        <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
          <button
            className="btn btn-ghost"
            style={{ flex: 1, background: activeTab === 'login' ? 'rgba(74,194,154,0.18)' : undefined }}
            onClick={() => setActiveTab('login')}
          >
            ورود
          </button>
          <button
            className="btn btn-ghost"
            style={{ flex: 1, background: activeTab === 'register' ? 'rgba(74,194,154,0.18)' : undefined }}
            onClick={() => setActiveTab('register')}
          >
            ثبت‌نام
          </button>
        </div>

        <form onSubmit={handleSubmit} className="grid" style={{ gap: 12 }}>
          <input
            className="input"
            placeholder="نام کاربری"
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
            required
          />
          {activeTab === 'register' && (
            <input
              className="input"
              type="email"
              placeholder="ایمیل"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
            />
          )}
          <input
            className="input"
            type="password"
            placeholder="رمز عبور"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            minLength={8}
            required
          />

          {error && <div style={{ color: '#f66', fontSize: 13 }}>{error}</div>}

          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn btn-primary" style={{ flex: 1 }} disabled={loading}>
              {loading ? '...' : 'تایید'}
            </button>
            <button type="button" className="btn btn-ghost" onClick={onClose} disabled={loading}>
              بستن
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default AuthModal
