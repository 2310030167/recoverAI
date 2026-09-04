export type ActionType = 'NO_ACTION' | 'REMINDER' | 'RETRY' | 'ESCALATE';
export type PolicyStatus = 'ELIGIBLE' | 'BLOCKED' | 'COOLDOWN_BLOCKED' | 'MAX_ATTEMPTS_EXCEEDED' | 'DISPUTE_BLOCKED' | 'INSUFFICIENT_ECONOMIC_VALUE' | 'RECOVERED';
export type ExecutionState = 'PENDING' | 'VALIDATING' | 'BLOCKED' | 'EXECUTING' | 'SUCCEEDED' | 'FAILED' | 'SKIPPED';
export type ProvenanceSource = 'EMPIRICAL' | 'DERIVED' | 'CONFIGURED' | 'SIMULATION_ASSUMPTION' | 'SYSTEM_SAFETY';

export interface RecoveryOpportunity {
  opportunity_id: string;
  customer_id: string;
  invoice_number: string;
  amount: number;
  due_date: string;
  days_overdue: number;
  horizon_window: '3d' | '7d' | '30d';
  natural_probability: number;
  assisted_probability: number;
  expected_incremental_revenue: number;
  recommended_action: ActionType;
  policy_status: PolicyStatus;
  recovery_status?: string;
  is_recovered?: boolean;
  recovered_amount?: number;
  is_disputed: boolean;
  is_opted_out: boolean;
}

export interface CandidateEvaluation {
  action: ActionType;
  natural_probability: number;
  assisted_probability: number;
  incremental_probability: number;
  intervention_cost: number;
  expected_incremental_revenue: number;
  is_positive_ev: boolean;
  policy_status: PolicyStatus;
  policy_reasons: string[];
  is_eligible: boolean;
}

export interface DecisionExplanation {
  opportunity_id: string;
  amount: number;
  natural_probability: number;
  recommended_action: ActionType;
  selected_action: ActionType;
  policy_status: PolicyStatus;
  policy_reasons: string[];
  expected_incremental_revenue: number;
  assisted_probability: number;
  candidate_evaluations: CandidateEvaluation[];
  explanation: string;
  evidence_level: string;
}

export interface BatchSimulationResult {
  total_opportunity_count: number;
  total_invoice_value: number;
  baseline_recovered_amount: number;
  baseline_intervention_cost: number;
  baseline_net_recovered_value: number;
  baseline_recovery_rate: number;
  recoverai_recovered_amount: number;
  recoverai_intervention_cost: number;
  recoverai_net_recovered_value: number;
  recoverai_recovery_rate: number;
  incremental_recovered_amount: number;
  net_incremental_revenue: number;
  recovery_rate_3d: number;
  recovery_rate_7d: number;
  recovery_rate_30d: number;
  avg_interventions_per_opportunity: number;
  total_interventions_executed: number;
  blocked_interventions_count: number;
  stopped_interventions_count: number;
}

export interface ExecutionRecord {
  execution_id: string;
  opportunity_id: string;
  customer_id: string;
  invoice_id: string;
  action: ActionType;
  provider: string;
  idempotency_key: string;
  requested_at: string;
  executed_at?: string;
  execution_status: ExecutionState;
  failure_code?: string;
  failure_reason?: string;
  provider_reference?: string;
  intervention_cost: number;
  policy_snapshot: Record<string, any>;
  economic_snapshot: Record<string, any>;
  metadata?: Record<string, any>;
  is_idempotent_replay: boolean;
}

export interface TimelineEvent {
  timestamp: string;
  event_type: string;
  title: string;
  description: string;
  actor: string;
  metadata: Record<string, any>;
}

export interface SyncPaymentResponse {
  success: boolean;
  opportunity_id: string;
  provider_reference?: string;
  payment_status: string;
  recovery_status: string;
  is_recovered: boolean;
  recovered_amount: number;
  payment_link_url?: string;
  amount_paid?: number;
  message: string;
  error_code?: string;
  error_message?: string;
}
