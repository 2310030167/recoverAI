import React from 'react';
import { Zap, CheckCircle2, XCircle, AlertCircle, Clock, RotateCcw } from 'lucide-react';
import { formatINR, formatDate } from '../../lib/utils';
import { ExecutionRecord } from '../../lib/types';

interface ExecutionLogTableProps {
  executions: ExecutionRecord[];
}

export const ExecutionLogTable: React.FC<ExecutionLogTableProps> = ({ executions }) => {
  return (
    <div className="space-y-6">
      <div className="spatial-card p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Zap className="h-5 w-5 text-amber-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">
              Test-Mode Execution Log ({executions.length})
            </h2>
          </div>
          <p className="text-xs text-slate-400">
            Real-time log of test-mode provider execution calls. Idempotency keys prevent duplicate execution.
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-semibold">
          <span>TEST MODE PROVIDER ACTIVE</span>
        </div>
      </div>

      <div className="spatial-card p-5 rounded-2xl">
        {executions.length === 0 ? (
          <div className="py-12 text-center text-slate-500 text-xs">
            No test-mode executions performed yet. Select an opportunity from the queue and click 'Execute in TEST MODE'.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                  <th className="py-3 px-3">Execution ID</th>
                  <th className="py-3 px-3">Opportunity</th>
                  <th className="py-3 px-3">Action</th>
                  <th className="py-3 px-3">Provider</th>
                  <th className="py-3 px-3">Idempotency Key</th>
                  <th className="py-3 px-3">Executed At</th>
                  <th className="py-3 px-3">Cost</th>
                  <th className="py-3 px-3">Status</th>
                  <th className="py-3 px-3">Provider Reference</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {executions.map((exec) => (
                  <tr key={exec.execution_id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-3 font-mono font-bold text-sky-400">
                      {exec.execution_id}
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-300">
                      {exec.opportunity_id}
                    </td>
                    <td className="py-3 px-3 font-bold text-slate-200">
                      {exec.action}
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-400">
                      {exec.provider}
                    </td>
                    <td className="py-3 px-3 font-mono text-[11px] text-slate-400">
                      {exec.idempotency_key}
                    </td>
                    <td className="py-3 px-3 text-slate-400">
                      {formatDate(exec.requested_at)}
                    </td>
                    <td className="py-3 px-3 fin-number text-amber-400 font-semibold">
                      {formatINR(exec.intervention_cost)}
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        exec.execution_status === 'SUCCEEDED'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : exec.execution_status === 'SKIPPED'
                          ? 'bg-slate-800 text-slate-400'
                          : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      }`}>
                        {exec.execution_status}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-mono text-[11px] text-emerald-400">
                      {exec.provider_reference || 'N/A'}
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
};
