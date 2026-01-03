import { Calendar, MessageSquare, Clock, ChevronRight } from 'lucide-react'

export default function LessonCard({ lesson, onClick }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div 
      className="card hover:shadow-md transition-shadow cursor-pointer"
      onClick={() => onClick?.(lesson)}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h4 className="font-medium text-gray-900 mb-1">
            {lesson.topic || 'Lección de práctica'}
          </h4>
          
          {lesson.summary && (
            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
              {lesson.summary}
            </p>
          )}
          
          <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5" />
              {formatDate(lesson.started_at)}
            </span>
            <span className="flex items-center gap-1">
              <MessageSquare className="w-3.5 h-3.5" />
              {lesson.messages_count} mensajes
            </span>
            {lesson.duration_minutes > 0 && (
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" />
                {lesson.duration_minutes} min
              </span>
            )}
          </div>
          
          {lesson.skills_practiced && lesson.skills_practiced.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-3">
              {lesson.skills_practiced.map((skill) => (
                <span 
                  key={skill}
                  className="px-2 py-0.5 bg-primary-50 text-primary-700 text-xs rounded-full"
                >
                  {skill}
                </span>
              ))}
            </div>
          )}
        </div>
        
        <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
      </div>
    </div>
  )
}
