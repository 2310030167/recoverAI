import {
  RecoveryOpportunity,
  DecisionExplanation,
  BatchSimulationResult,
  ExecutionRecord,
  TimelineEvent,
  ActionType
} from './types';

const API_BASE_URL = ((import.meta as any).env?.VITE_API_BASE_URL as string) || 'http://127.0.0.1:8000/api/v1';

async function fetchJSON<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const res = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(errorData.detail || `API Request Failed (${res.status})`);
    }

    return await res.json();
  } catch (err: any) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // Health
  checkHealth: () => fetchJSON<{ status: string; service: string; version: string }>('/health'),

  // Opportunities
  getOpportunities: (limit: number = 100, seed: number = 42) =>
    fetchJSON<RecoveryOpportunity[]>(`/opportunities?limit=${limit}&seed=${seed}`),

  evaluateOpportunity: (
    id: string,
    payload: {
      amount: number;
      natural_probability: number;
      is_disputed?: boolean;
      is_opted_out?: boolean;
      days_overdue?: number;
      custom_action_probs?: Record<string, number>;
    }
  ) =>
    fetchJSON<DecisionExplanation>(`/opportunities/${id}/evaluate`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // Simulator
  runBatchSimulation: (batch_size: number = 100, seed: number = 42) =>
    fetchJSON<BatchSimulationResult>('/simulator/run-batch', {
      method: 'POST',
      body: JSON.stringify({ batch_size, seed }),
    }),

  // Bounded Execution
  executeAction: (
    opportunity_id: string,
    payload: {
      action: ActionType;
      amount: number;
      natural_probability: number;
      customer_id?: string;
      invoice_id?: string;
      is_disputed?: boolean;
      is_opted_out?: boolean;
      idempotency_key?: string;
      provider_scenario?: string;
    }
  ) =>
    fetchJSON<ExecutionRecord>(`/opportunities/${opportunity_id}/execute`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getExecution: (execution_id: string) =>
    fetchJSON<ExecutionRecord>(`/executions/${execution_id}`),

  getTimeline: (opportunity_id: string) =>
    fetchJSON<TimelineEvent[]>(`/opportunities/${opportunity_id}/timeline`),

  getAudit: (opportunity_id: string) =>
    fetchJSON<Record<string, any>[]>(`/opportunities/${opportunity_id}/audit`),

  resetTestProvider: () =>
    fetchJSON<{ message: string }>('/test-provider/reset', {
      method: 'POST',
    }),

  syncPaymentStatus: (opportunity_id: string) =>
    fetchJSON<import('./types').SyncPaymentResponse>(`/opportunities/${opportunity_id}/sync-payment`, {
      method: 'POST',
    }),

  getGlobalAuditEvents: () =>
    fetchJSON<import('./types').AuditEvent[]>('/audit/events'),

  getPolicyGuardrails: () =>
    fetchJSON<import('./types').PolicyGuardrailsConfig>('/audit/policy'),
};
