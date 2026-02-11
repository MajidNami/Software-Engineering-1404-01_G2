import RatingStars from './RatingStars'
import { timeAgo } from '../utils/format'

function PostCard({ post, onOpen }) {
  return (
    <div className="card" style={{ padding: 14, cursor: 'pointer' }} onClick={() => onOpen?.(post.post_id)}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
        <div style={{ fontWeight: 700 }}>{post.username}</div>
        <div className="pill-ghost">{timeAgo(post.created_at)}</div>
      </div>
      <p style={{ margin: '8px 0', color: '#dbe6f5', lineHeight: 1.7 }}>
        {post.content?.slice(0, 240) || 'بدون متن'}
      </p>
      <div className="list-inline">
        <span className="pill-ghost">مکان #{post.place}</span>
        <span className="pill-ghost">👍 {post.like_count}</span>
        <span className="pill-ghost">👎 {post.dislike_count}</span>
        <span className="pill-ghost">پاسخ‌ها {post.reply_count}</span>
        <span className="pill-ghost">{post.status === 'APPROVED' ? 'تایید شده' : 'در انتظار'}</span>
      </div>
    </div>
  )
}

export default PostCard
