import React from 'react';
import { BarChart3, TrendingUp, ShieldCheck, DollarSign, Award, Layers } from 'lucide-react';
import { formatINR, formatPercent } from '../../lib/utils';
import { BatchSimulationResult } from '../../lib/types';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface AnalyticsDashboardProps {
  batchResult: BatchSimulationResult | null;
}

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ batchResult }) => {
  const comparisonData = [
    { name: 'Recovery Rate (%)', Baseline: batchResult ? batchResult.baseline_recovery_rate : 35.0, RecoverAI: batchResult ? batchResult.recoverai_recovery_rate : 72.0 },
    { name: '3D Window (%)', Baseline: 12.0, RecoverAI: batchResult ? batchResult.recovery_rate_3d : 38.0 },
    { name: '7D Window (%)', Baseline: 24.0, RecoverAI: batchResult ? batchResult.recovery_rate_7d : 58.0 },
    { name: '30D Window (%)', Baseline: 35.0, RecoverAI: batchResult ? batchResult.recovery_rate_30d : 72.0 },
  ];

  const actionDistData = [
    { name: 'REMINDER', count: 42, color: '#38bdf8' },
    { name: 'RETRY', count: 35, color: '#818cf8' },
    { name: 'NO_ACTION', count: 15, color: '#64748b' },
    { name: 'ESCALATE', count: 8, color: '#c084fc' },
  ];

  return (
    <div className="space-y-6">
      <div className="spatial-card p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <BarChart3 className="h-5 w-5 text-sky-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">Recovery Performance Analytics</h2>
            <span className="prov-badge prov-simulated">BATCH SIMULATION ANALYTICS</span>
          </div>
          <p className="text-xs text-slate-400">
            Comparative performance analytics contrasting natural settlement baseline against RecoverAI bounded decisioning.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* COMPARATIVE RECOVERY RATE CHART */}
        <div className="spatial-card p-5 rounded-xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Natural Baseline vs RecoverAI Policy Strategy
            </h3>
            <span className="prov-badge prov-simulated">Simulated Uplift</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonData}>
                <XAxis dataKey="name" stroke="#475569" fontSize={11} tickLine={false} />
                <YAxis stroke="#475569" fontSize={11} tickFormatter={(v) => `${v}%`} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  formatter={(val: any) => [`${val}%`, '']}
                />
                <Bar dataKey="Baseline" fill="#64748b" radius={[4, 4, 0, 0]} />
                <Bar dataKey="RecoverAI" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* ACTION DISTRIBUTION CHART */}
        <div className="spatial-card p-5 rounded-xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Action Selection Distribution
            </h3>
            <span className="prov-badge prov-configured">Bounded Strategy</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={actionDistData} layout="vertical">
                <XAxis type="number" stroke="#475569" fontSize={11} tickLine={false} />
                <YAxis dataKey="name" type="category" stroke="#475569" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                  {actionDistData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
