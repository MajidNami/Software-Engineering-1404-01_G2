import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Save, Send, ArrowRight, Loader2, Eye } from 'lucide-react'
import { api } from '../api'

export default function EditVersionPage() {
  const { name } = useParams()
  const [version, setVersion] = useState(null)
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(true)
  const [saveLoading, setSaveLoading] = useState(false)
  const [publishLoading, setPublishLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [isCreator, setIsCreator] = useState(null)

  useEffect(() => {
    const fetchVersion = async () => {
      setLoading(true)
      try {
        const data = await api.getVersion(name)
        setVersion(data)
        setContent(data.content || '')
        setError('')

        const article = await api.getArticle(data.article)
        try {
          const myArts = await api.myArticles()
          if (myArts && myArts.length > 0) {
            setIsCreator(String(article.creator_id) === String(myArts[0].creator_id))
          } else {
            setIsCreator(false)
          }
        } catch {
          setIsCreator(false)
        }
      } catch (err) {
        setError('خطا در بارگذاری نسخه.')
      } finally {
        setLoading(false)
      }
    }
    fetchVersion()
  }, [name])

  const handleSave = async () => {
    setSaveLoading(true)
    setMessage('')
    try {
      const data = await api.updateVersion(name, content)
      setVersion(data)
      setMessage('محتوا با موفقیت ذخیره شد!')
    } catch (err) {
      setMessage(err.data?.detail || 'خطا در ذخیره محتوا.')
    } finally {
      setSaveLoading(false)
    }
  }

  const handlePublish = async () => {
    setPublishLoading(true)
    setMessage('')
    try {
      await api.updateVersion(name, content)
      if (isCreator) {
        await api.publishVersion(name)
        setMessage('نسخه با موفقیت منتشر شد!')
      } else {
        await api.requestPublish(name)
        setMessage('درخواست انتشار با موفقیت ارسال شد!')
      }
    } catch (err) {
      setMessage(err.data?.detail || 'خطا در انتشار نسخه.')
    } finally {
      setPublishLoading(false)
    }
  }

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
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between flex-wrap gap-3 mb-6">
        <div>
          <h1 className="text-xl font-bold text-dark">ویرایش نسخه: {version.name}</h1>
          <p className="text-sm text-gray-500 mt-1">
            مقاله: <span className="text-forest font-medium">{version.article}</span>
          </p>
        </div>
        <div className="flex items-center gap-2">
          {version.article && (
            <Link
              to={`/articles/${encodeURIComponent(version.article)}/manage`}
              className="inline-flex items-center gap-1.5 bg-gray-200 hover:bg-gray-300 text-dark text-sm font-medium px-4 py-2 rounded-lg transition-colors"
            >
              <ArrowRight className="w-4 h-4" />
              بازگشت به مدیریت
            </Link>
          )}
          <Link
            to={`/versions/${encodeURIComponent(name)}/preview`}
            className="inline-flex items-center gap-1.5 bg-gray-200 hover:bg-gray-300 text-dark text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            <Eye className="w-4 h-4" />
            پیش‌نمایش
          </Link>
          <button
            onClick={handleSave}
            disabled={saveLoading}
            className="inline-flex items-center gap-1.5 bg-gold hover:bg-yellow-500 text-dark text-sm font-medium px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {saveLoading ? 'در حال ذخیره...' : 'ذخیره'}
          </button>
          <button
            onClick={handlePublish}
            disabled={publishLoading}
            className="inline-flex items-center gap-1.5 bg-forest hover:bg-leaf text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
            {publishLoading
              ? (isCreator ? 'در حال انتشار...' : 'در حال ارسال...')
              : (isCreator ? 'انتشار' : 'درخواست انتشار')}
          </button>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
        <div className="border-b border-gray-200 px-4 py-2 bg-gray-50">
          <span className="text-xs font-medium text-gray-500">Markdown Editor</span>
        </div>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          dir="auto"
          className="w-full min-h-[60vh] p-5 text-sm text-dark leading-relaxed resize-y focus:outline-none"
          placeholder="محتوای مارک‌داون خود را اینجا بنویسید..."
        />
      </div>

      {message && (
        <div className="mt-4 bg-white border border-gray-200 rounded-lg p-3 text-sm text-center text-gray-700 shadow-sm">
          {message}
        </div>
      )}

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
