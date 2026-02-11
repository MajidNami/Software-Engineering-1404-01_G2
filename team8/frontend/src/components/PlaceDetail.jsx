import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchPlace, fetchPlaceStats, fetchRatings, fetchPlacePosts, fetchPlaceMedia } from '../api/queries'
import { api } from '../api/client'
import RatingStars from './RatingStars'
import { shortNumber, timeAgo } from '../utils/format'
import { useAuth } from '../hooks/useAuth'
import PostModal from './PostModal'

function PlaceDetail({ placeId }) {
  const queryClient = useQueryClient()
  const { isAuthenticated } = useAuth()
  const [ratingValue, setRatingValue] = useState(5)
  const [comment, setComment] = useState('')
  const [postError, setPostError] = useState('')
  const [postModalId, setPostModalId] = useState(null)

  const enabled = !!placeId
  const { data: place, isLoading } = useQuery({
    queryKey: ['place', placeId],
    queryFn: () => fetchPlace(placeId),
    enabled,
  })
  const { data: stats } = useQuery({
    queryKey: ['place', placeId, 'stats'],
    queryFn: () => fetchPlaceStats(placeId),
    enabled,
  })
  const { data: ratings } = useQuery({
    queryKey: ['ratings', placeId],
    queryFn: () => fetchRatings(placeId),
    enabled,
  })
  const { data: posts } = useQuery({
    queryKey: ['posts', placeId],
    queryFn: () => fetchPlacePosts(placeId),
    enabled,
  })
  const { data: media } = useQuery({
    queryKey: ['media', placeId],
    queryFn: () => fetchPlaceMedia(placeId),
    enabled,
  })

  const ratingCounts = useMemo(() => {
    const base = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 }
    ratings?.forEach((r) => { base[r.score] = (base[r.score] || 0) + 1 })
    return base
  }, [ratings])

  const ratingMutation = useMutation({
    mutationFn: (payload) => api.post('/ratings/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries(['ratings', placeId])
      queryClient.invalidateQueries(['place', placeId, 'stats'])
    },
  })

  const postMutation = useMutation({
    mutationFn: (payload) => api.post('/posts/', payload),
    onSuccess: () => {
      setComment('')
      queryClient.invalidateQueries(['posts', placeId])
      queryClient.invalidateQueries(['place', placeId])
    },
  })

  const onSubmitRating = async (e) => {
    e.preventDefault()
    await ratingMutation.mutateAsync({ place: placeId, score: ratingValue })
  }

  const onSubmitPost = async (e) => {
    e.preventDefault()
    setPostError('')
    try {
      await postMutation.mutateAsync({ place: placeId, content: comment })
    } catch (err) {
      const msg = err?.response?.data?.error || 'ارسال نشد'
      setPostError(msg)
    }
  }

  if (!placeId) return <div className="empty">یک مکان را انتخاب کنید</div>
  if (isLoading) return <div className="card">در حال بارگذاری...</div>

  return (
    <div className="glass" style={{ padding: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start' }}>
        <div>
          <div className="pill">جدید برای شما</div>
          <h2 style={{ margin: '6px 0 4px', fontSize: 24 }}>{place.title}</h2>
          <div style={{ color: '#9fb4d3', display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            <span>{place.city_name}</span>
            <span>•</span>
            <span>{place.category_name || 'نامشخص'}</span>
          </div>
        </div>
        <div style={{ textAlign: 'left' }}>
          <RatingStars value={place.average_rating || 0} />
          <div style={{ color: '#9fb4d3', fontSize: 13, marginTop: 4 }}>
            {stats?.rating_count || place.rating_count || 0} رای
          </div>
        </div>
      </div>

      <p style={{ marginTop: 14, lineHeight: 1.8, color: '#dbe6f5' }}>
        {place.description || 'برای این مکان هنوز توضیحی ثبت نشده است.'}
      </p>

      <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', marginTop: 18 }}>
        <StatCard label="میانگین امتیاز" value={stats?.average_rating?.toFixed(1) || '—'} accent />
        <StatCard label="تعداد نظرات" value={shortNumber(stats?.rating_count || 0)} />
        <StatCard label="پست‌ها" value={shortNumber(stats?.post_count || 0)} />
        <StatCard label="رسانه‌ها" value={shortNumber(stats?.media_count || 0)} />
      </div>

      {media?.length ? (
        <div style={{ marginTop: 22 }}>
          <SectionTitle title="گالری اخیر" />
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))' }}>
            {media.slice(0, 6).map((m) => (
              <div key={m.media_id} className="card" style={{ padding: 10 }}>
                <img src={m.url} alt={m.place_title} style={{ height: 120, objectFit: 'cover', width: '100%' }} />
                <div style={{ color: '#9fb4d3', fontSize: 12, marginTop: 8 }}>{m.username}</div>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      <div className="grid" style={{ marginTop: 24, gridTemplateColumns: 'minmax(0, 1fr) 320px', gap: 16 }}>
        <div className="card">
          <SectionTitle title="نظرات" />
          {posts?.length ? (
            <div className="grid" style={{ gap: 12 }}>
              {posts.map((p) => (
                <PostItem key={p.post_id} post={p} onOpen={() => setPostModalId(p.post_id)} />
              ))}
            </div>
          ) : (
            <div className="empty">هنوز نظری ثبت نشده است.</div>
          )}
        </div>

        <div className="card" style={{ position: 'sticky', top: 12, alignSelf: 'flex-start' }}>
          <SectionTitle title="امتیاز شما" />
          <form className="grid" style={{ gap: 10 }} onSubmit={onSubmitRating}>
            <input type="range" min="1" max="5" step="1" value={ratingValue} onChange={(e) => setRatingValue(Number(e.target.value))} />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <RatingStars value={ratingValue} />
              <div className="pill-ghost">{ratingValue} از ۵</div>
            </div>
            <button className="btn btn-primary" disabled={!isAuthenticated}>
              {isAuthenticated ? 'ثبت امتیاز' : 'برای امتیاز وارد شوید'}
            </button>
          </form>

          <div className="divider" />

          <SectionTitle title="توزیع امتیازات" small />
          <div className="grid" style={{ gap: 6 }}>
            {[5, 4, 3, 2, 1].map((score) => (
              <div key={score} style={{ display: 'grid', gridTemplateColumns: '28px 1fr 40px', alignItems: 'center', gap: 6 }}>
                <span style={{ color: '#9fb4d3', fontSize: 13 }}>{score}★</span>
                <div style={{ height: 8, borderRadius: 999, background: '#223553', overflow: 'hidden' }}>
                  <div
                    style={{
                      width: ratings && ratings.length ? `${(ratingCounts[score] / ratings.length) * 100}%` : 0,
                      height: '100%',
                      background: 'linear-gradient(120deg, #4ac29a, #3aa382)',
                    }}
                  />
                </div>
                <span style={{ color: '#9fb4d3', fontSize: 12 }}>{ratingCounts[score] || 0}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: 18 }}>
        <SectionTitle title="ارسال نظر" />
        <form className="grid" style={{ gap: 10 }} onSubmit={onSubmitPost}>
          <textarea
            className="input"
            rows={3}
            placeholder={isAuthenticated ? 'نظر خود را درباره این مکان بنویسید...' : 'برای ارسال نظر وارد شوید'}
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            disabled={!isAuthenticated}
            required
          />
          {postError && <div style={{ color: '#f66', fontSize: 13 }}>{postError}</div>}
          <button className="btn btn-primary" disabled={!isAuthenticated || postMutation.isLoading}>
            {isAuthenticated ? 'ارسال نظر' : 'ورود / ثبت‌نام'}
          </button>
        </form>
      </div>
      {postModalId && (
        <PostModal
          postId={postModalId}
          onClose={() => setPostModalId(null)}
          onRequireAuth={() => {}}
        />
      )}
    </div>
  )
}

function SectionTitle({ title, small }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: small ? 8 : 12 }}>
      <div style={{ width: 8, height: 8, borderRadius: 999, background: 'linear-gradient(120deg, #4ac29a, #f7c948)' }} />
      <div style={{ fontWeight: 700, fontSize: small ? 14 : 16 }}>{title}</div>
    </div>
  )
}

function StatCard({ label, value, accent }) {
  return (
    <div
      className="card"
      style={{
        background: accent ? 'linear-gradient(135deg, #1d3a5f, #274c73)' : undefined,
        borderColor: accent ? 'rgba(74,194,154,0.7)' : undefined,
      }}
    >
      <div style={{ color: '#9fb4d3', fontSize: 13 }}>{label}</div>
      <div style={{ fontWeight: 800, fontSize: 22, marginTop: 6 }}>{value}</div>
    </div>
  )
}

function PostItem({ post, onOpen }) {
  return (
    <div className="card" style={{ padding: 14, cursor: 'pointer' }} onClick={onOpen}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ fontWeight: 700 }}>{post.username}</div>
        <div className="pill-ghost">{timeAgo(post.created_at)}</div>
      </div>
      <p style={{ margin: '10px 0 8px', lineHeight: 1.7, color: '#dbe6f5' }}>{post.content}</p>
      <div className="list-inline">
        <span className="pill-ghost">👍 {post.like_count}</span>
        <span className="pill-ghost">👎 {post.dislike_count}</span>
        <span className="pill-ghost">پاسخ‌ها {post.reply_count}</span>
      </div>
    </div>
  )
}

export default PlaceDetail
