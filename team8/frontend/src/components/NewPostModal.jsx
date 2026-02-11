import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchPlaces } from '../api/queries'
import { api } from '../api/client'
import { useAuth } from '../hooks/useAuth'

function NewPostModal({ onClose, onRequireAuth }) {
  const { isAuthenticated } = useAuth()
  const queryClient = useQueryClient()
  const [placeSearch, setPlaceSearch] = useState('')
  const [selectedPlace, setSelectedPlace] = useState('')
  const [content, setContent] = useState('')
  const [file, setFile] = useState(null)

  const { data: placeOptions } = useQuery({
    queryKey: ['places', { search: placeSearch }],
    queryFn: () => fetchPlaces({ search: placeSearch }),
  })

  const postMutation = useMutation({
    mutationFn: async () => {
      if (!isAuthenticated) {
        onRequireAuth?.('login')
        throw new Error('auth required')
      }
      let mediaId = null
      if (file) {
        const form = new FormData()
        form.append('file', file)
        form.append('place', selectedPlace)
        const res = await api.post('/media/', form, { headers: { 'Content-Type': 'multipart/form-data' } })
        mediaId = res.data.media_id
      }
      await api.post('/posts/', { place: selectedPlace, content, media: mediaId })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feed'] })
      queryClient.invalidateQueries({ queryKey: ['posts'] })
      onClose()
    },
  })

  const submit = (e) => {
    e.preventDefault()
    postMutation.mutate()
  }

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(4,10,20,0.78)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 40, padding: 16 }}>
      <div className="glass" style={{ width: '100%', maxWidth: 640, padding: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
          <div style={{ fontWeight: 800, fontSize: 18 }}>ارسال پست جدید</div>
          <button className="btn btn-ghost" onClick={onClose}>بستن</button>
        </div>
        <form className="grid" style={{ gap: 10 }} onSubmit={submit}>
          <input
            className="input"
            placeholder="جستجوی مکان (عنوان یا توضیح)"
            value={placeSearch}
            onChange={(e) => setPlaceSearch(e.target.value)}
          />
          <select
            value={selectedPlace}
            onChange={(e) => setSelectedPlace(e.target.value)}
            required
          >
            <option value="">انتخاب مکان</option>
            {placeOptions?.map((p) => (
              <option key={p.place_id} value={p.place_id}>
                {p.title}
              </option>
            ))}
          </select>
          <textarea
            className="input"
            rows={4}
            placeholder="متن پست..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
          />
          <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          <button className="btn btn-primary" disabled={!selectedPlace || !content || postMutation.isLoading}>
            {postMutation.isLoading ? 'در حال ارسال...' : 'ارسال پست'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default NewPostModal
