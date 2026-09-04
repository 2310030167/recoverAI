import React, { useState, useEffect } from 'react';
import { Header } from './components/shell/Header';
import { Sidebar, NavTab } from './components/shell/Sidebar';
import { OverviewDashboard } from './components/overview/OverviewDashboard';
import { RecoveryHorizonVisualizer } from './components/horizon/RecoveryHorizonVisualizer';
import { SpatialRecoveryUniverse } from './components/universe/SpatialRecoveryUniverse';
import { DecisionTraceVisualizer } from './components/decision_trace/DecisionTraceVisualizer';
import { EconomicWhatIfSimulator } from './components/economic_what_if/EconomicWhatIfSimulator';
import { OpportunityQueueTable } from './components/opportunities/OpportunityQueueTable';
import { OpportunityDetailModal } from './components/opportunities/OpportunityDetailModal';
import { ExecutionLogTable } from './components/executions/ExecutionLogTable';
import { AuditEventTimeline } from './components/audit/AuditEventTimeline';
import { AnalyticsDashboard } from './components/analytics/AnalyticsDashboard';

import {
  RecoveryOpportunity,
  DecisionExplanation,
  BatchSimulationResult,
  ExecutionRecord,
  TimelineEvent,
  ActionType
} from './lib/types';
import { api } from './lib/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<NavTab>('OVERVIEW');
  const [opportunities, setOpportunities] = useState<RecoveryOpportunity[]>([]);
  const [selectedOpp, setSelectedOpp] = useState<RecoveryOpportunity | null>(null);
  const [explanation, setExplanation] = useState<DecisionExplanation | null>(null);
  const [batchResult, setBatchResult] = useState<BatchSimulationResult | null>(null);
  const [executions, setExecutions] = useState<ExecutionRecord[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [isResetting, setIsResetting] = useState<boolean>(false);
  const [modalOpen, setModalOpen] = useState<boolean>(false);

  useEffect(() => {
    loadBackendData();
  }, []);

  const loadBackendData = async () => {
    setIsLoading(true);
    try {
      const opps = await api.getOpportunities(100, 42);
      setOpportunities(opps);
      if (opps.length > 0) {
        setSelectedOpp(opps[0]);
      }

      const batch = await api.runBatchSimulation(100, 42);
      setBatchResult(batch);
    } catch (err) {
      console.error('Failed to load backend data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectOpportunity = async (opp: RecoveryOpportunity) => {
    setSelectedOpp(opp);
    setModalOpen(true);
    try {
      const exp = await api.evaluateOpportunity(opp.opportunity_id, {
        amount: opp.amount,
        natural_probability: opp.natural_probability,
        is_disputed: opp.is_disputed,
        is_opted_out: opp.is_opted_out,
        days_overdue: opp.days_overdue,
      });
      setExplanation(exp);

      const tEvents = await api.getTimeline(opp.opportunity_id);
      setTimeline(tEvents);
    } catch (err) {
      console.error('Error fetching decision explanation:', err);
    }
  };

  const handleExecuteAction = async (action: ActionType) => {
    if (!selectedOpp) return;
    setIsExecuting(true);
    try {
      const record = await api.executeAction(selectedOpp.opportunity_id, {
        action,
        amount: selectedOpp.amount,
        natural_probability: selectedOpp.natural_probability,
        customer_id: selectedOpp.customer_id,
        is_disputed: selectedOpp.is_disputed,
        is_opted_out: selectedOpp.is_opted_out,
      });

      setExecutions((prev) => [record, ...prev]);
      const updatedTimeline = await api.getTimeline(selectedOpp.opportunity_id);
      setTimeline(updatedTimeline);

      if (record.metadata?.payment_link_url) {
        const linkUrl = record.metadata.payment_link_url;
        alert(`Razorpay Payment Link Created!\n\nStatus: Payment Link Created (Awaiting Customer Payment)\nLink: ${linkUrl}\n\nClick OK to open the test payment link in a new tab.\n\nAfter completing payment in Razorpay, click 'Sync Payment Status' to observe recovery settlement.`);
        window.open(linkUrl, '_blank', 'noopener,noreferrer');
      } else {
        alert(`Test Execution Completed: Status = ${record.execution_status}`);
      }
      setModalOpen(false);
    } catch (err: any) {
      alert(`Execution Failed: ${err.message || err}`);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleSyncPaymentStatus = async (oppId: string) => {
    try {
      const res = await api.syncPaymentStatus(oppId);
      if (res.success && res.is_recovered) {
        alert(`Razorpay Payment Verified!\n\nStatus: PAID (${res.recovery_status})\nAmount Recovered: ₹${res.recovered_amount.toLocaleString('en-IN')}\n\nRecoverAI has recorded the recovery outcome and updated the timeline & audit log!`);
      } else if (res.success) {
        alert(`Razorpay Payment Status Checked:\n\nStatus: ${res.payment_status} (${res.recovery_status})\nMessage: ${res.message}`);
      } else {
        alert(`Sync Failed: ${res.error_message || res.message}`);
      }
      const updatedTimeline = await api.getTimeline(oppId);
      setTimeline(updatedTimeline);
      const updatedOpps = await api.getOpportunities(100, 42);
      setOpportunities(updatedOpps);
    } catch (err: any) {
      alert(`Payment Sync Failed: ${err.message || err}`);
    }
  };

  const handleResetProvider = async () => {
    setIsResetting(true);
    try {
      await api.resetTestProvider();
      setExecutions([]);
      setTimeline([]);
      alert('Test Mode Provider & Execution Engine state reset successfully.');
    } catch (err) {
      console.error('Error resetting test provider:', err);
    } finally {
      setIsResetting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-[#e2e8f0] flex flex-col font-sans">
      <Header onResetProvider={handleResetProvider} isResetting={isResetting} />

      <div className="flex flex-1">
        <Sidebar
          activeTab={activeTab}
          onTabChange={setActiveTab}
          opportunityCount={opportunities.length}
        />

        <main className="flex-1 p-6 max-w-7xl mx-auto space-y-6">
          {isLoading ? (
            <div className="spatial-card p-12 rounded-2xl text-center space-y-4">
              <div className="inline-block animate-spin h-8 w-8 border-4 border-sky-500 border-t-transparent rounded-full"></div>
              <div className="text-sm font-semibold text-slate-300">
                Loading RecoverAI Backend Data...
              </div>
              <p className="text-xs text-slate-500">Connecting to FastAPI on port 8000</p>
            </div>
          ) : (
            <>
              {activeTab === 'OVERVIEW' && (
                <OverviewDashboard
                  opportunities={opportunities}
                  batchResult={batchResult}
                  onSelectOpportunity={handleSelectOpportunity}
                  onNavigateTab={setActiveTab}
                />
              )}

              {activeTab === 'RECOVERY' && (
                <div className="space-y-6">
                  <RecoveryHorizonVisualizer
                    opportunities={opportunities}
                    onSelectOpportunity={handleSelectOpportunity}
                  />
                  <SpatialRecoveryUniverse
                    opportunities={opportunities}
                    onSelectOpportunity={handleSelectOpportunity}
                  />
                </div>
              )}

              {activeTab === 'OPPORTUNITIES' && (
                <div className="space-y-6">
                  <OpportunityQueueTable
                    opportunities={opportunities}
                    onSelectOpportunity={handleSelectOpportunity}
                  />
                  <DecisionTraceVisualizer
                    explanation={explanation}
                    opportunity={selectedOpp}
                    onExecuteAction={handleExecuteAction}
                    isExecuting={isExecuting}
                  />
                  <EconomicWhatIfSimulator opportunity={selectedOpp} />
                </div>
              )}

              {activeTab === 'EXECUTIONS' && (
                <ExecutionLogTable executions={executions} />
              )}

              {activeTab === 'ANALYTICS' && (
                <AnalyticsDashboard batchResult={batchResult} />
              )}

              {activeTab === 'AUDIT' && (
                <AuditEventTimeline timeline={timeline} />
              )}
            </>
          )}
        </main>
      </div>

      {modalOpen && (
        <OpportunityDetailModal
          opportunity={selectedOpp}
          onClose={() => setModalOpen(false)}
          onExecute={handleExecuteAction}
          onSyncPayment={handleSyncPaymentStatus}
          isExecuting={isExecuting}
        />
      )}
    </div>
  );
};
