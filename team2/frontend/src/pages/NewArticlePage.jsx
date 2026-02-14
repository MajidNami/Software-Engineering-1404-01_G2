import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { PlusCircle, Loader2 } from 'lucide-react'
import { api } from '../api'

export default function NewArticlePage() {
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!name.trim()) return

    setLoading(true)
    setError('')
    try {
      const data = await api.createArticle(name.trim())
      navigate(`/articles/${encodeURIComponent(data.name)}`)
    } catch (err) {
      setError(err.data?.detail || 'خطا در ایجاد مقاله. مطمئن شوید وارد حساب کاربری خود شده‌اید.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-16">
      <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-forest/10 rounded-lg">
            <PlusCircle className="w-6 h-6 text-forest" />
          </div>
          <h1 className="text-xl font-bold text-dark">ایجاد مقاله جدید</h1>
        </div>

        <form onSubmit={handleSubmit}>
          <label className="block text-sm font-medium text-gray-600 mb-2">
            نام مقاله
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="مثلاً: مقاله-اول-من"
            className="w-full bg-gray-50 border border-gray-300 rounded-xl py-3 px-4 text-dark placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-forest focus:border-transparent"
          />

          {error && (
            <p className="mt-3 text-red-600 text-sm">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="mt-6 w-full bg-forest hover:bg-leaf text-white font-medium py-3 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                در حال ایجاد...
              </>
            ) : (
              'ایجاد مقاله'
            )}
          </button>
        </form>
      </div>
    </div>
  )
}
