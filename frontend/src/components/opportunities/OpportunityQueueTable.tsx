import React, { useState } from 'react';
import { Search, Filter, ArrowRight, Layers } from 'lucide-react';
import { formatINR, formatPercent } from '../../lib/utils';
import { RecoveryOpportunity } from '../../lib/types';

interface OpportunityQueueTableProps {
  opportunities: RecoveryOpportunity[];
  onSelectOpportunity: (opp: RecoveryOpportunity) => void;
}

export const OpportunityQueueTable: React.FC<OpportunityQueueTableProps> = ({
  opportunities,
  onSelectOpportunity
}) => {
  const [search, setSearch] = useState('');
  const [horizonFilter, setHorizonFilter] = useState<string>('ALL');
  const [actionFilter, setActionFilter] = useState<string>('ALL');

  const filtered = opportunities.filter((o) => {
    const matchesSearch =
      o.opportunity_id.toLowerCase().includes(search.toLowerCase()) ||
      o.customer_id.toLowerCase().includes(search.toLowerCase());
    const matchesHorizon = horizonFilter === 'ALL' || o.horizon_window === horizonFilter;
    const matchesAction = actionFilter === 'ALL' || o.recommended_action === actionFilter;

    return matchesSearch && matchesHorizon && matchesAction;
  });

  return (
    <div className="space-y-6">
      {/* HEADER & FILTERS */}
      <div className="spatial-card p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Layers className="h-5 w-5 text-sky-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">Active Recovery Queue ({filtered.length})</h2>
          </div>
          <p className="text-xs text-slate-400">
            Real-time queue of overdue receivables subject to ML natural prediction and bounded economic decisioning.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* SEARCH */}
          <div className="relative">
            <Search className="h-4 w-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search Opp or Customer..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 w-48"
            />
          </div>

          {/* HORIZON FILTER */}
          <select
            value={horizonFilter}
            onChange={(e) => setHorizonFilter(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-sky-500"
          >
            <option value="ALL">All Horizons</option>
            <option value="3d">3d Window</option>
            <option value="7d">7d Window</option>
            <option value="30d">30d Horizon</option>
          </select>

          {/* ACTION FILTER */}
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-sky-500"
          >
            <option value="ALL">All Actions</option>
            <option value="REMINDER">REMINDER</option>
            <option value="RETRY">RETRY</option>
            <option value="ESCALATE">ESCALATE</option>
            <option value="NO_ACTION">NO_ACTION</option>
          </select>
        </div>
      </div>

      {/* TABLE */}
      <div className="spatial-card p-5 rounded-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                <th className="py-3 px-3">Opportunity</th>
                <th className="py-3 px-3">Customer</th>
                <th className="py-3 px-3">Amount</th>
                <th className="py-3 px-3">Overdue</th>
                <th className="py-3 px-3">Natural P(R)</th>
                <th className="py-3 px-3">Assisted P(R)</th>
                <th className="py-3 px-3">Recommended Action</th>
                <th className="py-3 px-3">Expected EV</th>
                <th className="py-3 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filtered.map((opp) => (
                <tr key={opp.opportunity_id} className="hover:bg-slate-800/40 transition">
                  <td className="py-3 px-3 font-mono font-medium text-sky-400">
                    {opp.opportunity_id}
                  </td>
                  <td className="py-3 px-3 text-slate-300 font-medium">
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
                  <td className="py-3 px-3 fin-number text-sky-400 font-semibold">
                    {formatPercent(opp.assisted_probability * 100)}
                  </td>
                  <td className="py-3 px-3">
                    {opp.is_recovered || opp.policy_status === 'RECOVERED' || opp.recovery_status === 'RECOVERED' ? (
                      <span className="px-2 py-0.5 rounded text-[11px] font-extrabold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                        RECOVERED
                      </span>
                    ) : (
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
                    )}
                  </td>
                  <td className="py-3 px-3 font-semibold text-emerald-400 fin-number">
                    +{formatINR(opp.expected_incremental_revenue)}
                  </td>
                  <td className="py-3 px-3 text-right">
                    <button
                      onClick={() => onSelectOpportunity(opp)}
                      className="px-3 py-1 rounded bg-sky-500/10 hover:bg-sky-500/20 text-sky-300 font-semibold text-xs border border-sky-500/30 transition flex items-center gap-1 ml-auto"
                    >
                      <span>Inspect</span>
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
