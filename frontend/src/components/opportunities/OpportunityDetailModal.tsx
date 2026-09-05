import React, { useState } from 'react';
import { X, Play, ShieldAlert, CheckCircle2, AlertTriangle, ArrowRight, ShieldCheck, RefreshCw } from 'lucide-react';
import { formatINR, formatPercent } from '../../lib/utils';
import { RecoveryOpportunity, ActionType } from '../../lib/types';

interface OpportunityDetailModalProps {
  opportunity: RecoveryOpportunity | null;
  onClose: () => void;
  onExecute: (action: ActionType) => void;
  onSyncPayment?: (opportunityId: string) => Promise<void> | void;
  isExecuting: boolean;
}

export const OpportunityDetailModal: React.FC<OpportunityDetailModalProps> = ({
  opportunity,
  onClose,
  onExecute,
  onSyncPayment,
  isExecuting
}) => {
  const [executionStage, setExecutionStage] = useState<'REVIEW' | 'VALIDATING' | 'EXECUTED'>('REVIEW');
  const [isSyncing, setIsSyncing] = useState<boolean>(false);

  if (!opportunity) return null;

  const actions: ActionType[] = ['NO_ACTION', 'REMINDER', 'RETRY', 'ESCALATE'];

  const handleTriggerExecution = async (action: ActionType) => {
    setExecutionStage('VALIDATING');
    await onExecute(action);
    setExecutionStage('EXECUTED');
  };

  const handleSyncPayment = async () => {
    if (!onSyncPayment || !opportunity) return;
    setIsSyncing(true);
    try {
      await onSyncPayment(opportunity.opportunity_id);
    } catch (err) {
      console.error('Error in handleSyncPayment:', err);
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-md flex items-center justify-center p-4">
      <div className="spatial-card w-full max-w-3xl rounded-2xl bg-[#0f172a] border border-slate-700/80 shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
        {/* MODAL HEADER */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-base font-bold text-sky-400">{opportunity.opportunity_id}</span>
              <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/20">
                {opportunity.days_overdue} Days Overdue ({opportunity.horizon_window})
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">Customer ID: {opportunity.customer_id} | Invoice: {opportunity.invoice_number}</p>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* PROGRESS STAGE HEADER */}
        <div className="bg-slate-900/80 px-6 py-3 border-b border-slate-800/80 flex items-center justify-between text-xs font-mono">
          <div className="flex items-center gap-2">
            <span className={`h-2 w-2 rounded-full ${executionStage === 'EXECUTED' ? 'bg-emerald-400' : 'bg-sky-400 animate-pulse'}`}></span>
            <span className="text-slate-300">
              STAGE: {executionStage === 'REVIEW' ? '1. ECONOMIC REVIEW' : executionStage === 'VALIDATING' ? '2. POLICY & PROVIDER EXECUTION' : '3. OUTCOME OBSERVED'}
            </span>
          </div>
          <span className="text-slate-500">TEST MODE SAFEGUARD ACTIVE</span>
        </div>

        {/* MODAL BODY */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {/* HERO AMOUNT & BASELINE */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <div className="text-xs text-slate-400">Invoice Amount Exposure</div>
              <div className="text-2xl font-extrabold text-white fin-number mt-0.5">
                {formatINR(opportunity.amount)}
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <div className="text-xs text-slate-400">Natural P(R | X, A=0) Baseline</div>
              <div className="text-2xl font-bold text-sky-400 fin-number mt-0.5">
                {formatPercent(opportunity.natural_probability * 100)}
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <div className="text-xs text-slate-400">Recommended Action</div>
              <div className="text-2xl font-bold text-emerald-400 mt-0.5">
                {opportunity.recommended_action}
              </div>
            </div>
          </div>

          {/* ACTION COMPARISON MATRIX (NO_ACTION vs REMINDER vs RETRY vs ESCALATE) */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Action Economics & Policy Evaluation Matrix
            </h4>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                    <th className="py-2.5 px-3">Candidate Action</th>
                    <th className="py-2.5 px-3">Assisted P(R)</th>
                    <th className="py-2.5 px-3">Direct Cost</th>
                    <th className="py-2.5 px-3">Expected Incremental EV</th>
                    <th className="py-2.5 px-3">Policy Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {actions.map((act) => {
                    const isSelected = act === opportunity.recommended_action;
                    const cost = act === 'NO_ACTION' ? 0.0 : act === 'REMINDER' ? 0.50 : act === 'RETRY' ? 2.00 : 50.00;
                    const mult = act === 'NO_ACTION' ? 1.0 : act === 'REMINDER' ? 1.20 : act === 'RETRY' ? 1.35 : 1.15;
                    const assistedP = Math.min(1.0, opportunity.natural_probability * mult);
                    const incP = assistedP - opportunity.natural_probability;
                    const ev = opportunity.amount * incP - cost;

                    return (
                      <tr key={act} className={`${isSelected ? 'bg-indigo-500/10 font-medium' : 'hover:bg-slate-800/40'}`}>
                        <td className="py-3 px-3 font-bold text-slate-200 flex items-center gap-1.5">
                          {isSelected && <span className="h-2 w-2 rounded-full bg-indigo-400"></span>}
                          <span>{act}</span>
                        </td>
                        <td className="py-3 px-3 fin-number text-sky-400 font-semibold">
                          {formatPercent(assistedP * 100)}
                        </td>
                        <td className="py-3 px-3 fin-number text-slate-300">
                          {formatINR(cost)}
                        </td>
                        <td className={`py-3 px-3 fin-number font-bold ${ev > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {ev > 0 ? '+' : ''}{formatINR(ev)}
                        </td>
                        <td className="py-3 px-3">
                          <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            ELIGIBLE
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* RECOVERY OUTCOME ANIMATED CARD */}
          {executionStage === 'EXECUTED' && (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center justify-between shadow-lg shadow-emerald-500/10 animate-bounce">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-6 w-6 text-emerald-400 shrink-0" />
                <div>
                  <div className="font-extrabold text-sm text-emerald-200">
                    TEST-MODE RECOVERY OBSERVED: {formatINR(opportunity.amount)}
                  </div>
                  <div className="text-[11px] text-emerald-300/80">
                    Provider call succeeded. Immutable audit event and recovery outcome recorded.
                  </div>
                </div>
              </div>
              <span className="prov-badge prov-safety">TEST_MODE_EXECUTED_RECOVERY</span>
            </div>
          )}

          {/* WARNING & SAFETY ACKNOWLEDGEMENT */}
          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <div className="font-bold">Test Mode Safeguard Active</div>
              <p className="text-[11px] text-amber-300/80 mt-0.5">
                Executing this action will call the backend <code className="mono-code">POST /api/v1/opportunities/{opportunity.opportunity_id}/execute</code> endpoint via <code className="mono-code">RazorpayTestModeProvider</code>. No real money or live notifications will be processed.
              </p>
            </div>
          </div>
        </div>

        {/* MODAL FOOTER */}
        <div className="p-5 border-t border-slate-800 flex items-center justify-between bg-slate-900/60">
          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition"
            >
              Close
            </button>
            {onSyncPayment && (
              <button
                onClick={handleSyncPayment}
                disabled={isSyncing}
                className="px-4 py-2 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-xs font-semibold transition flex items-center gap-1.5 disabled:opacity-50"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${isSyncing ? 'animate-spin' : ''}`} />
                <span>{isSyncing ? 'VERIFYING PAYMENT...' : 'Verify & Sync Payment'}</span>
              </button>
            )}
          </div>

          {opportunity.is_recovered || opportunity.policy_status === 'RECOVERED' || opportunity.recovery_status === 'RECOVERED' ? (
            <button
              disabled
              className="px-5 py-2.5 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-xs font-bold flex items-center gap-2"
            >
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              <span>RECOVERY ALREADY OBSERVED ({formatINR(opportunity.recovered_amount || opportunity.amount)})</span>
            </button>
          ) : (
            <button
              onClick={() => handleTriggerExecution(opportunity.recommended_action)}
              disabled={isExecuting || opportunity.policy_status !== 'ELIGIBLE'}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-sky-500/20 transition disabled:opacity-50 flex items-center gap-2"
            >
              {isExecuting ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4 fill-current" />}
              <span>{isExecuting ? 'Executing Policy & Provider Call...' : `Execute ${opportunity.recommended_action} IN TEST MODE`}</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
