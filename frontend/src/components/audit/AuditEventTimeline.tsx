import React from 'react';
import { History } from 'lucide-react';
import { formatDate } from '../../lib/utils';
import { TimelineEvent, AuditEvent } from '../../lib/types';

interface AuditEventTimelineProps {
  timeline: (TimelineEvent | AuditEvent)[];
}

export const AuditEventTimeline: React.FC<AuditEventTimelineProps> = ({ timeline }) => {
  return (
    <div className="space-y-6">
      <div className="spatial-card p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <History className="h-5 w-5 text-indigo-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">Audit & Provenance Log ({timeline.length})</h2>
          </div>
          <p className="text-xs text-slate-400">
            Live chronological audit log tracing every detection, policy evaluation, test execution, and recovery event.
          </p>
        </div>

        <span className="prov-badge prov-safety">AUDIT TRAIL — LIVE</span>
      </div>

      <div className="spatial-card p-6 rounded-2xl space-y-6">
        {timeline.length === 0 ? (
          <div className="py-12 text-center text-slate-500 text-xs">
            No audit events recorded yet. Execute an action in the opportunities queue to generate live audit records.
          </div>
        ) : (
          <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
            {timeline.map((event: any, idx) => {
              const oppId = event.opportunity_id || (event.metadata && event.metadata.opportunity_id) || '';
              const title = event.title || event.event_type;
              const desc = event.details || event.description || '';

              return (
                <div key={event.id || idx} className="relative space-y-2">
                  <div className="absolute -left-6 top-1 h-3 w-3 rounded-full bg-sky-500 ring-4 ring-slate-900"></div>

                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-sky-400 font-mono">{event.event_type}</span>
                      {oppId && (
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-500/10 text-sky-300 border border-sky-500/20">
                          {oppId}
                        </span>
                      )}
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                        Actor: {event.actor || 'EXECUTION_ENGINE'}
                      </span>
                    </div>
                    <span className="text-xs text-slate-500 font-mono">{formatDate(event.timestamp)}</span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                    <h4 className="text-xs font-bold text-slate-200">{title}</h4>
                    <p className="text-xs text-slate-400">{desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
