import { useState } from 'react'
import { useLessons } from '../hooks/useLessons'
import LessonCard from '../components/LessonCard'
import { BookOpen, ChevronDown, X } from 'lucide-react'
import { api } from '../api/client'

export default function Lessons() {
  const { lessons, loading, error, hasMore, loadMore, refetch } = useLessons()
  const [selectedLesson, setSelectedLesson] = useState(null)
  const [lessonDetail, setLessonDetail] = useState(null)
  const [loadingDetail, setLoadingDetail] = useState(false)

  const handleLessonClick = async (lesson) => {
    setSelectedLesson(lesson)
    setLoadingDetail(true)
    try {
      const response = await api.getLessonDetail(lesson.id)
      setLessonDetail(response.data)
    } catch (err) {
      console.error('Error loading lesson detail:', err)
    } finally {
      setLoadingDetail(false)
    }
  }

  const closeModal = () => {
    setSelectedLesson(null)
    setLessonDetail(null)
  }

  if (loading && lessons.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500 mb-4">Error al cargar las lecciones</p>
        <button onClick={refetch} className="btn-primary">
          Reintentar
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <BookOpen className="w-6 h-6 text-primary-500" />
          Historial de Lecciones
        </h1>
        <p className="text-gray-500 mt-1">
          Revisa todas tus conversaciones y progreso
        </p>
      </div>

      {/* Lessons List */}
      {lessons.length === 0 ? (
        <div className="text-center py-12">
          <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">Aún no tienes lecciones</p>
          <p className="text-sm text-gray-400 mt-1">
            Envía un mensaje al bot para comenzar tu primera lección
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {lessons.map((lesson) => (
            <LessonCard
              key={lesson.id}
              lesson={lesson}
              onClick={handleLessonClick}
            />
          ))}

          {hasMore && (
            <button
              onClick={loadMore}
              disabled={loading}
              className="w-full py-3 text-primary-600 hover:bg-primary-50 rounded-xl font-medium flex items-center justify-center gap-2 transition-colors"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
              ) : (
                <>
                  <ChevronDown className="w-5 h-5" />
                  Cargar más
                </>
              )}
            </button>
          )}
        </div>
      )}

      {/* Lesson Detail Modal */}
      {selectedLesson && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
            {/* Modal Header */}
            <div className="p-4 border-b border-gray-100 flex items-center justify-between">
              <h3 className="font-semibold text-gray-900">
                {selectedLesson.topic || 'Detalle de Lección'}
              </h3>
              <button
                onClick={closeModal}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-4 overflow-y-auto max-h-[60vh]">
              {loadingDetail ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                </div>
              ) : lessonDetail ? (
                <div className="space-y-4">
                  {/* Summary */}
                  {lessonDetail.summary && (
                    <div className="bg-gray-50 rounded-xl p-4">
                      <p className="text-sm text-gray-600">{lessonDetail.summary}</p>
                    </div>
                  )}

                  {/* Messages */}
                  <div className="space-y-3">
                    {lessonDetail.messages?.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                            message.role === 'user'
                              ? 'bg-primary-500 text-white'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                          <p className={`text-xs mt-1 ${
                            message.role === 'user' ? 'text-primary-200' : 'text-gray-400'
                          }`}>
                            {new Date(message.created_at).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* AI Evaluation */}
                  {lessonDetail.ai_evaluation && (
                    <div className="border-t border-gray-100 pt-4 mt-4">
                      <h4 className="font-medium text-gray-900 mb-3">Evaluación</h4>
                      <div className="grid grid-cols-2 gap-3">
                        {lessonDetail.ai_evaluation.vocabulary_score !== undefined && (
                          <div className="bg-purple-50 rounded-lg p-3">
                            <p className="text-xs text-purple-600">Vocabulario</p>
                            <p className="text-lg font-bold text-purple-700">
                              {lessonDetail.ai_evaluation.vocabulary_score}%
                            </p>
                          </div>
                        )}
                        {lessonDetail.ai_evaluation.grammar_score !== undefined && (
                          <div className="bg-blue-50 rounded-lg p-3">
                            <p className="text-xs text-blue-600">Gramática</p>
                            <p className="text-lg font-bold text-blue-700">
                              {lessonDetail.ai_evaluation.grammar_score}%
                            </p>
                          </div>
                        )}
                        {lessonDetail.ai_evaluation.fluency_score !== undefined && (
                          <div className="bg-green-50 rounded-lg p-3">
                            <p className="text-xs text-green-600">Fluidez</p>
                            <p className="text-lg font-bold text-green-700">
                              {lessonDetail.ai_evaluation.fluency_score}%
                            </p>
                          </div>
                        )}
                        {lessonDetail.ai_evaluation.comprehension_score !== undefined && (
                          <div className="bg-amber-50 rounded-lg p-3">
                            <p className="text-xs text-amber-600">Comprensión</p>
                            <p className="text-lg font-bold text-amber-700">
                              {lessonDetail.ai_evaluation.comprehension_score}%
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">
                  No se pudo cargar el detalle
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
