import { useEffect, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import HeaderBar from '../components/HeaderBar'
import PlaceCard from '../components/PlaceCard'
import PlaceDetail from '../components/PlaceDetail'
import FeedSection from '../components/FeedSection'
import PostModal from '../components/PostModal'
import NewPostModal from '../components/NewPostModal'
import AuthModal from '../components/auth/AuthModal'
import { fetchCategories, fetchCities, fetchPlaces, fetchProvinces } from '../api/queries'

function HomePage() {
  const [filters, setFilters] = useState({ search: '', province: '', city: '', category: '' })
  const [selectedId, setSelectedId] = useState(null)
  const [postModalId, setPostModalId] = useState(null)
  const [newPostOpen, setNewPostOpen] = useState(false)
  const [authModal, setAuthModal] = useState({ open: false, mode: 'login' })

  const { data: provinces } = useQuery({ queryKey: ['provinces'], queryFn: fetchProvinces })
  const { data: categories } = useQuery({ queryKey: ['categories'], queryFn: fetchCategories })
  const { data: cities } = useQuery({
    queryKey: ['cities', filters.province],
    queryFn: () => fetchCities(filters.province),
    enabled: !!filters.province,
  })

  const placesQuery = useQuery({
    queryKey: ['places', filters],
    queryFn: () => fetchPlaces(filters),
    keepPreviousData: true,
  })

  useEffect(() => {
    if (!selectedId && placesQuery.data?.length) {
      setSelectedId(placesQuery.data[0].place_id)
    }
  }, [placesQuery.data, selectedId])

  const cityOptions = useMemo(() => cities || [], [cities])

  const requireAuth = (mode = 'login') => setAuthModal({ open: true, mode })

  return (
    <div className="shell">
      <HeaderBar onShowAuth={(mode) => setAuthModal({ open: true, mode })} />

      <div className="glass" style={{ padding: 22, marginBottom: 20 }}>
        <div style={{ display: 'grid', gap: 12, gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))' }}>
          <input
            className="input"
            placeholder="جستجوی عنوان یا توضیح"
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          />
          <select
            value={filters.province}
            onChange={(e) => setFilters({ ...filters, province: e.target.value, city: '' })}
          >
            <option value="">استان</option>
            {provinces?.map((p) => (
              <option key={p.province_id} value={p.province_id}>
                {p.name}
              </option>
            ))}
          </select>
          <select
            value={filters.city}
            onChange={(e) => setFilters({ ...filters, city: e.target.value })}
            disabled={!filters.province}
          >
            <option value="">شهر</option>
            {cityOptions.map((c) => (
              <option key={c.city_id} value={c.city_id}>
                {c.name}
              </option>
            ))}
          </select>
          <select
            value={filters.category}
            onChange={(e) => setFilters({ ...filters, category: e.target.value })}
          >
            <option value="">دسته‌بندی</option>
            {categories?.map((c) => (
              <option key={c.category_id} value={c.category_id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 10 }}>
          <button className="btn btn-primary" onClick={() => setNewPostOpen(true)}>ارسال پست جدید</button>
        </div>
      </div>

      <div className="grid" style={{ gridTemplateColumns: '380px minmax(0, 1fr)', gap: 18 }}>
        <div className="grid" style={{ gap: 10, alignSelf: 'flex-start', position: 'sticky', top: 12 }}>
          {placesQuery.isLoading && <div className="card">در حال بارگذاری...</div>}
          {!placesQuery.isLoading && placesQuery.data?.length === 0 && (
            <div className="card">نتیجه‌ای یافت نشد.</div>
          )}
          {placesQuery.data?.map((p) => (
            <PlaceCard key={p.place_id} place={p} active={selectedId === p.place_id} onSelect={setSelectedId} />
          ))}
        </div>

        {selectedId ? (
          <PlaceDetail placeId={selectedId} />
        ) : (
          <FeedSection onOpenPost={(pid) => setPostModalId(pid)} />
        )}
      </div>

      {postModalId && (
        <PostModal
          postId={postModalId}
          onClose={() => setPostModalId(null)}
          onRequireAuth={requireAuth}
        />
      )}
      {newPostOpen && (
        <NewPostModal
          onClose={() => setNewPostOpen(false)}
          onRequireAuth={requireAuth}
        />
      )}
      {authModal.open && <AuthModal mode={authModal.mode} onClose={() => setAuthModal({ open: false, mode: 'login' })} />}
    </div>
  )
}

export default HomePage
