import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { GitBranch, Eye, Edit3, ArrowRight, Loader2, Plus, Send, Inbox, ClipboardList } from 'lucide-react'
import { api } from '../api'

export default function ManageArticlePage() {
  const { name } = useParams()
  const navigate = useNavigate()
  const [article, setArticle] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [newVersionSource, setNewVersionSource] = useState('')
  const [newVersionName, setNewVersionName] = useState('')
  const [createLoading, setCreateLoading] = useState(false)
  const [emptyVersionName, setEmptyVersionName] = useState('')
  const [emptyCreateLoading, setEmptyCreateLoading] = useState(false)
  const [publishLoading, setPublishLoading] = useState('')
  const [currentUserId, setCurrentUserId] = useState(null)

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

  useEffect(() => {
    fetchArticle()
    const fetchUser = async () => {
      try {
        const data = await api.myArticles()
        if (data && data.length > 0) {
          setCurrentUserId(data[0].creator_id)
        }
      } catch {}
    }
    fetchUser()
  }, [name])

  const isCreator = currentUserId && article && String(article.creator_id) === String(currentUserId)

  const handlePublish = async (versionName) => {
    setPublishLoading(versionName)
    setMessage('')
    try {
      await api.publishVersion(versionName)
      await fetchArticle()
      setMessage('نسخه با موفقیت منتشر شد!')
    } catch (err) {
      setMessage(err.data?.detail || 'خطا در انتشار نسخه.')
    } finally {
      setPublishLoading('')
    }
  }

  const handleRequestPublish = async (versionName) => {
    setPublishLoading(versionName)
    setMessage('')
    try {
      await api.requestPublish(versionName)
      setMessage('درخواست انتشار با موفقیت ارسال شد!')
    } catch (err) {
      setMessage(err.data?.detail || 'خطا در ارسال درخواست انتشار.')
    } finally {
      setPublishLoading('')
    }
  }

  const handleCreateVersion = async (e) => {
    e.preventDefault()
    if (!newVersionSource || !newVersionName.trim()) return
    setCreateLoading(true)
    setMessage('')
    try {
      await api.createVersionFromVersion(newVersionSource, newVersionName.trim())
      setNewVersionSource('')
      setNewVersionName('')
      await fetchArticle()
      setMessage('نسخه جدید با موفقیت ایجاد شد!')
    } catch (err) {
      setMessage(err.data?.detail || 'خطا در ایجاد نسخه.')
    } finally {
      setCreateLoading(false)
    }
  }

  const handleCreateEmptyVersion = async (e) => {
    e.preventDefault()
    if (!emptyVersionName.trim()) return
    setEmptyCreateLoading(true)
    setMessage('')
    try {
      await api.createEmptyVersion(name, emptyVersionName.trim())
      setEmptyVersionName('')
      await fetchArticle()
      setMessage('نسخه خالی با موفقیت ایجاد شد!')
    } catch (err) {
      setMessage(err.data?.detail || 'خطا در ایجاد نسخه.')
    } finally {
      setEmptyCreateLoading(false)
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

  const versions = article?.versions || []
  const currentVersion = article?.current_version

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-start justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-2xl font-bold text-dark">{article.name}</h1>
              <p className="text-gray-500 text-sm mt-1">
                ایجادکننده: <span className="text-gray-700">{article.creator_id}</span>
              </p>
              {currentVersion && (
                <p className="text-gray-500 text-sm mt-1">
                  نسخه فعلی: <span className="text-forest font-medium">{currentVersion.name}</span>
                </p>
              )}
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              <Link
                to={`/articles/${encodeURIComponent(name)}`}
                className="inline-flex items-center gap-1.5 bg-forest hover:bg-leaf text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
              >
                <Eye className="w-4 h-4" />
                مشاهده مقاله
              </Link>
              {isCreator && (
                <Link
                  to={`/articles/${encodeURIComponent(name)}/requests`}
                  className="inline-flex items-center gap-1.5 bg-amber-500 hover:bg-amber-600 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
                >
                  <Inbox className="w-4 h-4" />
                  درخواست‌های انتشار
                </Link>
              )}
              {!isCreator && currentUserId && (
                <Link
                  to={`/articles/${encodeURIComponent(name)}/my-requests`}
                  className="inline-flex items-center gap-1.5 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
                >
                  <ClipboardList className="w-4 h-4" />
                  درخواست‌های من
                </Link>
              )}
            </div>
          </div>
        </div>

        <div className="p-6">
          <h2 className="text-lg font-bold text-dark mb-4 flex items-center gap-2">
            <GitBranch className="w-5 h-5 text-forest" />
            نسخه‌ها
          </h2>

          {versions.length > 0 ? (
            <div className="space-y-3 mb-6">
              {versions.map((v) => (
                <div
                  key={v.name}
                  className={`flex items-center justify-between flex-wrap gap-3 p-4 rounded-xl border ${
                    currentVersion?.name === v.name
                      ? 'border-forest bg-forest/5'
                      : 'border-gray-200 bg-gray-50'
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-dark text-sm truncate">{v.name}</span>
                      {currentVersion?.name === v.name && (
                        <span className="text-xs bg-forest text-white px-2 py-0.5 rounded-full whitespace-nowrap">
                          فعلی
                        </span>
                      )}
                    </div>
                    {v.summary && (
                      <p className="text-xs text-gray-500 mt-1 truncate">{v.summary}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Link
                      to={`/versions/${encodeURIComponent(v.name)}/preview`}
                      className="inline-flex items-center gap-1.5 bg-gray-200 hover:bg-gray-300 text-dark text-xs font-medium px-3 py-1.5 rounded-lg transition-colors"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      پیش‌نمایش
                    </Link>
                    <Link
                      to={`/versions/${encodeURIComponent(v.name)}/edit`}
                      className="inline-flex items-center gap-1.5 bg-forest hover:bg-leaf text-white text-xs font-medium px-3 py-1.5 rounded-lg transition-colors"
                    >
                      <Edit3 className="w-3.5 h-3.5" />
                      ویرایش
                    </Link>
                    {isCreator ? (
                      <button
                        onClick={() => handlePublish(v.name)}
                        disabled={publishLoading === v.name || currentVersion?.name === v.name}
                        className="inline-flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-medium px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {publishLoading === v.name ? (
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <Send className="w-3.5 h-3.5" />
                        )}
                        انتشار
                      </button>
                    ) : currentUserId ? (
                      <button
                        onClick={() => handleRequestPublish(v.name)}
                        disabled={publishLoading === v.name}
                        className="inline-flex items-center gap-1.5 bg-amber-500 hover:bg-amber-600 text-white text-xs font-medium px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {publishLoading === v.name ? (
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <Send className="w-3.5 h-3.5" />
                        )}
                        درخواست انتشار
                      </button>
                    ) : null}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm mb-6">نسخه‌ای موجود نیست.</p>
          )}

          <div className="bg-light border border-gray-200 rounded-xl p-5">
            <h3 className="text-sm font-bold text-dark mb-3 flex items-center gap-2">
              <Plus className="w-4 h-4 text-forest" />
              ایجاد نسخه جدید از نسخه موجود
            </h3>
            <form onSubmit={handleCreateVersion} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">نسخه مبدأ</label>
                <select
                  value={newVersionSource}
                  onChange={(e) => setNewVersionSource(e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg py-2 px-3 text-sm text-dark focus:outline-none focus:ring-2 focus:ring-forest focus:border-transparent"
                >
                  <option value="">انتخاب نسخه...</option>
                  {versions.map((v) => (
                    <option key={v.name} value={v.name}>{v.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">نام نسخه جدید</label>
                <input
                  type="text"
                  value={newVersionName}
                  onChange={(e) => setNewVersionName(e.target.value)}
                  placeholder="مثلاً: article-v2"
                  className="w-full bg-white border border-gray-300 rounded-lg py-2 px-3 text-sm text-dark placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-forest focus:border-transparent"
                />
              </div>
              <button
                type="submit"
                disabled={createLoading || !newVersionSource || !newVersionName.trim()}
                className="inline-flex items-center gap-1.5 bg-forest hover:bg-leaf text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {createLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    در حال ایجاد...
                  </>
                ) : (
                  <>
                    <GitBranch className="w-4 h-4" />
                    ایجاد نسخه
                  </>
                )}
              </button>
            </form>
          </div>

          <div className="bg-light border border-gray-200 rounded-xl p-5 mt-4">
            <h3 className="text-sm font-bold text-dark mb-3 flex items-center gap-2">
              <Plus className="w-4 h-4 text-forest" />
              ایجاد نسخه خالی
            </h3>
            <form onSubmit={handleCreateEmptyVersion} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">نام نسخه</label>
                <input
                  type="text"
                  value={emptyVersionName}
                  onChange={(e) => setEmptyVersionName(e.target.value)}
                  placeholder="مثلاً: article-v3"
                  className="w-full bg-white border border-gray-300 rounded-lg py-2 px-3 text-sm text-dark placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-forest focus:border-transparent"
                />
              </div>
              <button
                type="submit"
                disabled={emptyCreateLoading || !emptyVersionName.trim()}
                className="inline-flex items-center gap-1.5 bg-forest hover:bg-leaf text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {emptyCreateLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    در حال ایجاد...
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4" />
                    ایجاد نسخه خالی
                  </>
                )}
              </button>
            </form>
          </div>
        </div>
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
