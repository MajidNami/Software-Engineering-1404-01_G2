import { api } from './client'

const unpage = (data) => {
  if (data && Array.isArray(data.results)) return data.results
  return data
}

export const fetchProvinces = () => api.get('/provinces/').then((r) => r.data)
export const fetchCategories = () => api.get('/categories/').then((r) => r.data)
export const fetchCities = (province) =>
  api
    .get('/cities/', { params: province ? { province } : undefined })
    .then((r) => r.data)

export const fetchPlaces = (filters) =>
  api
    .get('/places/', {
      params: {
        search: filters.search || undefined,
        category: filters.category || undefined,
        city: filters.city || undefined,
        'city__province': filters.province || undefined,
      },
    })
    .then((r) => unpage(r.data))

export const fetchPlace = (id) => api.get(`/places/${id}/`).then((r) => r.data)
export const fetchPlaceStats = (id) => api.get(`/places/${id}/stats/`).then((r) => r.data)
export const fetchPlaceMedia = (id) =>
  api.get('/media/', { params: { place: id } }).then((r) => unpage(r.data))
export const fetchPlacePosts = (id) =>
  api.get('/posts/', { params: { place: id } }).then((r) => unpage(r.data))
export const fetchPostDetail = (id) => api.get(`/posts/${id}/`).then((r) => r.data)
export const fetchPostReplies = (id) => api.get(`/posts/${id}/replies/`).then((r) => unpage(r.data))
export const fetchRatings = (place) =>
  api.get('/ratings/', { params: { place } }).then((r) => unpage(r.data))
export const fetchMyRatings = () => api.get('/ratings/my/').then((r) => r.data)
export const fetchNotifications = () => api.get('/notifications/').then((r) => r.data)
export const fetchUnreadCount = () => api.get('/notifications/unread-count/').then((r) => r.data)

// Feed (latest posts across places)
export const fetchFeed = () => api.get('/posts/').then((r) => unpage(r.data))

// Moderation (admin)
export const fetchPendingPosts = () => api.get('/moderation/posts/').then((r) => unpage(r.data))
export const fetchPendingMedia = () => api.get('/moderation/media/').then((r) => unpage(r.data))
export const approvePost = (id) => api.post(`/moderation/posts/${id}/approve/`)
export const rejectPost = (id, reason = 'Rejected by admin') =>
  api.post(`/moderation/posts/${id}/reject/`, { reason })
export const approveMedia = (id) => api.post(`/moderation/media/${id}/approve/`)
export const rejectMedia = (id, reason = 'Rejected by admin') =>
  api.post(`/moderation/media/${id}/reject/`, { reason })
