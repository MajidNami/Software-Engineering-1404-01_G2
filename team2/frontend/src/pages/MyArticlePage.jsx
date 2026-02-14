import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { FileText, ArrowRight, Loader2 } from 'lucide-react'
import { api } from '../api'

export default function MyArticlePage() {
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchMyArticles = async () => {
      setLoading(true)
      try {
        const data = await api.myArticles()
        setArticles(data)
        setError('')
      } catch (err) {
        setError('خطا در بارگذاری مقالات. مطمئن شوید وارد حساب کاربری خود شده‌اید.')
      } finally {
        setLoading(false)
      }
    }
    fetchMyArticles()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 text-forest animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-dark mb-2">مقالات من</h1>
        <p className="text-gray-500 text-sm">مقالاتی که شما ایجاد کرده‌اید.</p>
      </div>

      {error && (
        <div className="text-center mb-6">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      {!error && articles.length === 0 && (
        <div className="text-center py-16">
          <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-sm mb-4">شما هنوز مقاله‌ای ایجاد نکرده‌اید.</p>
          <Link
            to="/articles/new"
            className="inline-flex items-center gap-2 bg-forest hover:bg-leaf text-white text-sm font-medium px-5 py-2.5 rounded-lg transition-colors"
          >
            ایجاد مقاله جدید
          </Link>
        </div>
      )}

      {articles.length > 0 && (
        <div className="space-y-3">
          {articles.map((article) => {
            const summary = article.current_version?.summary || ''

            return (
              <Link
                key={article.name}
                to={`/articles/${encodeURIComponent(article.name)}`}
                className="block bg-white border border-gray-200 rounded-xl p-4 hover:border-forest transition-colors shadow-sm"
              >
                <div className="flex items-start gap-3">
                  <FileText className="w-5 h-5 text-forest flex-shrink-0 mt-0.5" />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-medium text-dark text-sm">{article.name}</span>
                      <span className="text-xs text-gray-400 flex-shrink-0">
                        امتیاز: <span className="font-medium text-dark">{article.score}</span>
                      </span>
                    </div>
                    {summary && (
                      <p className="text-sm text-gray-600 mt-1.5 leading-relaxed">{summary}</p>
                    )}
                  </div>
                </div>
              </Link>
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
