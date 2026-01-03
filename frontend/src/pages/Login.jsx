import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { BookOpen, MessageCircle } from 'lucide-react'

export default function Login() {
  const [telegramId, setTelegramId] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { loginWithTelegramId, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/')
    }
  }, [isAuthenticated, navigate])

  useEffect(() => {
    // Auto-login if telegram_id is in URL
    const tid = searchParams.get('telegram_id')
    if (tid) {
      handleLogin(tid)
    }
  }, [searchParams])

  const handleLogin = async (tid) => {
    const idToUse = tid || telegramId
    if (!idToUse) {
      setError('Ingresa tu Telegram ID')
      return
    }

    setLoading(true)
    setError('')

    try {
      await loginWithTelegramId(idToUse)
      navigate('/')
    } catch (err) {
      setError('No se encontró tu cuenta. Asegúrate de haber iniciado el bot primero.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-500 via-purple-500 to-pink-500 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
            <span className="text-white font-bold text-3xl">E</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">English Profesor Expert</h1>
          <p className="text-gray-500 mt-2">Panel de Progreso del Estudiante</p>
        </div>

        {/* Info */}
        <div className="bg-blue-50 rounded-xl p-4 mb-6">
          <div className="flex items-start gap-3">
            <MessageCircle className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">¿Cómo accedo?</p>
              <p>Inicia el bot de Telegram y usa el comando <code className="bg-blue-100 px-1 rounded">/panel</code> para obtener un enlace directo.</p>
            </div>
          </div>
        </div>

        {/* Manual Login */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Telegram ID (opcional)
            </label>
            <input
              type="text"
              value={telegramId}
              onChange={(e) => setTelegramId(e.target.value)}
              placeholder="Ej: 123456789"
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all"
            />
          </div>

          {error && (
            <p className="text-red-500 text-sm">{error}</p>
          )}

          <button
            onClick={() => handleLogin()}
            disabled={loading}
            className="w-full btn-primary py-3 rounded-xl text-lg font-semibold disabled:opacity-50"
          >
            {loading ? 'Cargando...' : 'Acceder'}
          </button>
        </div>

        {/* Footer */}
        <div className="mt-8 pt-6 border-t border-gray-100 text-center">
          <p className="text-sm text-gray-500 flex items-center justify-center gap-2">
            <BookOpen className="w-4 h-4" />
            Aprende inglés de forma personalizada
          </p>
        </div>
      </div>
    </div>
  )
}
