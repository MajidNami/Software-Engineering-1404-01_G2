import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { FileText, Star, Clock, Tag, ArrowRight, Loader2 } from 'lucide-react'
import { api } from '../api'

function ArticleCard({ name, summary, score }) {
  return (
    <Link
      to={`/articles/${encodeURIComponent(name)}`}
      className="block bg-white border border-gray-200 rounded-xl p-4 hover:border-forest transition-colors shadow-sm"
    >
      <div className="flex items-start gap-3">
        <FileText className="w-5 h-5 text-forest flex-shrink-0 mt-0.5" />
        <div className="min-w-0 flex-1">
          <div className="flex items-center justify-between gap-2">
            <span className="font-medium text-dark text-sm">{name}</span>
            <span className="text-xs text-gray-400 flex-shrink-0">
              {score}★
            </span>
          </div>
          {summary && (
            <p className="text-sm text-gray-600 mt-1.5 leading-relaxed line-clamp-2">{summary}</p>
          )}
        </div>
      </div>
    </Link>
  )
}

function Section({ icon, title, children, loading, empty }) {
  return (
    <section className="mb-10">
      <h2 className="text-lg font-bold text-dark mb-4 flex items-center gap-2">
        {icon}
        {title}
      </h2>
      {loading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="w-6 h-6 text-forest animate-spin" />
        </div>
      ) : empty ? (
        <p className="text-gray-500 text-sm py-4">مقاله‌ای یافت نشد.</p>
      ) : (
        children
      )}
    </section>
  )
}

export default function HomePage() {
  const [newest, setNewest] = useState([])
  const [topRated, setTopRated] = useState([])
  const [byTag, setByTag] = useState([])
  const [loadingNewest, setLoadingNewest] = useState(true)
  const [loadingTopRated, setLoadingTopRated] = useState(true)
  const [loadingByTag, setLoadingByTag] = useState(true)

  useEffect(() => {
    api.newestArticles()
      .then(setNewest)
      .catch(() => {})
      .finally(() => setLoadingNewest(false))

    api.topRatedArticles()
      .then(setTopRated)
      .catch(() => {})
      .finally(() => setLoadingTopRated(false))

    api.topArticlesByTag()
      .then(setByTag)
      .catch(() => {})
      .finally(() => setLoadingByTag(false))
  }, [])

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="text-center mb-12">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-forest/10 mb-4">
          <FileText className="w-8 h-8 text-forest" />
        </div>
        <h1 className="text-3xl sm:text-4xl font-bold text-dark mb-2">دانشنامه (ویکی)</h1>
        <p className="text-gray-500">
          به دانشنامه گروه ۲ خوش آمدید
        </p>
      </div>

      <Section
        icon={<Clock className="w-5 h-5 text-blue-500" />}
        title="جدیدترین مقالات"
        loading={loadingNewest}
        empty={newest.length === 0}
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {newest.map((a) => (
            <ArticleCard key={a.name} {...a} />
          ))}
        </div>
      </Section>

      <Section
        icon={<Star className="w-5 h-5 text-amber-500" />}
        title="محبوب‌ترین مقالات"
        loading={loadingTopRated}
        empty={topRated.length === 0}
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {topRated.map((a) => (
            <ArticleCard key={a.name} {...a} />
          ))}
        </div>
      </Section>

      <Section
        icon={<Tag className="w-5 h-5 text-forest" />}
        title="برترین مقالات هر برچسب"
        loading={loadingByTag}
        empty={byTag.length === 0}
      >
        <div className="space-y-6">
          {byTag.map((group) => (
            <div key={group.tag}>
              <h3 className="text-sm font-semibold text-forest mb-2 flex items-center gap-1.5">
                <span className="bg-forest/10 text-forest px-2.5 py-0.5 rounded-full text-xs">
                  {group.tag}
                </span>
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {group.articles.map((a) => (
                  <ArticleCard key={a.name} {...a} />
                ))}
              </div>
            </div>
          ))}
        </div>
      </Section>

      <footer className="border-t border-gray-300 pt-6 text-center">
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
