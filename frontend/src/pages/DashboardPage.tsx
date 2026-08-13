import React, { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { SideMenu } from '../components/SideMenu';
import { dashboardApi } from '../api/dashboardApi';
import { DashboardMetrics } from '../types/dashboard';
import { AnimatedCounter } from '../components/AnimatedCounter';
import { Clock, Activity, HardDrive, Shield, AlertTriangle, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const data = await dashboardApi.getMetrics();
        setMetrics(data);
        setError(null);
      } catch {
        setError('Erro ao carregar dados do dashboard.');
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  const isTecnico = user?.role === 'tecnico';

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-blue-500 selection:text-white">
      {/* Header do Dashboard */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <SideMenu />
            <div className="flex items-center gap-2">
              <div className="p-2 bg-blue-600/20 text-blue-400 border border-blue-500/30 rounded-xl">
                <HardDrive className="w-5 h-5" />
              </div>
              <div>
                <h1 className="text-base font-bold text-white leading-tight">Gestão de Patrimônio</h1>
                <p className="text-xs text-slate-400">Dashboard de Controle</p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-slate-800/70 border border-slate-700/60 rounded-xl text-xs">
              <span className="text-slate-300 font-medium">{user?.email ? user.email.split('@')[0] : 'Usuário'}</span>
              <span className="px-2 py-0.5 rounded-md bg-blue-500/20 text-blue-300 font-bold uppercase text-[10px] tracking-wider">
                {user?.role}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Conteúdo Principal */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Banner de Boas-Vindas */}
        <div className="mb-8 p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-blue-950/40 to-slate-900 border border-slate-800/80 shadow-xl relative overflow-hidden animate-fade-in">
          <div className="relative z-10 flex items-center gap-4">
            <div className="p-3 bg-blue-500/10 border border-blue-500/20 text-blue-400 rounded-2xl">
              <Shield className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">
                Olá, <span className="text-blue-400">{user?.email ? user.email.split('@')[0] : 'Usuário'}</span>!
              </h2>
              <p className="text-xs sm:text-sm text-slate-400 mt-1">
                {isTecnico
                  ? 'Visão geral do sistema com métricas globais e controle total de patrimônio.'
                  : 'Acompanhe o andamento das suas solicitações de suporte em tempo real.'}
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-xs flex items-center gap-2 animate-fade-in">
            <AlertTriangle className="w-4 h-4" />
            <span>{error}</span>
          </div>
        )}

        {/* Grid de Cards do Dashboard */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((n) => (
              <div key={n} className="h-40 rounded-2xl bg-slate-900/40 border border-slate-800/60 animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-fade-in">
            {/* Card 1: Tickets Pendentes */}
            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 hover:border-amber-500/40 transition-all group shadow-lg flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Tickets Pendentes
                </span>
                <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 group-hover:scale-110 transition-transform">
                  <Clock className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-4">
                <div className="text-3xl font-extrabold text-white tracking-tight">
                  <AnimatedCounter value={metrics?.tickets_pending || 0} />
                </div>
                <p className="text-[11px] text-slate-400 mt-1">
                  {isTecnico ? 'Aguardando atendimento técnico' : 'Aguardando atendimento das suas solicitações'}
                </p>
              </div>
            </div>

            {/* Card 2: Tickets em Andamento */}
            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 hover:border-blue-500/40 transition-all group shadow-lg flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Tickets em Andamento
                </span>
                <div className="p-2.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 group-hover:scale-110 transition-transform">
                  <Activity className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-4">
                <div className="text-3xl font-extrabold text-white tracking-tight">
                  <AnimatedCounter value={metrics?.tickets_in_progress || 0} />
                </div>
                <p className="text-[11px] text-slate-400 mt-1">
                  {isTecnico ? 'Em análise ou intervenção' : 'Suas solicitações sendo atendidas'}
                </p>
              </div>
            </div>

            {/* Card 3: Equipamentos Cadastrados (Apenas Técnico - Cenário 2 & 3) */}
            {isTecnico && metrics?.equipments_total !== undefined && metrics?.equipments_total !== null && (
              <div
                onClick={() => navigate('/equipamentos')}
                data-testid="equipamentos-card"
                className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 hover:border-emerald-500/40 transition-all group shadow-lg flex flex-col justify-between cursor-pointer"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Equipamentos
                  </span>
                  <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 group-hover:scale-110 transition-transform">
                    <HardDrive className="w-5 h-5" />
                  </div>
                </div>
                <div className="mt-4">
                  <div className="text-3xl font-extrabold text-white tracking-tight">
                    <AnimatedCounter value={metrics.equipments_total} />
                  </div>
                  <div className="flex items-center justify-between mt-2">
                    <p className="text-[11px] text-slate-400">Total no patrimônio da empresa</p>
                    <div className="flex items-center gap-1 text-xs text-emerald-400 font-medium group-hover:translate-x-1 transition-transform">
                      <span>Ver painel</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};
