import React from 'react';
import {
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  DollarSign,
  ArrowRight,
  ShieldCheck,
  Zap
} from 'lucide-react';
import { formatINR, formatPercent } from '../../lib/utils';
import { RecoveryOpportunity, BatchSimulationResult } from '../../lib/types';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface OverviewDashboardProps {
  opportunities: RecoveryOpportunity[];
  batchResult: BatchSimulationResult | null;
  onSelectOpportunity: (opp: RecoveryOpportunity) => void;
  onNavigateTab: (tab: any) => void;
}

export const OverviewDashboard: React.FC<OverviewDashboardProps> = ({
  opportunities,
  batchResult,
  onSelectOpportunity,
  onNavigateTab
}) => {
  const totalRevenueAtRisk = opportunities.reduce((acc, o) => acc + o.amount, 0);
  const totalProjectedRecoverable = opportunities.reduce(
    (acc, o) => acc + o.amount * o.assisted_probability,
    0
  );

  const horizon3dAmount = opportunities
    .filter((o) => o.horizon_window === '3d')
    .reduce((acc, o) => acc + o.amount, 0);

  const horizon7dAmount = opportunities
    .filter((o) => o.horizon_window === '7d')
    .reduce((acc, o) => acc + o.amount, 0);

  const horizon30dAmount = opportunities
    .filter((o) => o.horizon_window === '30d')
    .reduce((acc, o) => acc + o.amount, 0);

  const trajectoryData = [
    { day: 'Day 0', Natural: 0, RecoverAI: 0 },
    { day: 'Day 3 (Primary)', Natural: 12, RecoverAI: 28 },
    { day: 'Day 7 (Secondary)', Natural: 24, RecoverAI: 49 },
    { day: 'Day 14 (Mid)', Natural: 31, RecoverAI: 64 },
    { day: 'Day 30 (Macro)', Natural: batchResult ? batchResult.baseline_recovery_rate : 35, RecoverAI: batchResult ? batchResult.recoverai_recovery_rate : 72 }
  ];

  return (
    <div className="space-y-6">
      {/* HERO SECTION — MONEY AT RISK */}
      <div className="spatial-card p-6 rounded-2xl relative overflow-hidden bg-gradient-to-r from-slate-900 via-[#111827] to-[#0f172a] border border-slate-800/80">
        <div className="absolute right-0 top-0 translate-x-12 -translate-y-12 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-400">
                TOTAL PORTFOLIO EXPOSURE
              </span>
              <span className="prov-badge prov-empirical">EMPIRICAL DATASET</span>
            </div>

            <h2 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight fin-number">
              {formatINR(totalRevenueAtRisk)}
            </h2>

            <p className="text-xs text-slate-400 mt-2 flex items-center gap-1.5">
              <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
              <span>Overdue receivables subject to natural recovery decline & payment default risk</span>
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <div className="px-4 py-3 rounded-xl bg-slate-800/60 border border-slate-700/50 text-left min-w-[140px]">
              <div className="text-[11px] font-medium text-slate-400">PROJECTED RECOVERABLE</div>
              <div className="text-xl font-bold text-sky-400 fin-number mt-0.5">
                {formatINR(totalProjectedRecoverable)}
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Action-conditioned EV</div>
            </div>

            <div className="px-4 py-3 rounded-xl bg-slate-800/60 border border-slate-700/50 text-left min-w-[140px]">
              <div className="text-[11px] font-medium text-slate-400">SIMULATED NET GAIN</div>
              <div className="text-xl font-bold text-emerald-400 fin-number mt-0.5">
                {formatINR(batchResult ? batchResult.net_incremental_revenue : 0)}
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Net of intervention costs</div>
            </div>
          </div>
        </div>
      </div>

      {/* KPI METRIC CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="spatial-card p-4 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Natural Baseline Rate</span>
            <span className="prov-badge prov-empirical">Baseline</span>
          </div>
          <div className="text-2xl font-bold text-slate-200 fin-number">
            {formatPercent(batchResult ? batchResult.baseline_recovery_rate : 35.0)}
          </div>
          <div className="text-[11px] text-slate-500">Unassisted 30d settlement rate</div>
        </div>

        <div className="spatial-card p-4 rounded-xl space-y-2 border-indigo-500/30">
          <div className="flex items-center justify-between text-xs text-indigo-300">
            <span>RecoverAI Recovery Rate</span>
            <span className="prov-badge prov-simulated">Simulated Policy</span>
          </div>
          <div className="text-2xl font-bold text-indigo-400 fin-number">
            {formatPercent(batchResult ? batchResult.recoverai_recovery_rate : 72.0)}
          </div>
          <div className="text-[11px] text-emerald-400 font-medium">
            +{formatPercent(batchResult ? (batchResult.recoverai_recovery_rate - batchResult.baseline_recovery_rate) : 37.0)} incremental uplift
          </div>
        </div>

        <div className="spatial-card p-4 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Total Executed Cost</span>
            <span className="prov-badge prov-configured">Configured Costs</span>
          </div>
          <div className="text-2xl font-bold text-amber-400 fin-number">
            {formatINR(batchResult ? batchResult.recoverai_intervention_cost : 0)}
          </div>
          <div className="text-[11px] text-slate-500">Reminders + Retries + Escalations</div>
        </div>

        <div className="spatial-card p-4 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Policy Allowed Rate</span>
            <span className="prov-badge prov-safety">Policy Engine</span>
          </div>
          <div className="text-2xl font-bold text-sky-400 fin-number">
            {formatPercent(
              batchResult && batchResult.total_interventions_executed > 0
                ? ((batchResult.total_interventions_executed - batchResult.blocked_interventions_count) /
                    batchResult.total_interventions_executed) *
                    100
                : 94.2
            )}
          </div>
          <div className="text-[11px] text-slate-500">Disputes & cooldowns enforced</div>
        </div>
      </div>

      {/* RECOVERY HORIZON SUMMARY & ANALYTICAL TRAJECTORY */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 3D / 7D / 30D RECOVERY HORIZON BREAKDOWN */}
        <div className="spatial-card p-5 rounded-xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Operational Recovery Horizons
            </h3>
            <button
              onClick={() => onNavigateTab('RECOVERY')}
              className="text-xs text-sky-400 hover:text-sky-300 font-semibold flex items-center gap-1"
            >
              <span>Explore Horizon</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>

          <div className="space-y-3">
            <div className="p-3 rounded-lg bg-slate-900/80 border border-emerald-500/30 flex items-center justify-between">
              <div>
                <div className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-emerald-400"></span>
                  <span>3 DAYS — Primary Operational Window</span>
                </div>
                <div className="text-xs text-slate-400 mt-1">
                  {opportunities.filter((o) => o.horizon_window === '3d').length} active opportunities
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-extrabold text-white fin-number">
                  {formatINR(horizon3dAmount, true)}
                </div>
                <div className="text-[10px] text-emerald-400 font-semibold">Highest natural recovery</div>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-900/80 border border-sky-500/30 flex items-center justify-between">
              <div>
                <div className="text-xs font-bold text-sky-400 flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-sky-400"></span>
                  <span>7 DAYS — Secondary Operational Window</span>
                </div>
                <div className="text-xs text-slate-400 mt-1">
                  {opportunities.filter((o) => o.horizon_window === '7d').length} active opportunities
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-extrabold text-white fin-number">
                  {formatINR(horizon7dAmount, true)}
                </div>
                <div className="text-[10px] text-sky-400 font-semibold">Intervention required</div>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-900/80 border border-amber-500/30 flex items-center justify-between">
              <div>
                <div className="text-xs font-bold text-amber-400 flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-amber-400"></span>
                  <span>30 DAYS — Macro Horizon Window</span>
                </div>
                <div className="text-xs text-slate-400 mt-1">
                  {opportunities.filter((o) => o.horizon_window === '30d').length} active opportunities
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-extrabold text-white fin-number">
                  {formatINR(horizon30dAmount, true)}
                </div>
                <div className="text-[10px] text-amber-400 font-semibold">Escalation threshold</div>
              </div>
            </div>
          </div>
        </div>

        {/* ANALYTICAL TRAJECTORY CHART */}
        <div className="spatial-card p-5 rounded-xl space-y-4 lg:col-span-2">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                Simulated Recovery Trajectory
              </h3>
              <p className="text-[11px] text-slate-400">
                Natural Baseline P(R | X, A=0) vs RecoverAI Bounded Policy Execution
              </p>
            </div>
            <span className="prov-badge prov-simulated">Simulated Trajectory</span>
          </div>

          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trajectoryData}>
                <defs>
                  <linearGradient id="colorRecoverAI" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorNatural" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#64748b" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#64748b" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="day" stroke="#475569" fontSize={10} tickLine={false} />
                <YAxis stroke="#475569" fontSize={10} tickFormatter={(val) => `${val}%`} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  formatter={(val: any) => [`${val}%`, '']}
                />
                <Area type="monotone" dataKey="RecoverAI" stroke="#6366f1" strokeWidth={2} fillOpacity={1} fill="url(#colorRecoverAI)" />
                <Area type="monotone" dataKey="Natural" stroke="#64748b" strokeWidth={2} strokeDasharray="4 4" fillOpacity={1} fill="url(#colorNatural)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* QUICK RECOVERY QUEUE — HIGHEST VALUE ACTIVE OPPORTUNITIES */}
      <div className="spatial-card p-5 rounded-xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Priority Recovery Queue
            </h3>
            <p className="text-[11px] text-slate-400">
              Highest monetary exposure opportunities requiring action selection
            </p>
          </div>
          <button
            onClick={() => onNavigateTab('OPPORTUNITIES')}
            className="text-xs text-sky-400 hover:text-sky-300 font-semibold flex items-center gap-1"
          >
            <span>View All Queue</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                <th className="py-2.5 px-3">Opportunity</th>
                <th className="py-2.5 px-3">Customer</th>
                <th className="py-2.5 px-3">Amount</th>
                <th className="py-2.5 px-3">Days Overdue</th>
                <th className="py-2.5 px-3">Natural P(R)</th>
                <th className="py-2.5 px-3">Recommended Action</th>
                <th className="py-2.5 px-3">Expected EV</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {opportunities.slice(0, 5).map((opp) => (
                <tr key={opp.opportunity_id} className="hover:bg-slate-800/40 transition">
                  <td className="py-3 px-3 font-mono font-medium text-sky-400">
                    {opp.opportunity_id}
                  </td>
                  <td className="py-3 px-3 font-medium text-slate-300">
                    {opp.customer_id}
                  </td>
                  <td className="py-3 px-3 font-bold text-white fin-number">
                    {formatINR(opp.amount)}
                  </td>
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                      opp.days_overdue <= 3
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : opp.days_overdue <= 7
                        ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {opp.days_overdue}d ({opp.horizon_window})
                    </span>
                  </td>
                  <td className="py-3 px-3 fin-number text-slate-300">
                    {formatPercent(opp.natural_probability * 100)}
                  </td>
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                      opp.recommended_action === 'RETRY'
                        ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                        : opp.recommended_action === 'REMINDER'
                        ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20'
                        : opp.recommended_action === 'ESCALATE'
                        ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
                        : 'bg-slate-800 text-slate-400'
                    }`}>
                      {opp.recommended_action}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-semibold text-emerald-400 fin-number">
                    +{formatINR(opp.expected_incremental_revenue)}
                  </td>
                  <td className="py-3 px-3 text-right">
                    <button
                      onClick={() => onSelectOpportunity(opp)}
                      className="px-3 py-1 rounded bg-sky-500/10 hover:bg-sky-500/20 text-sky-300 font-semibold text-xs border border-sky-500/30 transition flex items-center gap-1 ml-auto"
                    >
                      <span>Inspect Trace</span>
                      <ArrowRight className="h-3 w-3" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
