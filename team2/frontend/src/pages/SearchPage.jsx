import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, ArrowRight, Loader2, FileText } from 'lucide-react'
import { api } from '../api'

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError('')
    setResults(null)
    try {
      const data = await api.searchArticles(query.trim())
      setResults(data.results || [])
    } catch (err) {
      setError(err.data?.detail || 'خطا در جستجو. مطمئن شوید وارد حساب کاربری خود شده‌اید.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-dark mb-2">جستجوی مقالات</h1>
        <p className="text-gray-500 text-sm">عبارت مورد نظر خود را وارد کنید تا مقالات مرتبط را پیدا کنید.</p>
      </div>

      <form onSubmit={handleSearch} className="w-full max-w-lg mx-auto mb-8">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="جستجو..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-white border border-gray-300 rounded-xl py-3.5 pr-4 pl-12 text-dark placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-forest focus:border-transparent"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="mt-4 w-full bg-forest hover:bg-leaf text-white font-medium py-3 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              در حال جستجو...
            </>
          ) : (
            'جستجو'
          )}
        </button>
      </form>

      {error && (
        <div className="text-center">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      {results !== null && (
        <div>
          {results.length > 0 ? (
            <div className="space-y-4">
              {results.map((item, idx) => (
                <Link
                  key={idx}
                  to={`/articles/${encodeURIComponent(item.article_name || item.name || item)}`}
                  className="block bg-white border border-gray-200 rounded-xl p-4 hover:border-forest transition-colors shadow-sm"
                >
                  <div className="flex items-start gap-3">
                    <FileText className="w-5 h-5 text-forest flex-shrink-0 mt-0.5" />
                    <div className="min-w-0 flex-1">
                      <span className="font-medium text-dark text-sm">
                        {item.article_name || item.name || item}
                      </span>
                      {item.summary && (
                        <div className="mt-2 bg-light border border-gray-100 rounded-lg p-3">
                          <p className="text-sm text-gray-600 leading-relaxed">{item.summary}</p>
                        </div>
                      )}
                      {item.tags && item.tags.length > 0 && (
                        <div className="flex items-center gap-1.5 flex-wrap mt-2">
                          {item.tags.map((tag, i) => (
                            <span
                              key={i}
                              className="bg-forest/10 text-forest text-xs font-medium px-2 py-0.5 rounded-full"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-500 text-sm">نتیجه‌ای یافت نشد.</p>
          )}
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
