import { Lightbulb } from 'lucide-react'

export default function Recommendations({ recommendations }) {
  if (!recommendations || recommendations.length === 0) return null

  return (
    <div className="card bg-gradient-to-br from-amber-50 to-orange-50 border-amber-100">
      <h3 className="font-semibold text-gray-900 flex items-center gap-2 mb-4">
        <Lightbulb className="w-5 h-5 text-amber-500" />
        Recomendaciones
      </h3>
      
      <ul className="space-y-3">
        {recommendations.map((rec, index) => (
          <li 
            key={index}
            className="text-sm text-gray-700 pl-4 border-l-2 border-amber-300"
          >
            {rec}
          </li>
        ))}
      </ul>
    </div>
  )
}
