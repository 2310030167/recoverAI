import React, { useState } from 'react';
import { Layers, Info, Filter, ArrowRight, Eye, List, Grid, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';
import { formatINR, formatPercent } from '../../lib/utils';
import { RecoveryOpportunity } from '../../lib/types';

interface SpatialRecoveryUniverseProps {
  opportunities: RecoveryOpportunity[];
  onSelectOpportunity: (opp: RecoveryOpportunity) => void;
}

export const SpatialRecoveryUniverse: React.FC<SpatialRecoveryUniverseProps> = ({
  opportunities,
  onSelectOpportunity
}) => {
  const [hoveredOpp, setHoveredOpp] = useState<RecoveryOpportunity | null>(null);
  const [selectedOppId, setSelectedOppId] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'SPATIAL' | 'ACCESSIBLE_LIST'>('SPATIAL');
  const [zoomScale, setZoomScale] = useState<number>(1.0);

  const getActionColor = (action: string) => {
    switch (action) {
      case 'RETRY':
        return '#818cf8'; // Indigo
      case 'REMINDER':
        return '#38bdf8'; // Sky
      case 'ESCALATE':
        return '#c084fc'; // Purple
      default:
        return '#94a3b8'; // Slate
    }
  };

  const handleNodeClick = (opp: RecoveryOpportunity) => {
    setSelectedOppId(opp.opportunity_id);
    onSelectOpportunity(opp);
  };

  return (
    <div className="space-y-6">
      {/* HEADER & TOGGLE */}
      <div className="spatial-card p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Layers className="h-5 w-5 text-indigo-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">Spatial Recovery Universe (Map of Money at Risk)</h2>
            <span className="prov-badge prov-empirical">Empirical Opportunity Population</span>
          </div>
          <p className="text-xs text-slate-400">
            Y-Axis: Invoice Amount Exposure | X-Axis: Natural Baseline Settlement P(R) | Node Size: Exposure
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* ZOOM CONTROLS */}
          {viewMode === 'SPATIAL' && (
            <div className="flex items-center gap-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800 text-slate-400">
              <button
                onClick={() => setZoomScale((prev) => Math.min(1.5, prev + 0.15))}
                className="p-1.5 hover:text-white transition"
                title="Zoom In"
              >
                <ZoomIn className="h-3.5 w-3.5" />
              </button>
              <button
                onClick={() => setZoomScale((prev) => Math.max(0.7, prev - 0.15))}
                className="p-1.5 hover:text-white transition"
                title="Zoom Out"
              >
                <ZoomOut className="h-3.5 w-3.5" />
              </button>
              <button
                onClick={() => setZoomScale(1.0)}
                className="p-1.5 hover:text-white transition"
                title="Reset Zoom"
              >
                <RotateCcw className="h-3.5 w-3.5" />
              </button>
            </div>
          )}

          {/* VIEW MODE TOGGLE */}
          <div className="flex items-center gap-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => setViewMode('SPATIAL')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                viewMode === 'SPATIAL'
                  ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Grid className="h-3.5 w-3.5" />
              <span>Map of Money</span>
            </button>
            <button
              onClick={() => setViewMode('ACCESSIBLE_LIST')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                viewMode === 'ACCESSIBLE_LIST'
                  ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <List className="h-3.5 w-3.5" />
              <span>Accessible Table</span>
            </button>
          </div>
        </div>
      </div>

      {/* VIEW MODE: SPATIAL CANVAS */}
      {viewMode === 'SPATIAL' ? (
        <div className="spatial-card p-6 rounded-2xl relative h-[560px] border border-slate-800 bg-[#0d1322] overflow-hidden">
          {/* SVG AXES, COORDINATE GRID & RISK ZONE GUIDES */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            {/* Horizontal Grid Lines */}
            <line x1="0" y1="25%" x2="100%" y2="25%" stroke="#334155" strokeDasharray="4 4" opacity="0.4" />
            <line x1="0" y1="50%" x2="100%" y2="50%" stroke="#475569" strokeDasharray="6 6" opacity="0.6" />
            <line x1="0" y1="75%" x2="100%" y2="75%" stroke="#334155" strokeDasharray="4 4" opacity="0.4" />

            {/* Vertical Grid Lines */}
            <line x1="25%" y1="0" x2="25%" y2="100%" stroke="#334155" strokeDasharray="4 4" opacity="0.4" />
            <line x1="50%" y1="0" x2="50%" y2="100%" stroke="#475569" strokeDasharray="6 6" opacity="0.6" />
            <line x1="75%" y1="0" x2="75%" y2="100%" stroke="#334155" strokeDasharray="4 4" opacity="0.4" />
          </svg>

          {/* RISK QUADRANT WATERMARKS */}
          <div className="absolute inset-0 grid grid-cols-2 grid-rows-2 pointer-events-none p-6 text-[10px] font-mono font-bold tracking-wider opacity-30">
            <div className="text-rose-400">CRITICAL RISK ZONE (HIGH EXPOSURE / LOW P(R))</div>
            <div className="text-amber-400 text-right">HIGH VALUE ZONE (HIGH EXPOSURE / HIGH P(R))</div>
            <div className="text-sky-400 flex items-end">MONITORING ZONE (LOW EXPOSURE / LOW P(R))</div>
            <div className="text-emerald-400 flex items-end justify-end">STABLE ZONE (LOW EXPOSURE / HIGH P(R))</div>
          </div>

          {/* AXIS LABELS */}
          <div className="absolute left-3 top-1/2 -translate-y-1/2 -rotate-90 text-[10px] font-mono font-bold text-slate-500 tracking-widest pointer-events-none">
            INVOICE EXPOSURE AMOUNT (HIGH → LOW)
          </div>
          <div className="absolute bottom-2 left-1/2 -translate-x-1/2 text-[10px] font-mono font-bold text-slate-500 tracking-widest pointer-events-none">
            NATURAL RECOVERY BASELINE P(R) (0% → 100%)
          </div>

          {/* SPATIAL POPULATION NODES MAPPED TO ACTUAL DATA */}
          <div
            className="absolute inset-12 transition-transform duration-300"
            style={{ transform: `scale(${zoomScale})` }}
          >
            {opportunities.map((opp) => {
              const posX = Math.min(92, Math.max(8, opp.natural_probability * 84 + 8));
              const posY = Math.min(90, Math.max(10, (1 - opp.amount / 300000) * 80 + 10));
              const nodeRadius = Math.min(50, Math.max(18, Math.sqrt(opp.amount) / 14));
              const color = getActionColor(opp.recommended_action);
              const isSelected = selectedOppId === opp.opportunity_id;
              const isCritical = opp.amount > 100000 && opp.natural_probability < 0.35;

              return (
                <div
                  key={opp.opportunity_id}
                  onClick={() => handleNodeClick(opp)}
                  onMouseEnter={() => setHoveredOpp(opp)}
                  onMouseLeave={() => setHoveredOpp(null)}
                  style={{
                    left: `${posX}%`,
                    top: `${posY}%`,
                    width: `${nodeRadius}px`,
                    height: `${nodeRadius}px`,
                    backgroundColor: `${color}25`,
                    borderColor: isSelected ? '#ffffff' : color,
                    boxShadow: isSelected
                      ? `0 0 25px 4px #ffffff, 0 0 15px ${color}`
                      : isCritical
                      ? `0 0 20px 2px #f43f5e`
                      : `0 0 12px -2px ${color}60`
                  }}
                  className={`absolute rounded-full border-2 transform -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-200 hover:scale-125 hover:z-40 flex items-center justify-center group ${
                    isCritical ? 'ring-2 ring-rose-500/50 animate-pulse' : ''
                  }`}
                >
                  <span className="text-[9px] font-mono font-extrabold text-white opacity-90 group-hover:opacity-100">
                    {opp.opportunity_id.slice(-3)}
                  </span>
                </div>
              );
            })}
          </div>

          {/* HOVER TOOLTIP FLOATING CARD */}
          {hoveredOpp && (
            <div className="absolute bottom-6 right-6 z-50 p-4 rounded-xl spatial-card bg-slate-900/95 border border-indigo-500/50 w-80 space-y-2.5 shadow-2xl pointer-events-none backdrop-blur-md">
              <div className="flex items-center justify-between text-xs">
                <span className="font-mono font-bold text-sky-400">{hoveredOpp.opportunity_id}</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/20">
                  {hoveredOpp.days_overdue}d overdue ({hoveredOpp.horizon_window})
                </span>
              </div>

              <div>
                <div className="text-[10px] text-slate-400">Invoice Amount Exposure</div>
                <div className="text-xl font-bold text-white fin-number">
                  {formatINR(hoveredOpp.amount)}
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800 grid grid-cols-2 gap-2 text-xs">
                <div>
                  <div className="text-[10px] text-slate-500">Natural Baseline</div>
                  <div className="font-bold text-sky-300">{formatPercent(hoveredOpp.natural_probability * 100)}</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-500">Expected EV Delta E</div>
                  <div className="font-bold text-emerald-400">+{formatINR(hoveredOpp.expected_incremental_revenue)}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* ACCESSIBLE LIST FALLBACK */
        <div className="spatial-card p-5 rounded-2xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                  <th className="py-3 px-3">Opportunity</th>
                  <th className="py-3 px-3">Customer</th>
                  <th className="py-3 px-3">Amount Exposure</th>
                  <th className="py-3 px-3">Overdue Age</th>
                  <th className="py-3 px-3">Horizon</th>
                  <th className="py-3 px-3">Natural P(R)</th>
                  <th className="py-3 px-3">Recommended Action</th>
                  <th className="py-3 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {opportunities.map((opp) => (
                  <tr key={opp.opportunity_id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-3 font-mono font-bold text-sky-400">{opp.opportunity_id}</td>
                    <td className="py-3 px-3 text-slate-300">{opp.customer_id}</td>
                    <td className="py-3 px-3 font-bold text-white fin-number">{formatINR(opp.amount)}</td>
                    <td className="py-3 px-3">{opp.days_overdue}d</td>
                    <td className="py-3 px-3">{opp.horizon_window}</td>
                    <td className="py-3 px-3 fin-number text-slate-300">{formatPercent(opp.natural_probability * 100)}</td>
                    <td className="py-3 px-3 font-bold text-indigo-400">{opp.recommended_action}</td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => handleNodeClick(opp)}
                        className="px-3 py-1 rounded bg-sky-500/10 hover:bg-sky-500/20 text-sky-300 font-semibold text-xs border border-sky-500/30 transition ml-auto"
                      >
                        Inspect Trace
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
