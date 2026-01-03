import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const api = {
  // Auth
  authenticateByTelegramId: (telegramId) => 
    client.post(`/auth/telegram-id/${telegramId}`),
  
  // Students
  getCurrentStudent: () => client.get('/students/me'),
  getDashboard: () => client.get('/students/me/dashboard'),
  getLevels: () => client.get('/students/levels'),
  
  // Lessons
  getLessons: (limit = 10, offset = 0) => 
    client.get(`/lessons/?limit=${limit}&offset=${offset}`),
  getLessonDetail: (lessonId) => client.get(`/lessons/${lessonId}`),
}

export default client
