import React, { useState } from 'react';
import { Compass, Clock, ArrowRight, ShieldCheck, CheckCircle2, ChevronRight, Activity } from 'lucide-react';
import { formatINR, formatPercent } from '../../lib/utils';
import { RecoveryOpportunity } from '../../lib/types';

interface RecoveryHorizonVisualizerProps {
  opportunities: RecoveryOpportunity[];
  onSelectOpportunity: (opp: RecoveryOpportunity) => void;
}

export const RecoveryHorizonVisualizer: React.FC<RecoveryHorizonVisualizerProps> = ({
  opportunities,
  onSelectOpportunity
}) => {
  const [selectedHorizon, setSelectedHorizon] = useState<'ALL' | '3d' | '7d' | '30d'>('ALL');
  const [hoveredOpp, setHoveredOpp] = useState<RecoveryOpportunity | null>(null);

  const windows = [
    {
      id: '3d',
      title: '3 DAYS',
      subtitle: 'PRIMARY ACTION WINDOW',
      color: 'emerald',
      borderColor: 'border-emerald-500/40',
      bgColor: 'bg-emerald-500/10',
      textColor: 'text-emerald-400',
      description: 'Highest natural settlement period. Low-cost gentle reminders effective.'
    },
    {
      id: '7d',
      title: '7 DAYS',
      subtitle: 'SECONDARY INTERVENTION WINDOW',
      color: 'sky',
      borderColor: 'border-sky-500/40',
      bgColor: 'bg-sky-500/10',
      textColor: 'text-sky-400',
      description: 'Payment retry window. Automated smart retries prevent default escalation.'
    },
    {
      id: '30d',
      title: '30 DAYS',
      subtitle: 'MACRO RESOLUTION HORIZON',
      color: 'amber',
      borderColor: 'border-amber-500/40',
      bgColor: 'bg-amber-500/10',
      textColor: 'text-amber-400',
      description: 'High risk window. Escalation rules and high-exposure manual review thresholds.'
    }
  ] as const;

  const filteredOpps = selectedHorizon === 'ALL'
    ? opportunities
    : opportunities.filter((o) => o.horizon_window === selectedHorizon);

  return (
    <div className="space-y-6">
      {/* HEADER SECTION */}
      <div className="spatial-card p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Compass className="h-5 w-5 text-sky-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">Recovery Horizon Model</h2>
            <span className="prov-badge prov-configured">3d / 7d / 30d Horizons</span>
          </div>
          <p className="text-xs text-slate-400">
            Temporal path tracking overdue receivables from due date through primary, secondary, and macro horizons.
          </p>
        </div>

        {/* HORIZON FILTER BUTTONS */}
        <div className="flex items-center gap-2 bg-slate-900/80 p-1.5 rounded-xl border border-slate-800">
          <button
            onClick={() => setSelectedHorizon('ALL')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              selectedHorizon === 'ALL'
                ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            All Windows ({opportunities.length})
          </button>
          {windows.map((w) => {
            const count = opportunities.filter((o) => o.horizon_window === w.id).length;
            return (
              <button
                key={w.id}
                onClick={() => setSelectedHorizon(w.id as any)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                  selectedHorizon === w.id
                    ? `${w.bgColor} ${w.textColor} ${w.borderColor} border`
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {w.title} ({count})
              </button>
            );
          })}
        </div>
      </div>

      {/* TEMPORAL HORIZON PATH VISUALIZER */}
      <div className="spatial-card p-6 rounded-2xl border border-slate-800 space-y-6 relative overflow-hidden bg-gradient-to-r from-[#0d1322] via-[#111827] to-[#0f172a]">
        <div className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
          <span>Temporal Recovery Horizon Progression Path</span>
          <span className="text-sky-400 flex items-center gap-1">
            <Activity className="h-3.5 w-3.5" />
            Active Horizon Progression
          </span>
        </div>

        {/* HORIZONTAL STEP PIPELINE */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 relative">
          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
            <div className="text-[10px] font-mono font-bold text-slate-500">ORIGIN</div>
            <div className="text-sm font-bold text-slate-200">TODAY (Day 0)</div>
            <div className="text-xs text-slate-400">Invoice Due Date Exposure</div>
            <div className="text-xs font-bold text-slate-300 pt-2 border-t border-slate-800 fin-number">
              {formatINR(opportunities.reduce((acc, o) => acc + o.amount, 0), true)}
            </div>
          </div>

          {windows.map((w, idx) => {
            const oppsInW = opportunities.filter((o) => o.horizon_window === w.id);
            const amountInW = oppsInW.reduce((acc, o) => acc + o.amount, 0);

            return (
              <div
                key={w.id}
                onClick={() => setSelectedHorizon(w.id as any)}
                className={`p-4 rounded-xl spatial-card border ${w.borderColor} cursor-pointer space-y-2 relative group hover:scale-[1.02] transition`}
              >
                <div className="flex items-center justify-between">
                  <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${w.bgColor} ${w.textColor}`}>
                    {w.title}
                  </span>
                  <ChevronRight className={`h-4 w-4 ${w.textColor}`} />
                </div>

                <div className="text-sm font-bold text-white">{w.subtitle}</div>
                <div className="text-xs text-slate-400">{w.description}</div>

                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
                  <span className="text-[10px] text-slate-500">{oppsInW.length} Opps</span>
                  <span className={`text-sm font-extrabold fin-number ${w.textColor}`}>
                    {formatINR(amountInW, true)}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* FILTERED HORIZON OPPORTUNITY GRID */}
      <div className="spatial-card p-5 rounded-xl space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
            Opportunities in Horizon View ({filteredOpps.length})
          </h3>
          <span className="text-xs text-slate-400">
            Hover to inspect details | Click to open decision trace modal
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredOpps.map((opp) => (
            <div
              key={opp.opportunity_id}
              onClick={() => onSelectOpportunity(opp)}
              onMouseEnter={() => setHoveredOpp(opp)}
              onMouseLeave={() => setHoveredOpp(null)}
              className="spatial-card p-4 rounded-xl border border-slate-800/80 hover:border-sky-500/40 cursor-pointer space-y-3 transition group relative"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-semibold text-sky-400 group-hover:underline">
                  {opp.opportunity_id}
                </span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                  opp.horizon_window === '3d'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : opp.horizon_window === '7d'
                    ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20'
                    : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                }`}>
                  {opp.days_overdue}d overdue ({opp.horizon_window})
                </span>
              </div>

              <div>
                <div className="text-xs text-slate-400">{opp.customer_id}</div>
                <div className="text-lg font-bold text-white fin-number mt-0.5">
                  {formatINR(opp.amount)}
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-xs">
                <div>
                  <span className="text-slate-500 text-[10px]">Action: </span>
                  <span className="font-bold text-slate-200">{opp.recommended_action}</span>
                </div>
                <div className="text-right">
                  <span className="text-slate-500 text-[10px]">Expected EV: </span>
                  <span className="font-bold text-emerald-400">+{formatINR(opp.expected_incremental_revenue)}</span>
                </div>
              </div>

              {/* HOVER INSPECTION OVERLAY */}
              {hoveredOpp?.opportunity_id === opp.opportunity_id && (
                <div className="absolute inset-0 bg-slate-900/95 rounded-xl p-3 z-30 border border-sky-500/50 flex flex-col justify-between backdrop-blur-md">
                  <div className="flex justify-between text-[11px] font-mono">
                    <span className="text-sky-400 font-bold">{opp.opportunity_id}</span>
                    <span className="text-emerald-400 font-bold">{opp.policy_status}</span>
                  </div>
                  <div className="space-y-1 text-xs">
                    <div className="flex justify-between text-slate-300">
                      <span>Natural P(R):</span>
                      <span className="font-bold text-sky-300">{formatPercent(opp.natural_probability * 100)}</span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>Assisted P(R):</span>
                      <span className="font-bold text-indigo-300">{formatPercent(opp.assisted_probability * 100)}</span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>Net EV Delta E:</span>
                      <span className="font-bold text-emerald-400">+{formatINR(opp.expected_incremental_revenue)}</span>
                    </div>
                  </div>
                  <div className="text-[10px] text-sky-400 font-semibold text-right">
                    Click to open full decision trace →
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
