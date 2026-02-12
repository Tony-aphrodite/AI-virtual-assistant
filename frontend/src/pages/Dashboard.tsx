import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Phone, Clock, TrendingUp, CheckCircle } from 'lucide-react';
import { dashboardApi } from '@/services/api';
import type { DashboardStats, Call } from '@/types';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentCalls, setRecentCalls] = useState<Call[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsRes, callsRes] = await Promise.all([
        dashboardApi.getStats(),
        dashboardApi.getRecentCalls(5),
      ]);
      setStats(statsRes.data);
      setRecentCalls(callsRes.data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Cargando...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Resumen de actividad del asistente virtual
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total de Llamadas"
          value={stats?.total_calls || 0}
          icon={Phone}
          color="blue"
        />
        <StatCard
          title="Llamadas Hoy"
          value={stats?.today_calls || 0}
          icon={TrendingUp}
          color="green"
        />
        <StatCard
          title="Duración Promedio"
          value={`${Math.round(stats?.avg_duration || 0)}s`}
          icon={Clock}
          color="purple"
        />
        <StatCard
          title="Tasa de Éxito"
          value={`${Math.round((stats?.success_rate || 0) * 100)}%`}
          icon={CheckCircle}
          color="emerald"
        />
      </div>

      {/* Recent Calls */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">
            Llamadas Recientes
          </h2>
          <Link
            to="/calls"
            className="text-sm font-medium text-primary-600 hover:text-primary-700"
          >
            Ver todas →
          </Link>
        </div>

        {recentCalls.length === 0 ? (
          <div className="py-12 text-center text-gray-500">
            No hay llamadas recientes
          </div>
        ) : (
          <div className="space-y-4">
            {recentCalls.map((call) => (
              <CallListItem key={call.id} call={call} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ElementType;
  color: string;
}

function StatCard({ title, value, icon: Icon, color }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    emerald: 'bg-emerald-100 text-emerald-600',
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color as keyof typeof colorClasses]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
}

interface CallListItemProps {
  call: Call;
}

function CallListItem({ call }: CallListItemProps) {
  const isInbound = call.direction === 'inbound';

  return (
    <Link
      to={`/calls/${call.id}`}
      className="flex items-center justify-between p-4 rounded-lg hover:bg-gray-50 transition-colors"
    >
      <div className="flex items-center space-x-4">
        <div className={`p-2 rounded-lg ${isInbound ? 'bg-green-100' : 'bg-blue-100'}`}>
          <Phone className={`w-5 h-5 ${isInbound ? 'text-green-600' : 'text-blue-600'}`} />
        </div>
        <div>
          <div className="font-medium text-gray-900">{call.from_number}</div>
          <div className="text-sm text-gray-500">
            {formatDistanceToNow(new Date(call.created_at), {
              addSuffix: true,
              locale: es,
            })}
          </div>
        </div>
      </div>
      <div className="flex items-center space-x-4">
        {call.duration && (
          <div className="text-sm text-gray-600">{call.duration}s</div>
        )}
        <div className={`
          px-3 py-1 text-xs font-medium rounded-full
          ${call.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}
        `}>
          {call.status}
        </div>
      </div>
    </Link>
  );
}
