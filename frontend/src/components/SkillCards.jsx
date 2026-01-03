import { 
  Mic, Headphones, BookOpen, Pencil, Library, Brackets 
} from 'lucide-react'

const skillIcons = {
  SPEAKING: Mic,
  LISTENING: Headphones,
  READING: BookOpen,
  WRITING: Pencil,
  VOCABULARY: Library,
  GRAMMAR: Brackets
}

const skillColors = {
  SPEAKING: { bg: 'bg-red-50', text: 'text-red-500', bar: 'bg-red-500' },
  LISTENING: { bg: 'bg-blue-50', text: 'text-blue-500', bar: 'bg-blue-500' },
  READING: { bg: 'bg-green-50', text: 'text-green-500', bar: 'bg-green-500' },
  WRITING: { bg: 'bg-yellow-50', text: 'text-yellow-600', bar: 'bg-yellow-500' },
  VOCABULARY: { bg: 'bg-purple-50', text: 'text-purple-500', bar: 'bg-purple-500' },
  GRAMMAR: { bg: 'bg-indigo-50', text: 'text-indigo-500', bar: 'bg-indigo-500' }
}

export default function SkillCards({ skills }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {skills.map((skillProgress) => {
        const Icon = skillIcons[skillProgress.skill.code] || BookOpen
        const colors = skillColors[skillProgress.skill.code] || skillColors.READING
        
        return (
          <div key={skillProgress.skill.id} className="card">
            <div className="flex items-center gap-3 mb-3">
              <div className={`p-2 rounded-lg ${colors.bg}`}>
                <Icon className={`w-5 h-5 ${colors.text}`} />
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{skillProgress.skill.name}</h4>
                <p className="text-xs text-gray-500">
                  {skillProgress.lessons_completed} lecciones
                </p>
              </div>
              <span className="text-lg font-bold text-gray-900">
                {skillProgress.score}%
              </span>
            </div>
            
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className={`h-full ${colors.bar} rounded-full transition-all duration-500`}
                style={{ width: `${skillProgress.score}%` }}
              />
            </div>
            
            {skillProgress.last_practiced && (
              <p className="text-xs text-gray-400 mt-2">
                Última práctica: {new Date(skillProgress.last_practiced).toLocaleDateString()}
              </p>
            )}
          </div>
        )
      })}
    </div>
  )
}
