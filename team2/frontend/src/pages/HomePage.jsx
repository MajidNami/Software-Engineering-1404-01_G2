import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, FileText, ArrowRight } from 'lucide-react'
import { api } from '../api'

export default function HomePage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    setLoading(true)
    setError('')
    try {
      await api.getArticle(searchQuery.trim())
      navigate(`/articles/${encodeURIComponent(searchQuery.trim())}`)
    } catch (err) {
      if (err.status === 404) {
        setError('مقاله‌ای با این نام یافت نشد.')
      } else {
        setError('خطایی رخ داد. مطمئن شوید وارد حساب کاربری خود شده‌اید.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col">
      <section className="flex-1 flex flex-col items-center justify-center px-4 py-20">
        <div className="text-center max-w-2xl mx-auto">
          <div className="mb-6">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-forest/10 mb-6">
              <FileText className="w-10 h-10 text-forest" />
            </div>
          </div>

          <h1 className="text-4xl sm:text-5xl font-bold text-dark mb-4 leading-tight">
            دانشنامه (ویکی)
          </h1>
          <p className="text-gray-600 text-lg mb-10">
            نام مقاله را جستجو کنید تا آن را مشاهده، ویرایش یا رأی‌گیری کنید.
          </p>

          <form onSubmit={handleSearch} className="w-full max-w-lg mx-auto">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="نام مقاله را وارد کنید..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-white border border-gray-300 rounded-xl py-3.5 pr-4 pl-12 text-dark placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-forest focus:border-transparent"
              />
            </div>
            {error && (
              <p className="mt-3 text-red-600 text-sm">{error}</p>
            )}
            <button
              type="submit"
              disabled={loading}
              className="mt-4 w-full bg-forest hover:bg-leaf text-white font-medium py-3 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'در حال جستجو...' : 'جستجوی مقاله'}
            </button>
          </form>
        </div>
      </section>

      <footer className="border-t border-gray-300 py-6 text-center">
        <a
          href="/"
          className="inline-flex items-center gap-2 text-gray-500 hover:text-forest transition-colors text-sm"
        >
          <ArrowRight className="w-4 h-4" />
          بازگشت به داشبورد اصلی
        </a>
      </footer>
    </div>
  )
}
