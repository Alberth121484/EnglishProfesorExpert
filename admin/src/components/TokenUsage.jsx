import { useState, useEffect } from 'react';
import { DollarSign, MessageSquare, TrendingUp, RefreshCw } from 'lucide-react';
import { adminApi } from '../api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function TokenUsage() {
  const [tokenData, setTokenData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalCost, setTotalCost] = useState(0);
  const [totalTokens, setTotalTokens] = useState(0);

  const loadTokenUsage = async () => {
    try {
      setLoading(true);
      const response = await adminApi.getTokenUsage(100);
      setTokenData(response.data);
      
      const totals = response.data.reduce((acc, item) => ({
        tokens: acc.tokens + item.estimated_tokens,
        cost: acc.cost + item.estimated_cost_usd
      }), { tokens: 0, cost: 0 });
      
      setTotalTokens(totals.tokens);
      setTotalCost(totals.cost);
    } catch (err) {
      console.error('Error loading token usage:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTokenUsage();
  }, []);

  const chartData = tokenData.slice(0, 15).map(item => ({
    name: item.name.split(' ')[0],
    tokens: Math.round(item.estimated_tokens / 1000),
    cost: item.estimated_cost_usd
  }));

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold flex items-center gap-2">
            <DollarSign className="text-green-400" />
            Uso de Tokens
          </h1>
          <p className="text-slate-400 mt-1">Estimación de consumo y costos por usuario</p>
        </div>
        <button
          onClick={loadTokenUsage}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
        >
          <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
          Actualizar
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-green-500/20 to-green-600/10 rounded-xl p-6 border border-green-500/30">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-500/20 rounded-lg">
              <DollarSign className="text-green-400" size={24} />
            </div>
            <div>
              <p className="text-slate-400 text-sm">Costo Total Estimado</p>
              <p className="text-2xl font-bold text-green-400">${totalCost.toFixed(4)}</p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/10 rounded-xl p-6 border border-blue-500/30">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-500/20 rounded-lg">
              <TrendingUp className="text-blue-400" size={24} />
            </div>
            <div>
              <p className="text-slate-400 text-sm">Tokens Totales</p>
              <p className="text-2xl font-bold text-blue-400">{(totalTokens / 1000).toFixed(1)}K</p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/10 rounded-xl p-6 border border-purple-500/30">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-500/20 rounded-lg">
              <MessageSquare className="text-purple-400" size={24} />
            </div>
            <div>
              <p className="text-slate-400 text-sm">Mensajes Procesados</p>
              <p className="text-2xl font-bold text-purple-400">
                {tokenData.reduce((acc, item) => acc + item.messages_count, 0)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
        <p className="text-sm text-slate-400">
          💡 <strong className="text-slate-300">Nota:</strong> Los costos son estimaciones basadas en ~4 caracteres por token 
          y tarifa de $0.002/1K tokens (GPT-3.5). Los costos reales pueden variar según el modelo utilizado.
        </p>
      </div>

      {/* Chart */}
      <div className="bg-slate-800 rounded-xl p-4 lg:p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-4">Top 15 Usuarios por Consumo de Tokens</h3>
        {loading ? (
          <div className="h-64 flex items-center justify-center">
            <RefreshCw className="animate-spin text-slate-500" size={32} />
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis type="number" stroke="#64748b" tick={{ fontSize: 12 }} />
              <YAxis dataKey="name" type="category" stroke="#64748b" tick={{ fontSize: 12 }} width={80} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                formatter={(value, name) => [
                  name === 'tokens' ? `${value}K tokens` : `$${value.toFixed(4)}`,
                  name === 'tokens' ? 'Tokens' : 'Costo'
                ]}
              />
              <Bar dataKey="tokens" fill="#3b82f6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Users Table */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        <div className="p-4 border-b border-slate-700">
          <h3 className="font-semibold">Detalle por Usuario</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-700/50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-300">#</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-300">Usuario</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-slate-300">Mensajes</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-slate-300">Tokens Est.</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-slate-300">Costo Est.</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-slate-400">
                    Cargando datos...
                  </td>
                </tr>
              ) : tokenData.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-slate-400">
                    No hay datos disponibles
                  </td>
                </tr>
              ) : (
                tokenData.map((item, index) => (
                  <tr key={item.user_id} className="hover:bg-slate-700/50">
                    <td className="px-4 py-3 text-slate-400">{index + 1}</td>
                    <td className="px-4 py-3 font-medium">{item.name}</td>
                    <td className="px-4 py-3 text-right">{item.messages_count.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right text-blue-400">
                      {(item.estimated_tokens / 1000).toFixed(1)}K
                    </td>
                    <td className="px-4 py-3 text-right text-green-400">
                      ${item.estimated_cost_usd.toFixed(4)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
            {tokenData.length > 0 && (
              <tfoot className="bg-slate-700/30 font-semibold">
                <tr>
                  <td colSpan={2} className="px-4 py-3">Total</td>
                  <td className="px-4 py-3 text-right">
                    {tokenData.reduce((acc, item) => acc + item.messages_count, 0).toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-right text-blue-400">
                    {(totalTokens / 1000).toFixed(1)}K
                  </td>
                  <td className="px-4 py-3 text-right text-green-400">
                    ${totalCost.toFixed(4)}
                  </td>
                </tr>
              </tfoot>
            )}
          </table>
        </div>
      </div>
    </div>
  );
}

export default TokenUsage;
