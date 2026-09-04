import React from 'react';
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  Play,
  ShieldCheck,
  Zap,
  TrendingUp,
  Clock,
  Layers,
  ArrowRight,
  ChevronRight,
  HelpCircle
} from 'lucide-react';
import { formatINR, formatPercent } from '../../lib/utils';
import { DecisionExplanation, RecoveryOpportunity, ActionType } from '../../lib/types';

interface DecisionTraceVisualizerProps {
  explanation: DecisionExplanation | null;
  opportunity: RecoveryOpportunity | null;
  onExecuteAction: (action: ActionType) => void;
  isExecuting: boolean;
}

export const DecisionTraceVisualizer: React.FC<DecisionTraceVisualizerProps> = ({
  explanation,
  opportunity,
  onExecuteAction,
  isExecuting
}) => {
  if (!opportunity) {
    return (
      <div className="spatial-card p-8 rounded-2xl text-center text-slate-400">
        Select an opportunity from the recovery queue to inspect its complete decision trace.
      </div>
    );
  }

  const steps = [
    {
      step: '01',
      name: 'DETECT',
      title: 'Invoice Exposure',
      description: `Invoice INV_${opportunity.opportunity_id} is ${opportunity.days_overdue} days overdue.`,
      value: formatINR(opportunity.amount),
      badge: 'EMPIRICAL',
      badgeClass: 'prov-empirical',
      status: 'completed',
      details: `Customer: ${opportunity.customer_id}`
    },
    {
      step: '02',
      name: 'ESTIMATE',
      title: 'Natural Baseline P(R)',
      description: 'Censoring-adjusted settlement estimation without action.',
      value: formatPercent(opportunity.natural_probability * 100),
      badge: 'EMPIRICAL',
      badgeClass: 'prov-empirical',
      status: 'completed',
      details: 'Decile historical settlement'
    },
    {
      step: '03',
      name: 'SIMULATE',
      title: 'Action Uplift P(R | A)',
      description: `Action '${opportunity.recommended_action}' projects settlement uplift.`,
      value: formatPercent(opportunity.assisted_probability * 100),
      badge: 'SIMULATION_ASSUMPTION',
      badgeClass: 'prov-simulated',
      status: 'completed',
      details: `Uplift: +${formatPercent((opportunity.assisted_probability - opportunity.natural_probability) * 100)}`
    },
    {
      step: '04',
      name: 'VALUE',
      title: 'Economic Net EV',
      description: 'Delta E = Amount * Delta p - Cost.',
      value: `+${formatINR(opportunity.expected_incremental_revenue)}`,
      badge: 'DERIVED',
      badgeClass: 'prov-derived',
      status: 'completed',
      details: 'Net of intervention cost'
    },
    {
      step: '05',
      name: 'GOVERN',
      title: 'Policy Compliance',
      description: 'Checks cooldowns (24h), retry limits (3), and opt-outs.',
      value: opportunity.policy_status,
      badge: 'CONFIGURED',
      badgeClass: 'prov-configured',
      status: opportunity.policy_status === 'ELIGIBLE' ? 'completed' : 'blocked',
      details: opportunity.policy_status === 'ELIGIBLE' ? 'Policy constraints satisfied' : 'Blocked by business policy'
    },
    {
      step: '06',
      name: 'EXECUTE',
      title: 'Bounded Execution',
      description: 'Execution via RazorpayTestModeProvider.',
      value: 'TEST MODE READY',
      badge: 'SYSTEM_SAFETY',
      badgeClass: 'prov-safety',
      status: 'active',
      details: 'Zero financial risk'
    },
    {
      step: '07',
      name: 'OUTCOME',
      title: 'Recovery Outcome',
      description: 'Records recovery outcome and updates DB state.',
      value: 'PENDING EXECUTION',
      badge: 'SYSTEM_SAFETY',
      badgeClass: 'prov-safety',
      status: 'pending',
      details: 'Awaits provider execution'
    },
    {
      step: '08',
      name: 'CLOSE',
      title: 'Audit Closure',
      description: 'Closes opportunity cycle and records audit event.',
      value: 'TIMELINE OPEN',
      badge: 'SYSTEM_SAFETY',
      badgeClass: 'prov-safety',
      status: 'pending',
      details: 'Immutable audit log'
    }
  ];

  return (
    <div className="space-y-6">
      {/* TRACE HEADER & SUMMARY BOX */}
      <div className="spatial-card p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Layers className="h-5 w-5 text-sky-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">
              8-Step Decision Trace Pipeline: {opportunity.opportunity_id}
            </h2>
            <span className="prov-badge prov-derived">INTERCONNECTED STORYTELLING PIPELINE</span>
          </div>
          <p className="text-xs text-slate-400">
            Transparent decision lineage explaining WHY RecoverAI selected <strong className="text-white font-bold">{opportunity.recommended_action}</strong> for net gain of <strong className="text-emerald-400 font-bold">+{formatINR(opportunity.expected_incremental_revenue)}</strong>.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => onExecuteAction(opportunity.recommended_action)}
            disabled={isExecuting || opportunity.policy_status !== 'ELIGIBLE'}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-sky-500/20 transition disabled:opacity-50 flex items-center gap-2"
          >
            <Play className="h-4 w-4 fill-current" />
            <span>{isExecuting ? 'Executing...' : `Execute ${opportunity.recommended_action} in TEST MODE`}</span>
          </button>
        </div>
      </div>

      {/* WHY RECOVERAI CHOSE ACTION HIGHLIGHT BOX */}
      <div className="p-4 rounded-xl spatial-card bg-indigo-500/10 border border-indigo-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <ShieldCheck className="h-6 w-6 text-indigo-400 shrink-0" />
          <div>
            <div className="text-xs font-bold text-indigo-200">
              WHY RECOVERAI CHOSE {opportunity.recommended_action}:
            </div>
            <div className="text-xs text-slate-300 mt-0.5">
              Natural settlement baseline is {formatPercent(opportunity.natural_probability * 100)}. Action '{opportunity.recommended_action}' raises recovery to {formatPercent(opportunity.assisted_probability * 100)}, yielding a net positive expected incremental gain of +{formatINR(opportunity.expected_incremental_revenue)} net of direct costs. Policy constraints passed cleanly.
            </div>
          </div>
        </div>
        <span className="prov-badge prov-configured shrink-0">POLICY APPROVED</span>
      </div>

      {/* 8-STEP INTERCONNECTED PIPELINE GRID (Horizontal on Desktop, Vertical on Mobile) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 relative">
        {steps.map((s, idx) => {
          const isCompleted = s.status === 'completed';
          const isBlocked = s.status === 'blocked';
          const isActive = s.status === 'active';

          return (
            <div
              key={s.step}
              className={`spatial-card p-4 rounded-xl border relative space-y-3 transition ${
                isCompleted
                  ? 'border-emerald-500/30 bg-emerald-500/5'
                  : isBlocked
                  ? 'border-rose-500/30 bg-rose-500/5'
                  : isActive
                  ? 'border-sky-500/50 bg-sky-500/10 shadow-lg shadow-sky-500/10'
                  : 'border-slate-800 bg-slate-900/60'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold text-slate-400">STEP {s.step}</span>
                <span className={`prov-badge ${s.badgeClass}`}>{s.badge}</span>
              </div>

              <div>
                <div className={`text-xs font-bold font-mono ${
                  isCompleted ? 'text-emerald-400' : isBlocked ? 'text-rose-400' : isActive ? 'text-sky-400' : 'text-slate-500'
                }`}>
                  {s.name}
                </div>
                <h3 className="text-sm font-bold text-white mt-0.5">{s.title}</h3>
                <p className="text-xs text-slate-400 mt-1">{s.description}</p>
              </div>

              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <span className="text-[10px] text-slate-500 font-mono">{s.details}</span>
                <span className={`font-bold fin-number ${
                  isCompleted ? 'text-emerald-400' : isBlocked ? 'text-rose-400' : 'text-sky-300'
                }`}>
                  {s.value}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
