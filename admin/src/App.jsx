import { useState, useEffect } from 'react';
import { 
  Users, TrendingUp, MessageSquare, Clock, 
  BarChart3, UserMinus, DollarSign, Activity,
  Menu, X, RefreshCw, ChevronRight
} from 'lucide-react';
import { adminApi } from './api';
import Dashboard from './components/Dashboard';
import UsersPage from './components/UsersPage';
import ChurnedUsers from './components/ChurnedUsers';
import TokenUsage from './components/TokenUsage';
import Analytics from './components/Analytics';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
  { id: 'users', label: 'Usuarios', icon: Users },
  { id: 'churned', label: 'Inactivos', icon: UserMinus },
  { id: 'tokens', label: 'Uso de Tokens', icon: DollarSign },
  { id: 'analytics', label: 'Analíticas', icon: Activity },
];

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState(null);
  const [error, setError] = useState(null);

  const loadOverview = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await adminApi.getOverview();
      setOverview(response.data);
    } catch (err) {
      setError('Error al cargar datos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOverview();
  }, []);

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard overview={overview} loading={loading} onRefresh={loadOverview} />;
      case 'users':
        return <UsersPage />;
      case 'churned':
        return <ChurnedUsers />;
      case 'tokens':
        return <TokenUsage />;
      case 'analytics':
        return <Analytics />;
      default:
        return <Dashboard overview={overview} loading={loading} onRefresh={loadOverview} />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Mobile Header */}
      <header className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-slate-800 border-b border-slate-700 px-4 py-3">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-slate-700 transition-colors"
          >
            {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
          <h1 className="text-lg font-bold text-blue-400">English Tutor Admin</h1>
          <button
            onClick={loadOverview}
            className="p-2 rounded-lg hover:bg-slate-700 transition-colors"
          >
            <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </header>

      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-40 w-64 bg-slate-800 border-r border-slate-700 
        transform transition-transform duration-300 ease-in-out
        lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="p-6 border-b border-slate-700 hidden lg:block">
          <h1 className="text-xl font-bold text-blue-400">🎓 English Tutor</h1>
          <p className="text-sm text-slate-400 mt-1">Panel de Administración</p>
        </div>
        
        <nav className="p-4 mt-16 lg:mt-0">
          <ul className="space-y-2">
            {navItems.map((item) => (
              <li key={item.id}>
                <button
                  onClick={() => {
                    setCurrentPage(item.id);
                    setSidebarOpen(false);
                  }}
                  className={`
                    w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all
                    ${currentPage === item.id 
                      ? 'bg-blue-600 text-white' 
                      : 'text-slate-300 hover:bg-slate-700 hover:text-white'}
                  `}
                >
                  <item.icon size={20} />
                  <span>{item.label}</span>
                  {currentPage === item.id && <ChevronRight size={16} className="ml-auto" />}
                </button>
              </li>
            ))}
          </ul>
        </nav>

        {/* Quick Stats in Sidebar */}
        {overview && (
          <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-700 bg-slate-800/50">
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="bg-slate-700/50 rounded-lg p-2 text-center">
                <p className="text-slate-400">Usuarios</p>
                <p className="text-lg font-bold text-blue-400">{overview.total_users}</p>
              </div>
              <div className="bg-slate-700/50 rounded-lg p-2 text-center">
                <p className="text-slate-400">Activos Hoy</p>
                <p className="text-lg font-bold text-green-400">{overview.active_users_today}</p>
              </div>
            </div>
          </div>
        )}
      </aside>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <main className="lg:ml-64 pt-16 lg:pt-0 min-h-screen">
        <div className="p-4 lg:p-6">
          {error && (
            <div className="mb-4 p-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400">
              {error}
              <button onClick={loadOverview} className="ml-2 underline">Reintentar</button>
            </div>
          )}
          {renderPage()}
        </div>
      </main>
    </div>
  );
}

export default App;
