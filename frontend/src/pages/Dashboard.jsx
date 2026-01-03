import { useDashboard } from '../hooks/useDashboard'
import { useAuth } from '../context/AuthContext'
import StatsCards from '../components/StatsCards'
import LevelProgress from '../components/LevelProgress'
import ProgressRadar from '../components/ProgressRadar'
import SkillCards from '../components/SkillCards'
import Recommendations from '../components/Recommendations'
import { RefreshCw } from 'lucide-react'

export default function Dashboard() {
  const { user } = useAuth()
  const { dashboard, loading, error, refetch } = useDashboard()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500 mb-4">Error al cargar el dashboard</p>
        <button onClick={refetch} className="btn-primary">
          Reintentar
        </button>
      </div>
    )
  }

  if (!dashboard) return null

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            ¡Hola, {user?.first_name}! 👋
          </h1>
          <p className="text-gray-500 mt-1">
            Aquí está tu progreso de aprendizaje
          </p>
        </div>
        <button
          onClick={refetch}
          className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
          title="Actualizar"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      {/* Stats */}
      <StatsCards 
        student={dashboard.student} 
        recentLessons={dashboard.recent_lessons_count} 
      />

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Level Progress & Radar */}
        <div className="lg:col-span-2 space-y-6">
          <LevelProgress
            currentLevel={dashboard.student.current_level}
            nextLevel={dashboard.next_level}
            progressPercent={dashboard.level_progress_percent}
          />

          {/* Skills Radar Chart */}
          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-4">
              Mapa de Habilidades
            </h3>
            <ProgressRadar skills={dashboard.skills_progress} />
          </div>
        </div>

        {/* Right Column - Recommendations */}
        <div className="space-y-6">
          <Recommendations recommendations={dashboard.recommendations} />
          
          {/* Current Level Card */}
          <div className="card bg-gradient-to-br from-primary-500 to-purple-600 text-white">
            <h3 className="font-medium opacity-90 mb-2">Tu Nivel Actual</h3>
            <p className="text-2xl font-bold">
              {dashboard.student.current_level.name}
            </p>
            <p className="text-sm opacity-80 mt-2">
              {dashboard.student.current_level.description}
            </p>
          </div>
        </div>
      </div>

      {/* Skills Detail */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Detalle de Habilidades
        </h2>
        <SkillCards skills={dashboard.skills_progress} />
      </div>
    </div>
  )
}
