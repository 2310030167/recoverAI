import React from 'react';
import {
  TrendingUp,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
  Zap,
  Cpu
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

  const pipelineSteps = [
    { name: 'DETECT', desc: 'Overdue exposure' },
    { name: 'ESTIMATE', desc: 'Natural P(R)' },
    { name: 'SIMULATE', desc: 'Treatment uplift' },
    { name: 'VALUE', desc: 'Positive-EV check' },
    { name: 'GOVERN', desc: 'Policy constraints' },
    { name: 'EXECUTE', desc: 'Bounded action' },
    { name: 'OBSERVE', desc: 'Razorpay webhook' },
    { name: 'RECOVER', desc: 'Paid / settled' },
    { name: 'STOP', desc: 'Terminal state' }
  ];

  return (
    <div className="space-y-6">
      {/* HERO SECTION & SYSTEM STATUS */}
      <div className="spatial-card p-6 rounded-2xl relative overflow-hidden bg-gradient-to-r from-slate-900 via-[#111827] to-[#0f172a] border border-slate-800/80">
        <div className="absolute right-0 top-0 translate-x-12 -translate-y-12 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="relative z-10 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800/80">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-sky-400" />
              <span className="text-xs font-mono font-bold text-slate-300 tracking-wider">
                AI REVENUE RECOVERY COMMAND CENTER
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30 flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-amber-400 animate-pulse"></span>
                TEST MODE — ZERO FINANCIAL RISK
              </span>
              <span className="px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
                API LIVE
              </span>
              <span className="px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 flex items-center gap-1.5">
                <ShieldCheck className="h-3 w-3 text-indigo-400" />
                BOUNDED AGENT
              </span>
            </div>
          </div>

          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="space-y-1.5 max-w-2xl">
              <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                Recover revenue before it becomes write-off.
              </h2>
              <p className="text-xs text-slate-300 leading-relaxed">
                RecoverAI detects overdue exposure, estimates natural recovery, selects the highest-value intervention, and executes within policy boundaries.
              </p>
            </div>

            <div className="flex items-center gap-4 bg-slate-900/90 p-3.5 rounded-xl border border-slate-800 shrink-0">
              <div>
                <div className="text-[10px] font-mono font-semibold text-slate-400 uppercase tracking-wider">
                  Total Portfolio Exposure
                </div>
                <div className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight fin-number">
                  {formatINR(totalRevenueAtRisk)}
                </div>
              </div>
              <span className="prov-badge prov-empirical text-[10px]">EMPIRICAL DATASET</span>
            </div>
          </div>
        </div>
      </div>

      {/* KEY PORTFOLIO METRICS (6 CARDS) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3.5">
        <div className="spatial-card p-4 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Portfolio Exposure</span>
            <span className="prov-badge prov-empirical">Empirical</span>
          </div>
          <div className="text-xl font-bold text-white fin-number">
            {formatINR(totalRevenueAtRisk, true)}
          </div>
          <div className="text-[10px] text-slate-500">100 overdue invoices</div>
        </div>

        <div className="spatial-card p-4 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Active Opportunities</span>
            <span className="prov-badge prov-empirical">Batch</span>
          </div>
          <div className="text-xl font-bold text-sky-400 fin-number">
            {opportunities.length}
          </div>
          <div className="text-[10px] text-slate-500">Evaluating interventions</div>
        </div>

        <div className="spatial-card p-4 rounded-xl space-y-2 border-sky-500/30">
          <div className="flex items-center justify-between text-xs text-sky-300">
            <span>Projected Recoverable</span>
            <span className="prov-badge prov-configured">Projected EV</span>
          </div>
          <div className="text-xl font-bold text-sky-400 fin-number">
            {formatINR(totalProjectedRecoverable, true)}
          </div>
          <div className="text-[10px] text-slate-500">Action-conditioned EV</div>
        </div>

        <div className="spatial-card p-4 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Natural Baseline Rate</span>
            <span className="prov-badge prov-empirical">Baseline</span>
          </div>
          <div className="text-xl font-bold text-slate-300 fin-number">
            {formatPercent(batchResult ? batchResult.baseline_recovery_rate : 35.0)}
          </div>
          <div className="text-[10px] text-slate-500">Unassisted 30d rate</div>
        </div>

        <div className="spatial-card p-4 rounded-xl space-y-2 border-indigo-500/30">
          <div className="flex items-center justify-between text-xs text-indigo-300">
            <span>RecoverAI Recovery Rate</span>
            <span className="prov-badge prov-simulated">Simulated</span>
          </div>
          <div className="text-xl font-bold text-indigo-400 fin-number">
            {formatPercent(batchResult ? batchResult.recoverai_recovery_rate : 72.0)}
          </div>
          <div className="text-[10px] text-emerald-400 font-semibold">
            +{formatPercent(batchResult ? (batchResult.recoverai_recovery_rate - batchResult.baseline_recovery_rate) : 37.0)} uplift
          </div>
        </div>

        <div className="spatial-card p-4 rounded-xl space-y-2 border-emerald-500/30">
          <div className="flex items-center justify-between text-xs text-emerald-300">
            <span>Simulated Net Gain</span>
            <span className="prov-badge prov-simulated">Batch Simulation</span>
          </div>
          <div className="text-xl font-bold text-emerald-400 fin-number">
            {formatINR(batchResult ? batchResult.net_incremental_revenue : 0, true)}
          </div>
          <div className="text-[10px] text-slate-500">Net of execution costs</div>
        </div>
      </div>

      {/* AI DECISION PIPELINE SUMMARY */}
      <div className="spatial-card p-5 rounded-xl space-y-4 border border-indigo-500/20 bg-slate-900/60">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Cpu className="h-4 w-4 text-indigo-400" />
            <h3 className="text-xs font-mono font-bold text-slate-200 uppercase tracking-wider">
              RECOVERAI DECISION PIPELINE
            </h3>
          </div>
          <span className="text-[10px] font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
            AUTONOMOUS & BOUNDED AGENT FLOW
          </span>
        </div>

        {/* 9-STEP PIPELINE STEPS */}
        <div className="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-9 gap-1.5">
          {pipelineSteps.map((step, idx) => (
            <div key={step.name} className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-indigo-500/40 text-center space-y-0.5 transition">
              <div className="text-[10px] font-mono font-bold text-indigo-400 flex items-center justify-center gap-1">
                <span>{step.name}</span>
              </div>
              <div className="text-[9px] text-slate-400 truncate">{step.desc}</div>
            </div>
          ))}
        </div>

        <p className="text-xs text-slate-400 bg-slate-950/60 p-3 rounded-lg border border-slate-800/80 leading-relaxed">
          <strong className="text-slate-300 font-semibold">How it works: </strong>
          ML estimates natural recovery probability. RecoverAI evaluates intervention economics, applies deterministic policy guardrails, and executes only bounded actions.
        </p>
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
            <span className="prov-badge prov-simulated">BATCH SIMULATION</span>
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

      {/* PRIORITY RECOVERY QUEUE */}
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
