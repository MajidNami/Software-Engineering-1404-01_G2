import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Inbox, Check, X, Eye, ArrowRight, Loader2 } from 'lucide-react'
import { api } from '../api'

export default function RequestPublishPage() {
  const { name } = useParams()
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionLoading, setActionLoading] = useState(null)
  const [message, setMessage] = useState('')

  const fetchRequests = async () => {
    setLoading(true)
    try {
      const data = await api.listPublishRequests(name)
      setRequests(data)
      setError('')
    } catch (err) {
      setError(err.data?.detail || 'خطا در بارگذاری درخواست‌ها.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRequests()
  }, [name])

  const handleApprove = async (pk) => {
    setActionLoading(pk)
    setMessage('')
    try {
      await api.approvePublishRequest(pk)
      setMessage('درخواست تأیید و نسخه منتشر شد!')
      await fetchRequests()
    } catch (err) {
      setMessage(err.data?.detail || 'خطا در تأیید درخواست.')
    } finally {
      setActionLoading(null)
    }
  }

  const handleReject = async (pk) => {
    setActionLoading(pk)
    setMessage('')
    try {
      await api.rejectPublishRequest(pk)
      setMessage('درخواست رد شد.')
      await fetchRequests()
    } catch (err) {
      setMessage(err.data?.detail || 'خطا در رد درخواست.')
    } finally {
      setActionLoading(null)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 text-forest animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-dark mb-2">درخواست‌های انتشار</h1>
          <p className="text-gray-500 text-sm">
            مقاله: <span className="text-forest font-medium">{name}</span>
          </p>
        </div>
        <Link
          to={`/articles/${encodeURIComponent(name)}/manage`}
          className="inline-flex items-center gap-1.5 bg-gray-200 hover:bg-gray-300 text-dark text-sm font-medium px-4 py-2 rounded-lg transition-colors"
        >
          بازگشت به مدیریت
        </Link>
      </div>

      {error && (
        <div className="text-center mb-6">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      {message && (
        <div className="mb-6 bg-white border border-gray-200 rounded-lg p-3 text-sm text-center text-gray-700 shadow-sm">
          {message}
        </div>
      )}

      {!error && requests.length === 0 && (
        <div className="text-center py-16">
          <Inbox className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-sm">درخواست انتشار در انتظاری وجود ندارد.</p>
        </div>
      )}

      {requests.length > 0 && (
        <div className="space-y-3">
          {requests.map((req) => (
            <div
              key={req.id}
              className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm"
            >
              <div className="flex items-start justify-between flex-wrap gap-3">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-dark text-sm">{req.version_name}</span>
                    <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full">
                      در انتظار
                    </span>
                  </div>
                  {req.version_summary && (
                    <p className="text-sm text-gray-600 mt-1">{req.version_summary}</p>
                  )}
                  <p className="text-xs text-gray-400 mt-1">
                    درخواست‌دهنده: {req.requester_id}
                  </p>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <Link
                    to={`/articles/${encodeURIComponent(name)}/requests/${req.id}/review`}
                    className="inline-flex items-center gap-1.5 bg-gray-200 hover:bg-gray-300 text-dark text-xs font-medium px-3 py-1.5 rounded-lg transition-colors"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    پیش‌نمایش
                  </Link>
                  <button
                    onClick={() => handleApprove(req.id)}
                    disabled={actionLoading === req.id}
                    className="inline-flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-medium px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
                  >
                    {actionLoading === req.id ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Check className="w-3.5 h-3.5" />
                    )}
                    تأیید
                  </button>
                  <button
                    onClick={() => handleReject(req.id)}
                    disabled={actionLoading === req.id}
                    className="inline-flex items-center gap-1.5 bg-red-500 hover:bg-red-600 text-white text-xs font-medium px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
                  >
                    {actionLoading === req.id ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <X className="w-3.5 h-3.5" />
                    )}
                    رد
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <footer className="border-t border-gray-300 mt-10 pt-6 text-center">
        <a
          href="http://localhost:8000"
          className="inline-flex items-center gap-2 text-gray-500 hover:text-forest transition-colors text-sm"
        >
          <ArrowRight className="w-4 h-4" />
          بازگشت به داشبورد اصلی
        </a>
      </footer>
    </div>
  )
}
