import { Flame, BookOpen, Clock, Award } from 'lucide-react'

export default function StatsCards({ student, recentLessons }) {
  const stats = [
    {
      label: 'Racha',
      value: student.streak_days,
      unit: 'días',
      icon: Flame,
      color: 'text-orange-500',
      bgColor: 'bg-orange-50'
    },
    {
      label: 'Lecciones',
      value: student.total_lessons,
      unit: 'total',
      icon: BookOpen,
      color: 'text-blue-500',
      bgColor: 'bg-blue-50'
    },
    {
      label: 'Tiempo',
      value: student.total_minutes,
      unit: 'min',
      icon: Clock,
      color: 'text-green-500',
      bgColor: 'bg-green-50'
    },
    {
      label: 'Esta semana',
      value: recentLessons,
      unit: 'lecciones',
      icon: Award,
      color: 'text-purple-500',
      bgColor: 'bg-purple-50'
    }
  ]

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <div key={stat.label} className="card">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${stat.bgColor}`}>
              <stat.icon className={`w-5 h-5 ${stat.color}`} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              <p className="text-xs text-gray-500">{stat.unit}</p>
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-2">{stat.label}</p>
        </div>
      ))}
    </div>
  )
}
