import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Edit3, ArrowRight, Loader2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { api } from '../api'

export default function ArticlePage() {
  const { name } = useParams()
  const [article, setArticle] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchArticle = async () => {
      setLoading(true)
      try {
        const data = await api.getArticle(name)
        setArticle(data)
        setError('')
      } catch (err) {
        setError('خطا در بارگذاری مقاله.')
      } finally {
        setLoading(false)
      }
    }
    fetchArticle()
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

  const currentVersion = article?.current_version
  const content = currentVersion?.content || ''
  const summary = currentVersion?.summary || ''
  const tags = currentVersion?.tags || []

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between flex-wrap gap-3 mb-6">
        <div>
          <h1 className="text-xl font-bold text-dark">{article.name}</h1>
          <p className="text-sm text-gray-500 mt-1">
            ایجادکننده: <span className="text-gray-700">{article.creator_id}</span>
            {currentVersion && (
              <> · نسخه فعلی: <span className="text-forest font-medium">{currentVersion.name}</span></>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to={`/articles/${encodeURIComponent(name)}/manage`}
            className="inline-flex items-center gap-1.5 bg-forest hover:bg-leaf text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            <Edit3 className="w-4 h-4" />
            ویرایش
          </Link>
        </div>
      </div>

      {summary && (
        <div className="bg-light border border-gray-200 rounded-xl p-4 mb-4">
          <h3 className="text-sm font-semibold text-gray-600 mb-1">خلاصه</h3>
          <p className="text-gray-700 text-sm">{summary}</p>
        </div>
      )}

      {tags.length > 0 && (
        <div className="flex items-center gap-2 flex-wrap mb-4">
          {tags.map((tag) => (
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
          <span className="text-xs font-medium text-gray-500">محتوای مقاله</span>
        </div>
        <div className="p-6" dir="auto">
          {content ? (
            <div className="prose prose-sm max-w-none prose-headings:text-dark prose-p:text-gray-700 prose-a:text-forest prose-strong:text-dark prose-code:bg-gray-100 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-pre:bg-gray-900 prose-pre:text-gray-100">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {content}
              </ReactMarkdown>
            </div>
          ) : (
            <p className="text-gray-500 text-sm text-center py-8">هنوز محتوایی ثبت نشده است.</p>
          )}
        </div>
      </div>

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
