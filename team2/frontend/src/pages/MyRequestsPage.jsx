import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ClipboardList, Eye, ArrowRight, Loader2 } from 'lucide-react'
import { api } from '../api'

const STATUS_MAP = {
  pending: { label: 'در انتظار', className: 'bg-amber-100 text-amber-700' },
  approved: { label: 'تأیید شده', className: 'bg-emerald-100 text-emerald-700' },
  rejected: { label: 'رد شده', className: 'bg-red-100 text-red-700' },
}

export default function MyRequestsPage() {
  const { name } = useParams()
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchRequests = async () => {
      setLoading(true)
      try {
        const data = await api.myPublishRequests(name)
        setRequests(data)
        setError('')
      } catch (err) {
        setError(err.data?.detail || 'خطا در بارگذاری درخواست‌ها.')
      } finally {
        setLoading(false)
      }
    }
    fetchRequests()
  }, [name])

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
          <h1 className="text-2xl font-bold text-dark mb-2">درخواست‌های من</h1>
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

      {!error && requests.length === 0 && (
        <div className="text-center py-16">
          <ClipboardList className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-sm">شما هنوز درخواست انتشاری ارسال نکرده‌اید.</p>
        </div>
      )}

      {requests.length > 0 && (
        <div className="space-y-3">
          {requests.map((req) => {
            const statusInfo = STATUS_MAP[req.status] || STATUS_MAP.pending
            return (
              <div
                key={req.id}
                className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm"
              >
                <div className="flex items-start justify-between flex-wrap gap-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-dark text-sm">{req.version_name}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${statusInfo.className}`}>
                        {statusInfo.label}
                      </span>
                    </div>
                    {req.version_summary && (
                      <p className="text-sm text-gray-600 mt-1">{req.version_summary}</p>
                    )}
                    <p className="text-xs text-gray-400 mt-1">
                      {new Date(req.created_at).toLocaleDateString('fa-IR')}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <Link
                      to={`/versions/${encodeURIComponent(req.version_name)}/preview`}
                      className="inline-flex items-center gap-1.5 bg-gray-200 hover:bg-gray-300 text-dark text-xs font-medium px-3 py-1.5 rounded-lg transition-colors"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      مشاهده نسخه
                    </Link>
                  </div>
                </div>
              </div>
            )
          })}
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
