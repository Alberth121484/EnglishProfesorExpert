import { useState, useEffect } from 'react';
import { Activity, TrendingUp, Users, Calendar, RefreshCw } from 'lucide-react';
import { adminApi } from '../api';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area, BarChart, Bar
} from 'recharts';

function Analytics() {
  const [dailyStats, setDailyStats] = useState([]);
  const [engagement, setEngagement] = useState(null);
  const [levelStats, setLevelStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  const loadData = async () => {
    try {
      setLoading(true);
      const [daily, engage, levels] = await Promise.all([
        adminApi.getDailyStats(days),
        adminApi.getEngagement(),
        adminApi.getUsageByLevel()
      ]);
      setDailyStats(daily.data);
      setEngagement(engage.data);
      setLevelStats(levels.data);
    } catch (err) {
      console.error('Error loading analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [days]);

  const totalNewUsers = dailyStats.reduce((acc, d) => acc + d.new_users, 0);
  const totalLessons = dailyStats.reduce((acc, d) => acc + d.lessons_count, 0);
  const avgDailyActive = Math.round(dailyStats.reduce((acc, d) => acc + d.active_users, 0) / dailyStats.length) || 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold flex items-center gap-2">
            <Activity className="text-purple-400" />
            Analíticas
          </h1>
          <p className="text-slate-400 mt-1">Métricas detalladas de uso y engagement</p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:border-blue-500"
          >
            <option value={7}>Últimos 7 días</option>
            <option value={14}>Últimos 14 días</option>
            <option value={30}>Últimos 30 días</option>
            <option value={60}>Últimos 60 días</option>
            <option value={90}>Últimos 90 días</option>
          </select>
          <button
            onClick={loadData}
            disabled={loading}
            className="p-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Period Summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <p className="text-slate-400 text-sm">Nuevos usuarios ({days}d)</p>
          <p className="text-2xl font-bold text-green-400 mt-1">{totalNewUsers}</p>
        </div>
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <p className="text-slate-400 text-sm">Lecciones totales ({days}d)</p>
          <p className="text-2xl font-bold text-blue-400 mt-1">{totalLessons}</p>
        </div>
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <p className="text-slate-400 text-sm">Prom. Activos/día</p>
          <p className="text-2xl font-bold text-purple-400 mt-1">{avgDailyActive}</p>
        </div>
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <p className="text-slate-400 text-sm">Prom. Lecciones/día</p>
          <p className="text-2xl font-bold text-orange-400 mt-1">
            {Math.round(totalLessons / days) || 0}
          </p>
        </div>
      </div>

      {/* Engagement Metrics */}
      {engagement && (
        <div className="bg-slate-800 rounded-xl p-4 lg:p-6 border border-slate-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="text-green-400" />
            Métricas de Engagement
          </h3>
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-gradient-to-br from-green-500/10 to-green-600/5 rounded-lg p-4 border border-green-500/20">
              <p className="text-slate-400 text-sm">Retención 7 días</p>
              <p className="text-3xl font-bold text-green-400">{engagement.retention_rate_7d}%</p>
              <p className="text-xs text-slate-500 mt-1">Usuarios que regresan en 7 días</p>
            </div>
            <div className="bg-gradient-to-br from-blue-500/10 to-blue-600/5 rounded-lg p-4 border border-blue-500/20">
              <p className="text-slate-400 text-sm">Retención 30 días</p>
              <p className="text-3xl font-bold text-blue-400">{engagement.retention_rate_30d}%</p>
              <p className="text-xs text-slate-500 mt-1">Usuarios que regresan en 30 días</p>
            </div>
            <div className="bg-gradient-to-br from-red-500/10 to-red-600/5 rounded-lg p-4 border border-red-500/20">
              <p className="text-slate-400 text-sm">Tasa de Abandono</p>
              <p className="text-3xl font-bold text-red-400">{engagement.churn_rate}%</p>
              <p className="text-xs text-slate-500 mt-1">Usuarios inactivos +14 días</p>
            </div>
          </div>
        </div>
      )}

      {/* Activity Chart */}
      <div className="bg-slate-800 rounded-xl p-4 lg:p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-4">📈 Actividad Diaria</h3>
        {loading ? (
          <div className="h-64 flex items-center justify-center">
            <RefreshCw className="animate-spin text-slate-500" size={32} />
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={dailyStats}>
              <defs>
                <linearGradient id="colorActive" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorNew" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis 
                dataKey="date" 
                stroke="#64748b" 
                tick={{ fontSize: 11 }}
                tickFormatter={(v) => v.slice(5)}
              />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                labelStyle={{ color: '#f1f5f9' }}
              />
              <Area 
                type="monotone" 
                dataKey="active_users" 
                stroke="#3b82f6" 
                fillOpacity={1} 
                fill="url(#colorActive)" 
                name="Usuarios Activos"
              />
              <Area 
                type="monotone" 
                dataKey="new_users" 
                stroke="#22c55e" 
                fillOpacity={1} 
                fill="url(#colorNew)" 
                name="Nuevos Usuarios"
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Lessons Chart */}
      <div className="bg-slate-800 rounded-xl p-4 lg:p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-4">📚 Lecciones y Mensajes por Día</h3>
        {loading ? (
          <div className="h-64 flex items-center justify-center">
            <RefreshCw className="animate-spin text-slate-500" size={32} />
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={dailyStats}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis 
                dataKey="date" 
                stroke="#64748b" 
                tick={{ fontSize: 11 }}
                tickFormatter={(v) => v.slice(5)}
              />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                labelStyle={{ color: '#f1f5f9' }}
              />
              <Bar dataKey="lessons_count" fill="#8b5cf6" name="Lecciones" radius={[4, 4, 0, 0]} />
              <Bar dataKey="messages_count" fill="#f59e0b" name="Mensajes" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Level Distribution */}
      <div className="bg-slate-800 rounded-xl p-4 lg:p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-4">🎯 Distribución por Nivel</h3>
        <div className="space-y-3">
          {levelStats.map((level, index) => {
            const colors = ['bg-gray-500', 'bg-green-500', 'bg-blue-500', 'bg-purple-500', 'bg-orange-500', 'bg-red-500'];
            return (
              <div key={level.level} className="flex items-center gap-4">
                <div className="w-20 text-sm font-medium">{level.level}</div>
                <div className="flex-1 bg-slate-700 rounded-full h-6 overflow-hidden">
                  <div 
                    className={`h-full ${colors[index % colors.length]} flex items-center justify-end pr-2 transition-all duration-500`}
                    style={{ width: `${Math.max(level.percentage, 5)}%` }}
                  >
                    <span className="text-xs font-medium">{level.user_count}</span>
                  </div>
                </div>
                <div className="w-16 text-right text-sm text-slate-400">
                  {level.percentage}%
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Insights */}
      <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-xl p-4 lg:p-6 border border-blue-500/20">
        <h3 className="text-lg font-semibold mb-4">💡 Insights</h3>
        <ul className="space-y-2 text-sm">
          {totalNewUsers > 0 && (
            <li className="flex items-start gap-2">
              <span className="text-green-400">✓</span>
              <span>Has conseguido {totalNewUsers} nuevos usuarios en los últimos {days} días.</span>
            </li>
          )}
          {engagement && engagement.retention_rate_7d > 50 && (
            <li className="flex items-start gap-2">
              <span className="text-green-400">✓</span>
              <span>Tu retención a 7 días ({engagement.retention_rate_7d}%) está por encima del promedio.</span>
            </li>
          )}
          {engagement && engagement.churn_rate > 30 && (
            <li className="flex items-start gap-2">
              <span className="text-yellow-400">⚠</span>
              <span>La tasa de abandono ({engagement.churn_rate}%) es alta. Considera enviar recordatorios.</span>
            </li>
          )}
          {levelStats.length > 0 && levelStats[0]?.percentage > 60 && (
            <li className="flex items-start gap-2">
              <span className="text-blue-400">ℹ</span>
              <span>La mayoría de usuarios están en nivel {levelStats[0].level}. El contenido de este nivel es clave.</span>
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}

export default Analytics;
