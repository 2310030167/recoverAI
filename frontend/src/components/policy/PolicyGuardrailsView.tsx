import React from 'react';
import { ShieldCheck, Lock, AlertTriangle, Scale, Clock, RefreshCw, CheckCircle2, FileText, Ban } from 'lucide-react';
import { PolicyGuardrailsConfig } from '../../lib/types';
import { formatINR } from '../../lib/utils';

interface PolicyGuardrailsViewProps {
  config: PolicyGuardrailsConfig | null;
}

export const PolicyGuardrailsView: React.FC<PolicyGuardrailsViewProps> = ({ config }) => {
  const defaultRules = [
    {
      id: 'RULE_01',
      name: 'Positive Expected Value Required',
      category: 'ECONOMIC_EV',
      description: 'Expected incremental revenue EV = Amount * Delta p - Cost must be strictly > ₹0 for action execution.',
      threshold: '> ₹0.00 EV',
      status: 'ACTIVE_ENFORCED'
    },
    {
      id: 'RULE_02',
      name: 'Customer Opt-Out Protection',
      category: 'COMPLIANCE',
      description: 'Automated recovery communications and retries are immediately blocked if customer has opted out.',
      threshold: 'Opt-Out Flag == True -> BLOCK',
      status: 'ACTIVE_ENFORCED'
    },
    {
      id: 'RULE_03',
      name: 'Disputed Invoice Protection',
      category: 'COMPLIANCE',
      description: 'Automated recovery interventions are strictly blocked for invoices under legal or billing dispute.',
      threshold: 'Dispute Flag == True -> BLOCK',
      status: 'ACTIVE_ENFORCED'
    },
    {
      id: 'RULE_04',
      name: 'Intervention Cooldown Window',
      category: 'OPERATIONAL',
      description: 'Requires minimum hours to elapse between consecutive automated actions on the same opportunity.',
      threshold: `${config?.thresholds?.cooldown_hours ?? 24.0}h Cooldown`,
      status: 'ACTIVE_ENFORCED'
    },
    {
      id: 'RULE_05',
      name: 'Maximum Payment Retry Cap',
      category: 'OPERATIONAL',
      description: 'Strict limit on payment retry attempts per opportunity to prevent customer fatigue and spam.',
      threshold: `${config?.thresholds?.max_retry_attempts ?? 3} Retries Max`,
      status: 'ACTIVE_ENFORCED'
    },
    {
      id: 'RULE_06',
      name: 'Maximum Total Interventions Cap',
      category: 'OPERATIONAL',
      description: 'Hard cap on total cumulative automated interventions allowed across an opportunity lifecycle.',
      threshold: `${config?.thresholds?.max_interventions ?? 5} Interventions Cap`,
      status: 'ACTIVE_ENFORCED'
    },
    {
      id: 'RULE_07',
      name: 'Escalation Criteria',
      category: 'GOVERNANCE',
      description: 'ESCALATE action is permitted only if invoice is overdue >= 14d, amount >= ₹100k, or disputed.',
      threshold: `>= 14d OR >= ₹100,000 OR Disputed`,
      status: 'ACTIVE_ENFORCED'
    },
    {
      id: 'RULE_08',
      name: 'Recovery Stopping Rule',
      category: 'SYSTEM_SAFETY',
      description: 'Once payment status is observed as PAID/RECOVERED, all further automated actions are permanently blocked.',
      threshold: 'Status == RECOVERED -> BLOCK ALL',
      status: 'ACTIVE_ENFORCED'
    },
    {
      id: 'RULE_09',
      name: 'Strict Idempotency Guardrail',
      category: 'SYSTEM_SAFETY',
      description: 'Duplicate execution requests return cached execution record to prevent duplicate payment links.',
      threshold: 'Idempotency Key Check -> REPLAY CACHE',
      status: 'ACTIVE_ENFORCED'
    }
  ];

  const rules = config?.rules && config.rules.length > 0 ? config.rules : defaultRules;

  return (
    <div className="space-y-6">
      {/* HEADER */}
      <div className="spatial-card p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <ShieldCheck className="h-5 w-5 text-emerald-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">AI Autonomy Boundaries & Policy Guardrails</h2>
            <span className="prov-badge prov-configured">CONFIGURED PARAMETERS</span>
          </div>
          <p className="text-xs text-slate-400">
            Deterministic business policy constraints, safety thresholds, and stopping rules governing RecoverAI intervention execution.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 rounded-xl bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 text-xs font-semibold font-mono flex items-center gap-1.5">
            <CheckCircle2 className="h-4 w-4" />
            <span>9 SAFETY RULES ACTIVE</span>
          </span>
        </div>
      </div>

      {/* CONCEPTUAL DISCLAIMER BOX */}
      <div className="p-4 rounded-xl spatial-card bg-slate-900/90 border border-slate-800 flex items-start gap-3">
        <Scale className="h-5 w-5 text-sky-400 shrink-0 mt-0.5" />
        <div className="space-y-1 text-xs">
          <div className="font-bold text-slate-200">AI Autonomy Governance Framework</div>
          <p className="text-slate-400 leading-relaxed">
            These rules represent hard business policy boundaries and deterministic system guardrails enforced by the <code className="text-sky-300">PolicyEngine</code> and <code className="text-sky-300">ActionValidator</code>. They operate independently of ML predictions to guarantee safe, bounded autonomous recovery without financial or compliance risk.
          </p>
        </div>
      </div>

      {/* PARAMETERS CONFIG GRID */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
        <div className="spatial-card p-3 rounded-xl border border-slate-800/80 text-center space-y-1">
          <div className="text-[10px] text-slate-400 font-mono">COOLDOWN</div>
          <div className="text-base font-bold text-sky-400 font-mono">{config?.thresholds?.cooldown_hours ?? 24}h</div>
          <div className="text-[9px] text-slate-500">Min hours between actions</div>
        </div>
        <div className="spatial-card p-3 rounded-xl border border-slate-800/80 text-center space-y-1">
          <div className="text-[10px] text-slate-400 font-mono">RETRY CAP</div>
          <div className="text-base font-bold text-indigo-400 font-mono">{config?.thresholds?.max_retry_attempts ?? 3}</div>
          <div className="text-[9px] text-slate-500">Max payment retries</div>
        </div>
        <div className="spatial-card p-3 rounded-xl border border-slate-800/80 text-center space-y-1">
          <div className="text-[10px] text-slate-400 font-mono">INTERVENTIONS</div>
          <div className="text-base font-bold text-purple-400 font-mono">{config?.thresholds?.max_interventions ?? 5}</div>
          <div className="text-[9px] text-slate-500">Max total interventions</div>
        </div>
        <div className="spatial-card p-3 rounded-xl border border-slate-800/80 text-center space-y-1">
          <div className="text-[10px] text-slate-400 font-mono">ESCALATION THRESHOLD</div>
          <div className="text-base font-bold text-amber-400 font-mono">₹100k</div>
          <div className="text-[9px] text-slate-500">Amount or 14d overdue</div>
        </div>
        <div className="spatial-card p-3 rounded-xl border border-slate-800/80 text-center space-y-1">
          <div className="text-[10px] text-slate-400 font-mono">MIN EV THRESHOLD</div>
          <div className="text-base font-bold text-emerald-400 font-mono">&gt; ₹0</div>
          <div className="text-[9px] text-slate-500">Net positive EV required</div>
        </div>
        <div className="spatial-card p-3 rounded-xl border border-slate-800/80 text-center space-y-1">
          <div className="text-[10px] text-slate-400 font-mono">STOPPING RULE</div>
          <div className="text-base font-bold text-rose-400 font-mono">HARD BLOCK</div>
          <div className="text-[9px] text-slate-500">Blocks action if paid</div>
        </div>
      </div>

      {/* 9 RULES GRID */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {rules.map((rule) => (
          <div key={rule.id} className="spatial-card p-4 rounded-xl border border-slate-800 space-y-3 flex flex-col justify-between">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold text-slate-500">{rule.id}</span>
                <span className={`px-2 py-0.5 rounded text-[9px] font-mono font-bold ${
                  rule.category === 'SYSTEM_SAFETY'
                    ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                    : rule.category === 'COMPLIANCE'
                    ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    : rule.category === 'ECONOMIC_EV'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : 'bg-sky-500/10 text-sky-400 border border-sky-500/20'
                }`}>
                  {rule.category}
                </span>
              </div>
              <h3 className="text-sm font-bold text-white leading-tight">{rule.name}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{rule.description}</p>
            </div>

            <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
              <span className="text-[11px] font-mono font-bold text-sky-300">{rule.threshold}</span>
              <span className="px-2 py-0.5 rounded text-[9px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                {rule.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
