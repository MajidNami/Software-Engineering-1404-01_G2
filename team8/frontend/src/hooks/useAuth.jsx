import { createContext, useContext, useMemo, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api, setAuthToken } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const queryClient = useQueryClient()
  const [token, setToken] = useState(() => localStorage.getItem('team8_token'))

  const { data: profile, isLoading: authLoading } = useQuery({
    queryKey: ['auth', 'profile', token],
    queryFn: async () => {
      if (!token) return null
      const res = await api.get('/auth/profile/')
      return res.data.user
    },
    enabled: !!token,
    staleTime: 1000 * 60 * 5,
    retry: 1,
  })

  const login = async (payload) => {
    const res = await api.post('/auth/login/', payload)
    const newToken = res.data.token
    setAuthToken(newToken)
    setToken(newToken)
    await queryClient.invalidateQueries({ queryKey: ['auth'] })
    return res.data
  }

  const register = async (payload) => {
    const res = await api.post('/auth/register/', payload)
    const newToken = res.data.token
    setAuthToken(newToken)
    setToken(newToken)
    await queryClient.invalidateQueries({ queryKey: ['auth'] })
    return res.data
  }

  const logout = async () => {
    try {
      await api.post('/auth/logout/')
    } catch (err) {
      // ignore
    }
    setAuthToken(null)
    setToken(null)
    queryClient.removeQueries()
  }

  const value = useMemo(
    () => ({
      user: profile,
      token,
      authLoading,
      login,
      register,
      logout,
      isAuthenticated: !!profile,
    }),
    [profile, token, authLoading]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => useContext(AuthContext)
