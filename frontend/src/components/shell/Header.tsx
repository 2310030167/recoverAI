import React, { useState, useEffect } from 'react';
import { Shield, RefreshCw, Cpu, CheckCircle2, Activity } from 'lucide-react';
import { api } from '../../lib/api';

interface HeaderProps {
  onResetProvider: () => void;
  isResetting: boolean;
}

export const Header: React.FC<HeaderProps> = ({ onResetProvider, isResetting }) => {
  const [latencyMs, setLatencyMs] = useState<number | null>(null);
  const [isHealthy, setIsHealthy] = useState<boolean>(true);

  useEffect(() => {
    measureLatency();
    const interval = setInterval(measureLatency, 10000);
    return () => clearInterval(interval);
  }, []);

  const measureLatency = async () => {
    const t0 = performance.now();
    try {
      await api.checkHealth();
      const t1 = performance.now();
      setLatencyMs(Math.round(t1 - t0));
      setIsHealthy(true);
    } catch {
      setIsHealthy(false);
      setLatencyMs(null);
    }
  };

  return (
    <header className="h-16 border-b border-slate-800/80 bg-[#0f172a]/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40">
      <div className="flex items-center gap-3">
        <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
          <Cpu className="h-5 w-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-bold text-slate-100 tracking-tight">RecoverAI</h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20">
              BUILDATHON TRACK 03
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-medium">AI Revenue Recovery Command Center</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Environment Indicator */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-semibold">
          <span className="h-2 w-2 rounded-full bg-amber-400 animate-pulse"></span>
          <span>TEST MODE — Zero Financial Risk</span>
        </div>

        {/* Real Measured API Health & Latency */}
        <div className="flex items-center gap-2 text-xs text-emerald-400 font-mono font-medium bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-md">
          <CheckCircle2 className="h-3.5 w-3.5" />
          <span>API LIVE</span>
          {latencyMs !== null && (
            <span className="text-[11px] text-slate-400 flex items-center gap-1 border-l border-emerald-500/30 pl-2">
              <Activity className="h-3 w-3 text-sky-400" />
              <span>{latencyMs}ms</span>
            </span>
          )}
        </div>

        {/* Reset Provider Button */}
        <button
          onClick={onResetProvider}
          disabled={isResetting}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-medium border border-slate-700 transition disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isResetting ? 'animate-spin' : ''}`} />
          <span>Reset Test Provider</span>
        </button>
      </div>
    </header>
  );
};
