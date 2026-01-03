import { TrendingUp, Target } from 'lucide-react'

export default function LevelProgress({ currentLevel, nextLevel, progressPercent }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
          <Target className="w-5 h-5 text-primary-500" />
          Progreso de Nivel
        </h3>
        <span className="text-sm text-gray-500">{progressPercent}%</span>
      </div>

      <div className="mb-4">
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="font-medium text-primary-600">{currentLevel?.name}</span>
          {nextLevel && (
            <span className="text-gray-400">{nextLevel?.name}</span>
          )}
        </div>
        
        <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary-500 to-purple-500 rounded-full transition-all duration-500"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {nextLevel ? (
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <TrendingUp className="w-4 h-4 text-green-500" />
          <span>
            {progressPercent >= 75 
              ? '¡Casi listo para subir de nivel!'
              : `Continúa practicando para alcanzar ${nextLevel.name}`
            }
          </span>
        </div>
      ) : (
        <div className="text-sm text-amber-600 font-medium">
          ¡Has alcanzado el nivel máximo!
        </div>
      )}
    </div>
  )
}
