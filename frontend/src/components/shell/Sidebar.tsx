import React from 'react';
import {
  LayoutDashboard,
  Compass,
  Layers,
  ShieldCheck,
  Zap,
  BarChart3,
  History,
  FileText
} from 'lucide-react';

export type NavTab = 'OVERVIEW' | 'RECOVERY' | 'OPPORTUNITIES' | 'POLICY' | 'EXECUTIONS' | 'ANALYTICS' | 'AUDIT';

interface SidebarProps {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  opportunityCount: number;
}

interface NavItem {
  id: NavTab;
  label: string;
  icon: any;
  badge?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange, opportunityCount }) => {
  const navItems: NavItem[] = [
    { id: 'OVERVIEW', label: 'Overview', icon: LayoutDashboard },
    { id: 'RECOVERY', label: 'Recovery Horizon', icon: Compass },
    { id: 'OPPORTUNITIES', label: 'Opportunities', icon: Layers, badge: opportunityCount },
    { id: 'POLICY', label: 'Policy & Guardrails', icon: ShieldCheck },
    { id: 'EXECUTIONS', label: 'Executions', icon: Zap },
    { id: 'ANALYTICS', label: 'Analytics', icon: BarChart3 },
    { id: 'AUDIT', label: 'Audit Log', icon: History },
  ];

  return (
    <aside className="w-64 border-r border-slate-800/80 bg-[#0b0f19] p-4 flex flex-col justify-between h-[calc(100vh-4rem)] sticky top-16">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-500">
          Command Navigation
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold transition ${
                isActive
                  ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Icon className={`h-4 w-4 ${isActive ? 'text-sky-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && item.badge > 0 && (
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono ${
                  isActive ? 'bg-sky-500/20 text-sky-300' : 'bg-slate-800 text-slate-400'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Signature Capabilities Summary Footnote */}
      <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/60 space-y-2">
        <div className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-300">
          <FileText className="h-3.5 w-3.5 text-indigo-400" />
          <span>Proven Provenance</span>
        </div>
        <p className="text-[10px] text-slate-400 leading-relaxed">
          Every decision trace explicitly identifies empirical data, policy parameters, and simulation assumptions.
        </p>
      </div>
    </aside>
  );
};
