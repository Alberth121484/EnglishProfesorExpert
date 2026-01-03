import { createContext, useContext, useState, useEffect } from 'react'
import { api } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const token = localStorage.getItem('token')
    
    if (!token) {
      // Check for telegram_id in URL params
      const params = new URLSearchParams(window.location.search)
      const telegramId = params.get('telegram_id')
      
      if (telegramId) {
        try {
          await loginWithTelegramId(telegramId)
          // Clean URL
          window.history.replaceState({}, '', window.location.pathname)
          return
        } catch (error) {
          console.error('Auto-login failed:', error)
        }
      }
      
      setLoading(false)
      return
    }

    try {
      const response = await api.getCurrentStudent()
      setUser(response.data)
      setIsAuthenticated(true)
    } catch (error) {
      localStorage.removeItem('token')
    } finally {
      setLoading(false)
    }
  }

  const loginWithTelegramId = async (telegramId) => {
    try {
      const response = await api.authenticateByTelegramId(telegramId)
      const { access_token } = response.data
      
      localStorage.setItem('token', access_token)
      
      const userResponse = await api.getCurrentStudent()
      setUser(userResponse.data)
      setIsAuthenticated(true)
      
      return true
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
    setIsAuthenticated(false)
  }

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      isAuthenticated,
      loginWithTelegramId,
      logout,
      checkAuth
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
