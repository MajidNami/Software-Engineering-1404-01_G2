import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowRight, Loader2, Edit3 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { api } from '../api'

export default function PreviewVersionPage() {
  const { name } = useParams()
  const [version, setVersion] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchVersion = async () => {
      setLoading(true)
      try {
        const data = await api.getVersion(name)
        setVersion(data)
        setError('')
      } catch (err) {
        setError('خطا در بارگذاری نسخه.')
      } finally {
        setLoading(false)
      }
    }
    fetchVersion()
  }, [name])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 text-forest animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <p className="text-red-600 text-lg mb-4">{error}</p>
        <Link to="/" className="text-forest hover:text-leaf underline">
          بازگشت به خانه
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between flex-wrap gap-3 mb-6">
        <div>
          <h1 className="text-xl font-bold text-dark">پیش‌نمایش نسخه: {version.name}</h1>
          <p className="text-sm text-gray-500 mt-1">
            مقاله: <span className="text-forest font-medium">{version.article}</span>
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to={`/versions/${encodeURIComponent(name)}/edit`}
            className="inline-flex items-center gap-1.5 bg-forest hover:bg-leaf text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            <Edit3 className="w-4 h-4" />
            ویرایش
          </Link>
          {version.article && (
            <Link
              to={`/articles/${encodeURIComponent(version.article)}`}
              className="inline-flex items-center gap-1.5 bg-gray-200 hover:bg-gray-300 text-dark text-sm font-medium px-4 py-2 rounded-lg transition-colors"
            >
              بازگشت به مقاله
            </Link>
          )}
        </div>
      </div>

      {version.summary && (
        <div className="bg-light border border-gray-200 rounded-xl p-4 mb-4">
          <h3 className="text-sm font-semibold text-gray-600 mb-1">خلاصه</h3>
          <p className="text-gray-700 text-sm">{version.summary}</p>
        </div>
      )}

      {version.tags && version.tags.length > 0 && (
        <div className="flex items-center gap-2 flex-wrap mb-4">
          {version.tags.map((tag) => (
            <span
              key={tag.name}
              className="bg-forest/10 text-forest text-xs font-medium px-2.5 py-1 rounded-full"
            >
              {tag.name}
            </span>
          ))}
        </div>
      )}

      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
        <div className="border-b border-gray-200 px-4 py-2 bg-gray-50">
          <span className="text-xs font-medium text-gray-500">Markdown Preview</span>
        </div>
        <div className="p-6" dir="auto">
          {version.content ? (
            <div className="prose prose-sm max-w-none prose-headings:text-dark prose-p:text-gray-700 prose-a:text-forest prose-strong:text-dark prose-code:bg-gray-100 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-pre:bg-gray-900 prose-pre:text-gray-100">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {version.content}
              </ReactMarkdown>
            </div>
          ) : (
            <p className="text-gray-500 text-sm text-center py-8">هنوز محتوایی ثبت نشده است.</p>
          )}
        </div>
      </div>

      <p className="text-xs text-gray-500 mt-3">
        ویرایشگر: {version.editor_id}
      </p>

      <footer className="border-t border-gray-300 mt-8 pt-6 text-center">
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
