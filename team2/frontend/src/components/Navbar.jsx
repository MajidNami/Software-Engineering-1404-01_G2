import { Link, useLocation } from 'react-router-dom'
import { BookOpen, PlusCircle, Home, Search, User } from 'lucide-react'

export default function Navbar() {
  const location = useLocation()

  const linkClass = (path) =>
    `flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
      location.pathname === path
        ? 'bg-forest text-white'
        : 'text-green-100 hover:bg-leaf hover:text-white'
    }`

  return (
    <nav className="bg-forest border-b border-leaf sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2 text-white font-bold text-lg">
            <BookOpen className="w-6 h-6 text-gold" />
            <span>دانشنامه (ویکی)</span>
            <span className="text-xs bg-gold/20 text-gold px-2 py-0.5 rounded-full mr-2">
              گروه ۲
            </span>
          </Link>

          <div className="flex items-center gap-1">
            <Link to="/" className={linkClass('/')}>
              <Home className="w-4 h-4" />
              <span>خانه</span>
            </Link>
            <Link to="/search" className={linkClass('/search')}>
              <Search className="w-4 h-4" />
              <span>جستجو</span>
            </Link>
            <Link to="/my-articles" className={linkClass('/my-articles')}>
              <User className="w-4 h-4" />
              <span>مقالات من</span>
            </Link>
            <Link to="/articles/new" className={linkClass('/articles/new')}>
              <PlusCircle className="w-4 h-4" />
              <span>مقاله جدید</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}
