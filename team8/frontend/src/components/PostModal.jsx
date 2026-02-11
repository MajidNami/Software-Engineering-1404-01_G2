import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchPostDetail, fetchPostReplies } from '../api/queries'
import { api } from '../api/client'
import { useAuth } from '../hooks/useAuth'
import RatingStars from './RatingStars'
import { timeAgo } from '../utils/format'
import { useState } from 'react'

function PostModal({ postId, onClose, onRequireAuth }) {
  const { isAuthenticated } = useAuth()
  const queryClient = useQueryClient()
  const [replyText, setReplyText] = useState('')
  const [file, setFile] = useState(null)
  const { data: post } = useQuery({
    queryKey: ['post', postId],
    queryFn: () => fetchPostDetail(postId),
    enabled: !!postId,
  })
  const { data: replies } = useQuery({
    queryKey: ['post', postId, 'replies'],
    queryFn: () => fetchPostReplies(postId),
    enabled: !!postId,
  })

  const replyMutation = useMutation({
    mutationFn: async () => {
      if (!isAuthenticated) {
        onRequireAuth?.('login')
        throw new Error('auth required')
      }
      let mediaId = null
      if (file) {
        const form = new FormData()
        form.append('file', file)
        form.append('place', post.place)
        const res = await api.post('/media/', form, { headers: { 'Content-Type': 'multipart/form-data' } })
        mediaId = res.data.media_id
      }
      await api.post('/posts/', {
        place: post.place,
        parent: post.post_id,
        media: mediaId,
        content: replyText,
      })
    },
    onSuccess: () => {
      setReplyText('')
      setFile(null)
      queryClient.invalidateQueries({ queryKey: ['post', postId, 'replies'] })
    },
  })

  if (!post) return null

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(4,10,20,0.78)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 30, padding: 16 }}>
      <div className="glass" style={{ width: '100%', maxWidth: 720, maxHeight: '90vh', overflow: 'auto', padding: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 10 }}>
          <div style={{ fontSize: 18, fontWeight: 800 }}>پست #{post.post_id}</div>
          <button className="btn btn-ghost" onClick={onClose}>بستن</button>
        </div>
        <div className="card" style={{ marginTop: 10 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ fontWeight: 700 }}>{post.username}</div>
            <div className="pill-ghost">{timeAgo(post.created_at)}</div>
          </div>
          <p style={{ margin: '10px 0', lineHeight: 1.7, color: '#dbe6f5' }}>{post.content}</p>
          {post.media_detail?.url && (
            <img src={post.media_detail.url} alt="media" style={{ width: '100%', maxHeight: 320, objectFit: 'cover', marginTop: 8 }} />
          )}
          <div className="list-inline" style={{ marginTop: 10 }}>
            <span className="pill-ghost">👍 {post.like_count}</span>
            <span className="pill-ghost">👎 {post.dislike_count}</span>
            <span className="pill-ghost">پاسخ‌ها {post.reply_count}</span>
          </div>
        </div>

        <div className="card" style={{ marginTop: 12 }}>
          <div style={{ fontWeight: 700, marginBottom: 8 }}>ارسال پاسخ</div>
          <form className="grid" style={{ gap: 8 }} onSubmit={(e) => { e.preventDefault(); replyMutation.mutate(); }}>
            <textarea
              className="input"
              rows={3}
              placeholder="متن پاسخ..."
              value={replyText}
              onChange={(e) => setReplyText(e.target.value)}
              required
            />
            <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
            <button className="btn btn-primary" disabled={replyMutation.isLoading || !replyText}>
              {replyMutation.isLoading ? 'در حال ارسال...' : 'ارسال پاسخ'}
            </button>
          </form>
        </div>

        <div className="card" style={{ marginTop: 12 }}>
          <div style={{ fontWeight: 700, marginBottom: 8 }}>پاسخ‌ها</div>
          {replies?.length ? (
            <div className="grid" style={{ gap: 10 }}>
              {replies.map((r) => (
                <div key={r.post_id} className="card" style={{ background: '#1a2c45' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ fontWeight: 700 }}>{r.username}</div>
                    <div className="pill-ghost">{timeAgo(r.created_at)}</div>
                  </div>
                  <p style={{ margin: '8px 0', lineHeight: 1.7, color: '#dbe6f5' }}>{r.content}</p>
                  {r.media && <span className="pill-ghost">رسانه ضمیمه</span>}
                </div>
              ))}
            </div>
          ) : (
            <div className="empty">پاسخی ثبت نشده است.</div>
          )}
        </div>
      </div>
    </div>
  )
}

export default PostModal
