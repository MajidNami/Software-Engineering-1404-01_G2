import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

export const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
})

export const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem('team8_token', token)
    api.defaults.headers.common.Authorization = `Bearer ${token}`
  } else {
    localStorage.removeItem('team8_token')
    delete api.defaults.headers.common.Authorization
  }
}

// Initialize from storage on first load
const saved = localStorage.getItem('team8_token')
if (saved) {
  setAuthToken(saved)
}

api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response && error.response.status === 401) {
      setAuthToken(null)
    }
    return Promise.reject(error)
  }
)
