import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchPlacePosts, fetchPlaces, fetchFeed } from '../api/queries'
import PostCard from './PostCard'

function FeedSection({ onOpenPost }) {
  const { data: feed, isLoading } = useQuery({
    queryKey: ['feed'],
    queryFn: fetchFeed,
  })

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
        <div style={{ fontWeight: 800 }}>جدیدترین پست‌ها</div>
      </div>
      {isLoading && <div className="empty">در حال بارگذاری...</div>}
      {!isLoading && (!feed || feed.length === 0) && <div className="empty">پستی یافت نشد.</div>}
      <div className="grid" style={{ gap: 10 }}>
        {feed?.map((p) => (
          <PostCard key={p.post_id} post={p} onOpen={onOpenPost} />
        ))}
      </div>
    </div>
  )
}

export default FeedSection
