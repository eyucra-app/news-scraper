'use client';

import { useEffect, useState } from 'react';
import {
  getHeadlineStats,
  getSources,
  startScraping,
  startScheduler,
  stopScheduler,
  getScrapingStatus,
  testSingularConnection,
  getHeadlines,
} from '@/lib/api';
import type { ScrapeStats, NewsSource, SchedulerStatus, Headline } from '@/lib/types';
import { formatBoliviaTime } from '@/lib/timezone';

export default function Dashboard() {
  const [stats, setStats] = useState<ScrapeStats | null>(null);
  const [sources, setSources] = useState<NewsSource[]>([]);
  const [schedulerStatus, setSchedulerStatus] = useState<SchedulerStatus | null>(null);
  const [headlines, setHeadlines] = useState<Headline[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionMessage, setActionMessage] = useState('');

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  async function loadData() {
    try {
      const [statsData, sourcesData, statusData, headlinesData] = await Promise.all([
        getHeadlineStats(),
        getSources(true),
        getScrapingStatus(),
        getHeadlines({ limit: 10 }),
      ]);
      setStats(statsData);
      setSources(sourcesData);
      setSchedulerStatus(statusData);
      setHeadlines(headlinesData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleStartScraping() {
    setActionMessage('⏳ Iniciando scraping...');
    try {
      const result = await startScraping();
      setActionMessage(
        `✅ Scraping completado: ${result.stats.headlines_new} nuevos titulares de ${result.stats.sources_scraped} fuentes`
      );
      loadData();
    } catch (error: any) {
      setActionMessage(`❌ Error: ${error.message}`);
    }
  }

  async function handleStartScheduler() {
    try {
      await startScheduler(5);
      setActionMessage('✅ Scheduler automático activado (cada 5 minutos)');
      loadData();
    } catch (error: any) {
      setActionMessage(`❌ Error: ${error.message}`);
    }
  }

  async function handleStopScheduler() {
    try {
      await stopScheduler();
      setActionMessage('⏸️ Scheduler pausado');
      loadData();
    } catch (error: any) {
      setActionMessage(`❌ Error: ${error.message}`);
    }
  }

  async function handleTestSingular() {
    setActionMessage('🧪 Probando conexión con Singular.live...');
    try {
      const result = await testSingularConnection();
      setActionMessage(result.status === 'success' ? '✅ ' + result.message : '❌ ' + result.message);
    } catch (error: any) {
      setActionMessage(`❌ Error: ${error.message}`);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-400">Cargando dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-slate-400">Vista general del sistema de scraping de noticias</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Titulares"
          value={stats?.total || 0}
          icon="📋"
          color="from-blue-500 to-cyan-500"
        />
        <StatCard
          title="Enviados"
          value={stats?.sent || 0}
          icon="✅"
          color="from-emerald-500 to-teal-500"
        />
        <StatCard
          title="Pendientes"
          value={stats?.unsent || 0}
          icon="⏳"
          color="from-amber-500 to-orange-500"
        />
        <StatCard
          title="Fuentes Activas"
          value={sources.length}
          icon="🌐"
          color="from-purple-500 to-pink-500"
        />
      </div>

      {/* Controls */}
      <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700 p-6">
        <h2 className="text-xl font-semibold text-white mb-4">🎯 Control de Scraping</h2>
        <div className="flex flex-wrap gap-3 mb-4">
          <button
            onClick={handleStartScraping}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition flex items-center space-x-2"
          >
            <span>▶️</span>
            <span>Iniciar Scraping</span>
          </button>
          <button
            onClick={handleStartScheduler}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-medium transition flex items-center space-x-2"
          >
            <span>⏰</span>
            <span>Activar Automático</span>
          </button>
          <button
            onClick={handleStopScheduler}
            className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg font-medium transition flex items-center space-x-2"
          >
            <span>⏸️</span>
            <span>Pausar Automático</span>
          </button>
          <button
            onClick={handleTestSingular}
            className="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-lg font-medium transition flex items-center space-x-2"
          >
            <span>🧪</span>
            <span>Test Singular.live</span>
          </button>
        </div>
        {actionMessage && (
          <div className="p-3 bg-slate-700/50 rounded-lg text-sm text-slate-300 border border-slate-600">
            {actionMessage}
          </div>
        )}
        {schedulerStatus && (
          <div className="mt-4 text-sm text-slate-400">
            <span className="font-medium">Estado Scheduler:</span>{' '}
            {schedulerStatus.running ? (
              <span className="text-emerald-400">
                ✓ Activo {schedulerStatus.paused && '(pausado)'}
              </span>
            ) : (
              <span className="text-slate-500">○ Inactivo</span>
            )}
            {schedulerStatus.next_run && (
              <span className="ml-3">
                Próximo: {formatBoliviaTime(schedulerStatus.next_run)}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Recent Headlines */}
      <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700 p-6">
        <h2 className="text-xl font-semibold text-white mb-4">📜 Últimos Titulares</h2>
        {headlines.length === 0 ? (
          <div className="text-center py-12 text-slate-400">
            <div className="text-5xl mb-4">📭</div>
            <p>No hay titulares aún. Inicia el scraping para comenzar.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">Titular</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-slate-400 w-32">Fuente</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-slate-400 w-32">Estado</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-slate-400 w-40">Fecha</th>
                </tr>
              </thead>
              <tbody>
                {headlines.map((headline) => (
                  <tr key={headline.id} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                    <td className="py-3 px-4 text-slate-300">{headline.title}</td>
                    <td className="py-3 px-4 text-slate-400 text-sm">{headline.source_name}</td>
                    <td className="py-3 px-4">
                      {headline.sent_to_singular ? (
                        <span className="inline-block px-3 py-1 bg-emerald-500/20 text-emerald-400 rounded-full text-xs font-medium whitespace-nowrap">
                          ✓ Enviado
                        </span>
                      ) : (
                        <span className="inline-block px-3 py-1 bg-amber-500/20 text-amber-400 rounded-full text-xs font-medium whitespace-nowrap">
                          ⏳ Pendiente
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-slate-400 text-sm whitespace-nowrap">
                      {formatBoliviaTime(headline.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  icon,
  color,
}: {
  title: string;
  value: number;
  icon: string;
  color: string;
}) {
  return (
    <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700 p-6 hover:scale-105 transition-transform">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-slate-400 uppercase tracking-wide">{title}</span>
        <span className="text-2xl">{icon}</span>
      </div>
      <div className={`text-3xl font-bold bg-gradient-to-r ${color} bg-clip-text text-transparent`}>
        {value.toLocaleString()}
      </div>
    </div>
  );
}
