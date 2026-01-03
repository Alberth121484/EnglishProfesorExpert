import { useState, useEffect } from 'react';
import { Search, Filter, ChevronDown, User, Clock, BookOpen, Flame, ExternalLink } from 'lucide-react';
import { adminApi } from '../api';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [activeOnly, setActiveOnly] = useState(false);
  const [sortBy, setSortBy] = useState('last_activity');
  const [selectedUser, setSelectedUser] = useState(null);
  const [userDetail, setUserDetail] = useState(null);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await adminApi.getUsers({
        active_only: activeOnly,
        sort_by: sortBy,
        limit: 200
      });
      setUsers(response.data);
    } catch (err) {
      console.error('Error loading users:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadUserDetail = async (userId) => {
    try {
      const response = await adminApi.getUserDetail(userId);
      setUserDetail(response.data);
    } catch (err) {
      console.error('Error loading user detail:', err);
    }
  };

  useEffect(() => {
    loadUsers();
  }, [activeOnly, sortBy]);

  useEffect(() => {
    if (selectedUser) {
      loadUserDetail(selectedUser);
    }
  }, [selectedUser]);

  const filteredUsers = users.filter(user => 
    user.name.toLowerCase().includes(search.toLowerCase()) ||
    user.telegram_id.toString().includes(search) ||
    (user.username && user.username.toLowerCase().includes(search.toLowerCase()))
  );

  const getLevelColor = (level) => {
    const colors = {
      'PRE_A1': 'bg-gray-500',
      'A1': 'bg-green-500',
      'A2': 'bg-blue-500',
      'B1': 'bg-purple-500',
      'B2': 'bg-orange-500',
      'C1': 'bg-red-500',
    };
    return colors[level] || 'bg-gray-500';
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold">Usuarios</h1>
          <p className="text-slate-400 mt-1">{users.length} usuarios registrados</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
          <input
            type="text"
            placeholder="Buscar por nombre, ID o username..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:border-blue-500"
          />
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={() => setActiveOnly(!activeOnly)}
            className={`px-4 py-2 rounded-lg border transition-colors ${
              activeOnly 
                ? 'bg-green-600 border-green-600 text-white' 
                : 'bg-slate-800 border-slate-700 text-slate-300 hover:border-slate-600'
            }`}
          >
            Solo Activos
          </button>
          
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:border-blue-500"
          >
            <option value="last_activity">Última actividad</option>
            <option value="registered_at">Fecha registro</option>
            <option value="total_lessons">Lecciones</option>
            <option value="streak_days">Racha</option>
          </select>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-700/50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-300">Usuario</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-300 hidden sm:table-cell">Nivel</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-300 hidden md:table-cell">Lecciones</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-300 hidden lg:table-cell">Racha</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-300">Estado</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-300 hidden sm:table-cell">Última actividad</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate-400">
                    Cargando usuarios...
                  </td>
                </tr>
              ) : filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate-400">
                    No se encontraron usuarios
                  </td>
                </tr>
              ) : (
                filteredUsers.map((user) => (
                  <tr 
                    key={user.user_id} 
                    className="hover:bg-slate-700/50 cursor-pointer transition-colors"
                    onClick={() => setSelectedUser(user.user_id)}
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                          <span className="text-sm font-bold">{user.name.charAt(0).toUpperCase()}</span>
                        </div>
                        <div>
                          <p className="font-medium">{user.name}</p>
                          <p className="text-sm text-slate-400">@{user.username || user.telegram_id}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 hidden sm:table-cell">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getLevelColor(user.level)}`}>
                        {user.level}
                      </span>
                    </td>
                    <td className="px-4 py-3 hidden md:table-cell">
                      <div className="flex items-center gap-1">
                        <BookOpen size={16} className="text-slate-400" />
                        <span>{user.total_lessons}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 hidden lg:table-cell">
                      <div className="flex items-center gap-1">
                        <Flame size={16} className="text-orange-400" />
                        <span>{user.streak_days} días</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        user.is_active 
                          ? 'bg-green-500/20 text-green-400' 
                          : 'bg-red-500/20 text-red-400'
                      }`}>
                        {user.is_active ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-400 hidden sm:table-cell">
                      {user.last_activity 
                        ? formatDistanceToNow(new Date(user.last_activity), { addSuffix: true, locale: es })
                        : 'Nunca'
                      }
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* User Detail Modal */}
      {selectedUser && userDetail && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={() => setSelectedUser(null)}>
          <div 
            className="bg-slate-800 rounded-xl border border-slate-700 w-full max-w-lg max-h-[80vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 border-b border-slate-700">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                  <span className="text-2xl font-bold">{userDetail.name.charAt(0).toUpperCase()}</span>
                </div>
                <div>
                  <h2 className="text-xl font-bold">{userDetail.name}</h2>
                  <p className="text-slate-400">@{userDetail.username || userDetail.telegram_id}</p>
                  <span className={`inline-block mt-1 px-2 py-1 rounded text-xs font-medium ${getLevelColor(userDetail.level)}`}>
                    {userDetail.level}
                  </span>
                </div>
              </div>
            </div>
            
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-700/50 rounded-lg p-3">
                  <p className="text-slate-400 text-sm">Lecciones</p>
                  <p className="text-xl font-bold">{userDetail.total_lessons}</p>
                </div>
                <div className="bg-slate-700/50 rounded-lg p-3">
                  <p className="text-slate-400 text-sm">Racha</p>
                  <p className="text-xl font-bold">{userDetail.streak_days} días</p>
                </div>
                <div className="bg-slate-700/50 rounded-lg p-3">
                  <p className="text-slate-400 text-sm">Minutos totales</p>
                  <p className="text-xl font-bold">{userDetail.total_minutes}</p>
                </div>
                <div className="bg-slate-700/50 rounded-lg p-3">
                  <p className="text-slate-400 text-sm">Días inactivo</p>
                  <p className="text-xl font-bold">{userDetail.days_since_last_activity}</p>
                </div>
              </div>

              <div>
                <p className="text-slate-400 text-sm mb-2">Telegram ID</p>
                <p className="font-mono bg-slate-700/50 rounded px-3 py-2">{userDetail.telegram_id}</p>
              </div>

              <div>
                <p className="text-slate-400 text-sm mb-2">Registrado</p>
                <p>{new Date(userDetail.registered_at).toLocaleDateString('es-MX', { 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}</p>
              </div>

              {userDetail.recent_lessons?.length > 0 && (
                <div>
                  <p className="text-slate-400 text-sm mb-2">Lecciones recientes</p>
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {userDetail.recent_lessons.map((lesson) => (
                      <div key={lesson.id} className="bg-slate-700/50 rounded-lg p-2 text-sm flex justify-between items-center">
                        <span>{lesson.skill || 'General'}</span>
                        <span className="text-slate-400">
                          {new Date(lesson.started_at).toLocaleDateString('es-MX')}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="p-4 border-t border-slate-700">
              <button
                onClick={() => setSelectedUser(null)}
                className="w-full py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UsersPage;
