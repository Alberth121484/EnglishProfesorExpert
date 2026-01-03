import { useState, useEffect } from 'react';
import { 
  Users, TrendingUp, MessageSquare, BookOpen,
  UserPlus, Activity, Calendar, RefreshCw
} from 'lucide-react';
import { adminApi } from '../api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const StatCard = ({ title, value, icon: Icon, change, changeType, color = 'blue' }) => {
  const colors = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600',
  };

  return (
    <div className="bg-slate-800 rounded-xl p-4 lg:p-6 border border-slate-700">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-slate-400 text-sm">{title}</p>
          <p className="text-2xl lg:text-3xl font-bold mt-1">{value}</p>
          {change !== undefined && (
            <p className={`text-sm mt-2 ${changeType === 'up' ? 'text-green-400' : 'text-red-400'}`}>
              {changeType === 'up' ? '↑' : '↓'} {change}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg bg-gradient-to-br ${colors[color]}`}>
          <Icon size={24} className="text-white" />
        </div>
      </div>
    </div>
  );
};

const COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

function Dashboard({ overview, loading, onRefresh }) {
  const [dailyStats, setDailyStats] = useState([]);
  const [levelStats, setLevelStats] = useState([]);
  const [engagement, setEngagement] = useState(null);
  const [loadingCharts, setLoadingCharts] = useState(true);

  useEffect(() => {
    const loadChartData = async () => {
      try {
        setLoadingCharts(true);
        const [daily, levels, engage] = await Promise.all([
          adminApi.getDailyStats(14),
          adminApi.getUsageByLevel(),
          adminApi.getEngagement()
        ]);
        setDailyStats(daily.data);
        setLevelStats(levels.data);
        setEngagement(engage.data);
      } catch (err) {
        console.error('Error loading chart data:', err);
      } finally {
        setLoadingCharts(false);
      }
    };
    loadChartData();
  }, []);

  if (loading && !overview) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="animate-spin text-blue-400" size={48} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold">Dashboard</h1>
          <p className="text-slate-400 mt-1">Resumen general del tutor de inglés</p>
        </div>
        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
        >
          <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
          Actualizar
        </button>
      </div>

      {/* Main Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          title="Total Usuarios" 
          value={overview?.total_users || 0} 
          icon={Users} 
          color="blue"
        />
        <StatCard 
          title="Activos Hoy" 
          value={overview?.active_users_today || 0} 
          icon={Activity}
          color="green"
        />
        <StatCard 
          title="Nuevos (7 días)" 
          value={overview?.new_users_week || 0} 
          icon={UserPlus}
          color="purple"
        />
        <StatCard 
          title="Total Lecciones" 
          value={overview?.total_lessons || 0} 
          icon={BookOpen}
          color="orange"
        />
      </div>

      {/* Secondary Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <p className="text-slate-400 text-sm">Activos (7 días)</p>
          <p className="text-xl font-bold text-blue-400">{overview?.active_users_week || 0}</p>
        </div>
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <p className="text-slate-400 text-sm">Activos (30 días)</p>
          <p className="text-xl font-bold text-green-400">{overview?.active_users_month || 0}</p>
        </div>
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <p className="text-slate-400 text-sm">Promedio Lecciones/Usuario</p>
          <p className="text-xl font-bold text-purple-400">{overview?.avg_lessons_per_user || 0}</p>
        </div>
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <p className="text-slate-400 text-sm">Promedio Racha (días)</p>
          <p className="text-xl font-bold text-orange-400">{overview?.avg_streak_days || 0}</p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activity Chart */}
        <div className="bg-slate-800 rounded-xl p-4 lg:p-6 border border-slate-700">
          <h3 className="text-lg font-semibold mb-4">Actividad (últimos 14 días)</h3>
          {loadingCharts ? (
            <div className="h-64 flex items-center justify-center">
              <RefreshCw className="animate-spin text-slate-500" />
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={dailyStats}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis 
                  dataKey="date" 
                  stroke="#64748b"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(v) => v.slice(5)}
                />
                <YAxis stroke="#64748b" tick={{ fontSize: 12 }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                  labelStyle={{ color: '#f1f5f9' }}
                />
                <Line type="monotone" dataKey="active_users" stroke="#3b82f6" strokeWidth={2} name="Usuarios Activos" />
                <Line type="monotone" dataKey="new_users" stroke="#22c55e" strokeWidth={2} name="Nuevos" />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Level Distribution */}
        <div className="bg-slate-800 rounded-xl p-4 lg:p-6 border border-slate-700">
          <h3 className="text-lg font-semibold mb-4">Distribución por Nivel</h3>
          {loadingCharts ? (
            <div className="h-64 flex items-center justify-center">
              <RefreshCw className="animate-spin text-slate-500" />
            </div>
          ) : (
            <div className="flex flex-col lg:flex-row items-center gap-4">
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={levelStats}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={2}
                    dataKey="user_count"
                    nameKey="level"
                  >
                    {levelStats.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex flex-wrap gap-2 justify-center">
                {levelStats.map((item, index) => (
                  <div key={item.level} className="flex items-center gap-2 text-sm">
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: COLORS[index % COLORS.length] }}
                    />
                    <span>{item.level}: {item.percentage}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Engagement Stats */}
      {engagement && (
        <div className="bg-slate-800 rounded-xl p-4 lg:p-6 border border-slate-700">
          <h3 className="text-lg font-semibold mb-4">📊 Métricas de Engagement</h3>
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-slate-700/50 rounded-lg p-4 text-center">
              <p className="text-slate-400 text-sm">Retención 7 días</p>
              <p className="text-2xl font-bold text-green-400">{engagement.retention_rate_7d}%</p>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-4 text-center">
              <p className="text-slate-400 text-sm">Retención 30 días</p>
              <p className="text-2xl font-bold text-blue-400">{engagement.retention_rate_30d}%</p>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-4 text-center">
              <p className="text-slate-400 text-sm">Tasa de Abandono</p>
              <p className="text-2xl font-bold text-red-400">{engagement.churn_rate}%</p>
            </div>
          </div>
        </div>
      )}

      {/* Messages Stats */}
      <div className="bg-slate-800 rounded-xl p-4 lg:p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-4">💬 Estadísticas de Mensajes</h3>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-3xl font-bold text-blue-400">{overview?.total_messages || 0}</p>
            <p className="text-slate-400 text-sm mt-1">Total Mensajes</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-green-400">{overview?.total_lessons || 0}</p>
            <p className="text-slate-400 text-sm mt-1">Total Lecciones</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-purple-400">
              {overview?.total_lessons > 0 
                ? Math.round(overview.total_messages / overview.total_lessons) 
                : 0}
            </p>
            <p className="text-slate-400 text-sm mt-1">Msgs/Lección</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-orange-400">{overview?.new_users_month || 0}</p>
            <p className="text-slate-400 text-sm mt-1">Nuevos (mes)</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
