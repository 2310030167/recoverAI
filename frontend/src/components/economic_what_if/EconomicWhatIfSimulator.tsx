import React, { useState } from 'react';
import { Sliders, RefreshCw, TrendingUp, AlertTriangle, HelpCircle, ShieldCheck } from 'lucide-react';
import { formatINR, formatPercent } from '../../lib/utils';
import { RecoveryOpportunity, DecisionExplanation } from '../../lib/types';
import { api } from '../../lib/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface EconomicWhatIfSimulatorProps {
  opportunity: RecoveryOpportunity | null;
}

export const EconomicWhatIfSimulator: React.FC<EconomicWhatIfSimulatorProps> = ({ opportunity }) => {
  const [amount, setAmount] = useState<number>(opportunity ? opportunity.amount : 80000);
  const [naturalProb, setNaturalProb] = useState<number>(opportunity ? opportunity.natural_probability : 0.30);
  const [multiplier, setMultiplier] = useState<number>(1.20);
  const [costOverride, setCostOverride] = useState<number>(0.50);
  const [isEvaluating, setIsEvaluating] = useState<boolean>(false);

  const handleRunWhatIf = async () => {
    if (!opportunity) return;
    setIsEvaluating(true);
    try {
      const customAssisted = Math.min(1.0, naturalProb * multiplier);
      await api.evaluateOpportunity(opportunity.opportunity_id, {
        amount,
        natural_probability: naturalProb,
        custom_action_probs: {
          REMINDER: customAssisted,
          RETRY: Math.min(1.0, naturalProb * 1.35),
          ESCALATE: Math.min(1.0, naturalProb * 1.15),
        }
      });
    } catch (err) {
      console.error('What-If evaluation error:', err);
    } finally {
      setIsEvaluating(false);
    }
  };

  const calculatedAssistedProb = Math.min(1.0, naturalProb * multiplier);
  const calculatedDeltaP = Math.max(0.0, calculatedAssistedProb - naturalProb);
  const grossGain = amount * calculatedDeltaP;
  const naturalValue = amount * naturalProb;
  const grossAssistedValue = amount * calculatedAssistedProb;
  const calculatedEV = grossGain - costOverride;
  const isApproved = calculatedEV > 0;

  const sensitivityData = [
    { name: 'Natural Recovery Baseline', value: naturalValue, color: '#38bdf8' },
    { name: 'Gross Assisted Recovery', value: grossAssistedValue, color: '#818cf8' },
    { name: 'Gross Inc. Revenue Gain', value: grossGain, color: '#34d399' },
    { name: 'Net EV Delta E', value: Math.max(0, calculatedEV), color: isApproved ? '#10b981' : '#f43f5e' }
  ];

  return (
    <div className="space-y-6">
      {/* HEADER */}
      <div className="spatial-card p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Sliders className="h-5 w-5 text-indigo-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">Economic What-If Decision Laboratory</h2>
            <span className="prov-badge prov-simulated">BACKEND SENSITIVITY CALCULATION</span>
          </div>
          <p className="text-xs text-slate-400">
            Stress-test economic expected value equation Delta E = Amount * Delta p - Cost under dynamic sensitivity parameters.
          </p>
        </div>

        <button
          onClick={handleRunWhatIf}
          disabled={isEvaluating}
          className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-500/20 transition disabled:opacity-50 flex items-center gap-2"
        >
          <RefreshCw className={`h-4 w-4 ${isEvaluating ? 'animate-spin' : ''}`} />
          <span>Re-Evaluate Backend Economics</span>
        </button>
      </div>

      {/* CONTROLS & DYNAMIC SENSITIVITY WATERFALL GRAPH GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* SLIDER CONTROLS PANEL */}
        <div className="spatial-card p-5 rounded-xl space-y-5 lg:col-span-2">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Sensitivity Parameter Adjustments
            </h3>
            <span className="prov-badge prov-simulated">SIMULATION_ASSUMPTION</span>
          </div>

          {/* 1. Invoice Revenue Amount Slider */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Invoice Revenue Exposure (Amount)</span>
              <span className="font-bold text-white fin-number">{formatINR(amount)}</span>
            </div>
            <input
              type="range"
              min="1000"
              max="500000"
              step="1000"
              value={amount}
              onChange={(e) => setAmount(Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
            />
          </div>

          {/* 2. Natural Recovery Baseline Probability Slider */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Natural Baseline P(R | X, A=0)</span>
              <span className="font-bold text-sky-400 fin-number">{formatPercent(naturalProb * 100)}</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.95"
              step="0.05"
              value={naturalProb}
              onChange={(e) => setNaturalProb(Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-500"
            />
          </div>

          {/* 3. Action Treatment Multiplier Slider */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400 flex items-center gap-1.5">
                <span>Treatment Uplift Multiplier (A=REMINDER)</span>
                <span className="prov-badge prov-simulated">SIMULATION_ASSUMPTION</span>
              </span>
              <span className="font-bold text-amber-400 fin-number">{multiplier.toFixed(2)}x</span>
            </div>
            <input
              type="range"
              min="1.00"
              max="2.00"
              step="0.05"
              value={multiplier}
              onChange={(e) => setMultiplier(Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
          </div>

          {/* 4. Direct Cost Override Slider */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Intervention Direct Cost Override</span>
              <span className="font-bold text-slate-300 fin-number">{formatINR(costOverride)}</span>
            </div>
            <input
              type="range"
              min="0.00"
              max="100.00"
              step="0.50"
              value={costOverride}
              onChange={(e) => setCostOverride(Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
          </div>
        </div>

        {/* REAL-TIME DYNAMIC EXPECTED VALUE DISPLAY & WATERFALL GRAPH */}
        <div className="spatial-card p-5 rounded-xl space-y-4 border-indigo-500/30 bg-gradient-to-b from-slate-900 via-[#111827] to-[#0f172a]">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-indigo-300 uppercase tracking-wider">
              Economic Result
            </h3>
            <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${
              isApproved ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
            }`}>
              {isApproved ? 'APPROVED' : 'BLOCKED'}
            </span>
          </div>

          <div className="space-y-3 pt-1">
            <div className="h-36 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sensitivityData} layout="vertical">
                  <XAxis type="number" stroke="#475569" fontSize={9} tickLine={false} tickFormatter={(v) => `₹${v}`} />
                  <YAxis dataKey="name" type="category" stroke="#475569" fontSize={9} tickLine={false} width={110} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '6px', fontSize: '10px' }} />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {sensitivityData.map((entry, idx) => (
                      <Cell key={`cell-${idx}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="p-3 rounded-lg bg-slate-900/80 border border-indigo-500/40 space-y-1">
              <div className="text-[10px] text-slate-400">EXPECTED NET RECOVERY (DELTA E)</div>
              <div className={`text-2xl font-extrabold fin-number ${
                calculatedEV > 0 ? 'text-emerald-400' : 'text-rose-400'
              }`}>
                {calculatedEV > 0 ? '+' : ''}{formatINR(calculatedEV)}
              </div>
              <div className="text-[10px] text-slate-400">
                Action Status: <strong className={isApproved ? 'text-emerald-400' : 'text-rose-400'}>{isApproved ? 'ACTION APPROVED' : 'ACTION BLOCKED (EV <= 0)'}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
