import { useState, useEffect } from 'react';
import { UserMinus, AlertTriangle, Send, Clock, BookOpen } from 'lucide-react';
import { adminApi } from '../api';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

function ChurnedUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [daysInactive, setDaysInactive] = useState(14);

  const loadChurnedUsers = async () => {
    try {
      setLoading(true);
      const response = await adminApi.getChurnedUsers(daysInactive);
      setUsers(response.data);
    } catch (err) {
      console.error('Error loading churned users:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadChurnedUsers();
  }, [daysInactive]);

  const getInactivityColor = (days) => {
    if (days >= 30) return 'text-red-400 bg-red-500/20';
    if (days >= 21) return 'text-orange-400 bg-orange-500/20';
    return 'text-yellow-400 bg-yellow-500/20';
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold flex items-center gap-2">
            <UserMinus className="text-red-400" />
            Usuarios Inactivos
          </h1>
          <p className="text-slate-400 mt-1">
            {users.length} usuarios sin actividad en más de {daysInactive} días
          </p>
        </div>
      </div>

      {/* Filter */}
      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <div className="flex flex-col sm:flex-row sm:items-center gap-4">
          <label className="text-slate-400">Mostrar usuarios inactivos por más de:</label>
          <select
            value={daysInactive}
            onChange={(e) => setDaysInactive(Number(e.target.value))}
            className="px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-blue-500"
          >
            <option value={7}>7 días</option>
            <option value={14}>14 días</option>
            <option value={21}>21 días</option>
            <option value={30}>30 días</option>
            <option value={60}>60 días</option>
            <option value={90}>90 días</option>
          </select>
        </div>
      </div>

      {/* Alert Box */}
      <div className="bg-yellow-500/10 border border-yellow-500/50 rounded-xl p-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="text-yellow-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-yellow-400">Usuarios en riesgo de abandono</p>
            <p className="text-sm text-slate-300 mt-1">
              Estos usuarios no han interactuado con el tutor recientemente. 
              Considera enviarles un recordatorio o encuesta para recuperarlos.
            </p>
          </div>
        </div>
      </div>

      {/* Users List */}
      <div className="space-y-3">
        {loading ? (
          <div className="text-center py-12 text-slate-400">
            Cargando usuarios inactivos...
          </div>
        ) : users.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-green-400 text-5xl mb-4">🎉</div>
            <p className="text-xl font-medium">¡Excelente!</p>
            <p className="text-slate-400 mt-2">
              No hay usuarios inactivos por más de {daysInactive} días
            </p>
          </div>
        ) : (
          users.map((user) => (
            <div 
              key={user.user_id}
              className="bg-slate-800 rounded-xl p-4 border border-slate-700 hover:border-slate-600 transition-colors"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center">
                    <span className="text-lg font-bold text-slate-300">
                      {user.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <p className="font-medium">{user.name}</p>
                    <div className="flex items-center gap-3 text-sm text-slate-400 mt-1">
                      <span className="flex items-center gap-1">
                        <BookOpen size={14} />
                        {user.total_lessons} lecciones
                      </span>
                      <span className={`px-2 py-0.5 rounded text-xs ${
                        user.level === 'PRE_A1' ? 'bg-gray-500/30' : 'bg-blue-500/30'
                      }`}>
                        {user.level}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className={`px-3 py-1 rounded-full text-sm font-medium ${getInactivityColor(user.days_inactive)}`}>
                      {user.days_inactive} días inactivo
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      Última vez: {user.last_activity 
                        ? formatDistanceToNow(new Date(user.last_activity), { addSuffix: true, locale: es })
                        : 'Nunca'
                      }
                    </p>
                  </div>
                  
                  <a
                    href={`https://t.me/${user.telegram_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
                    title="Contactar por Telegram"
                  >
                    <Send size={18} />
                  </a>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Summary */}
      {users.length > 0 && (
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <h3 className="font-semibold mb-3">📊 Resumen de Inactividad</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-400">
                {users.filter(u => u.days_inactive < 21).length}
              </p>
              <p className="text-sm text-slate-400">14-21 días</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-400">
                {users.filter(u => u.days_inactive >= 21 && u.days_inactive < 30).length}
              </p>
              <p className="text-sm text-slate-400">21-30 días</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-red-400">
                {users.filter(u => u.days_inactive >= 30).length}
              </p>
              <p className="text-sm text-slate-400">+30 días</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-slate-300">
                {Math.round(users.reduce((acc, u) => acc + u.total_lessons, 0) / users.length) || 0}
              </p>
              <p className="text-sm text-slate-400">Prom. Lecciones</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChurnedUsers;
