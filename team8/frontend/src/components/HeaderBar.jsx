import { useState } from 'react'
import AuthModal from './auth/AuthModal'
import { useAuth } from '../hooks/useAuth'

function HeaderBar({ onShowAuth }) {
  const { user, isAuthenticated, logout } = useAuth()
  const [authOpen, setAuthOpen] = useState(false)
  const [mode, setMode] = useState('login')

  const openAuth = (m) => {
    if (onShowAuth) {
      onShowAuth(m)
    } else {
      setMode(m)
      setAuthOpen(true)
    }
  }

  return (
    <>
      <header className="glass" style={{ padding: 16, marginBottom: 20, display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 40, height: 40, borderRadius: 12, background: 'linear-gradient(135deg, #4ac29a, #f7c948)', boxShadow: '0 10px 30px rgba(0,0,0,0.35)' }} />
          <div>
            <div style={{ fontWeight: 800, letterSpacing: 0.4 }}>سامانه گردشگری تیم ۸</div>
            <div style={{ color: '#9fb4d3', fontSize: 13 }}>نظرات، رسانه، امتیازدهی</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {isAuthenticated && user?.is_admin && (
            <a className="btn btn-ghost" href="/admin">
              بخش ادمین
            </a>
          )}
          {!isAuthenticated ? (
            <>
              <button className="btn btn-ghost" onClick={() => openAuth('login')}>
                ورود
              </button>
              <button className="btn btn-primary" onClick={() => openAuth('register')}>
                ثبت‌نام
              </button>
            </>
          ) : (
            <>
              <div className="pill-ghost">{user?.username}</div>
              <button className="btn btn-ghost" onClick={logout}>
                خروج
              </button>
            </>
          )}
        </div>
      </header>

      {!onShowAuth && authOpen && <AuthModal mode={mode} onClose={() => setAuthOpen(false)} />}
    </>
  )
}

export default HeaderBar
