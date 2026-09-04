import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from app.schemas.execution import (
    ExecutionRecordSchema,
    ExecutionState,
    ProviderType,
    DetailedRecoveryOutcomeSchema,
    RecoverySourceType,
    OpportunityTimelineEvent,
    OpportunityTimelineResponse
)
from app.schemas.canonical import ActionType, ExecutionStatus, PolicyStatus
from app.services.execution.provider import ProviderExecutionResult
from app.core.logging import logger


class ExecutionResultProcessor:
    """
    Execution Result & Recovery Outcome Processor.
    Updates DB domain models, generates InterventionEvents, RecoveryOutcomes, and AuditEvent timeline records.
    """

    def __init__(self):
        self.outcomes_store: Dict[str, DetailedRecoveryOutcomeSchema] = {}
        self.timeline_store: Dict[str, List[OpportunityTimelineEvent]] = {}
        self.audit_store: Dict[str, List[Dict[str, Any]]] = {}

    def reset(self) -> None:
        """Reset result processor stores."""
        self.outcomes_store.clear()
        self.timeline_store.clear()
        self.audit_store.clear()

    def process_result(
        self,
        record: ExecutionRecordSchema,
        provider_result: ProviderExecutionResult,
        amount: float,
        simulate_recovery: bool = True
    ) -> ExecutionRecordSchema:
        """
        Process provider execution output and update execution record and recovery outcome.
        """
        record.executed_at = datetime.now(timezone.utc)

        # 1. Timeline event logging
        timeline_events = self.timeline_store.setdefault(record.opportunity_id, [])
        audit_events = self.audit_store.setdefault(record.opportunity_id, [])

        if provider_result.success:
            record.execution_status = provider_result.execution_state
            record.provider_reference = provider_result.provider_reference
            record.provider = provider_result.provider
            record.metadata = provider_result.metadata

            if provider_result.provider == ProviderType.RAZORPAY_PAYMENT_LINK:
                short_url = provider_result.metadata.get("payment_link_url", "")
                
                # Add Timeline Event for Payment Link
                timeline_events.append(
                    OpportunityTimelineEvent(
                        timestamp=record.executed_at,
                        event_type="PAYMENT_LINK_CREATED",
                        title="Payment Link Created (Awaiting Payment)",
                        description=f"Razorpay Payment Link generated for ₹{amount:,.2f}. Status=AWAITING_PAYMENT. Link: {short_url}",
                        metadata={
                            "cost": record.intervention_cost,
                            "provider_ref": provider_result.provider_reference,
                            "payment_link_url": short_url,
                            "payment_status": "PENDING"
                        }
                    )
                )

                # Audit Event
                audit_events.append({
                    "id": f"AUD_{uuid.uuid4().hex[:8].upper()}",
                    "opportunity_id": record.opportunity_id,
                    "event_type": "PAYMENT_LINK_CREATED_SUCCESS",
                    "actor": "EXECUTION_ENGINE",
                    "details": f"Razorpay Payment Link {provider_result.provider_reference} created for ₹{amount:,.2f}. Status=AWAITING_PAYMENT. URL={short_url}",
                    "timestamp": record.executed_at
                })
            else:
                # Add Timeline Event for local test mode
                timeline_events.append(
                    OpportunityTimelineEvent(
                        timestamp=record.executed_at,
                        event_type="ACTION_EXECUTED",
                        title=f"Executed Action: {record.action.value}",
                        description=f"Action {record.action.value} processed via provider {record.provider.value}. Status={record.execution_status.value}. Ref={provider_result.provider_reference}",
                        metadata={"cost": record.intervention_cost, "provider_ref": provider_result.provider_reference}
                    )
                )

                # Audit Event
                audit_events.append({
                    "id": f"AUD_{uuid.uuid4().hex[:8].upper()}",
                    "opportunity_id": record.opportunity_id,
                    "event_type": "ACTION_EXECUTED_SUCCESS",
                    "actor": "EXECUTION_ENGINE",
                    "details": f"Action {record.action.value} processed. Status={record.execution_status.value}. Cost=₹{record.intervention_cost:,.2f}. ProviderRef={provider_result.provider_reference}",
                    "timestamp": record.executed_at
                })

            # Process Test-Mode Recovery Outcome if configured
            if simulate_recovery and record.action != ActionType.NO_ACTION:
                outcome_id = f"OUT_{uuid.uuid4().hex[:8].upper()}"
                net_val = amount - record.intervention_cost
                
                is_plink = (provider_result.provider == ProviderType.RAZORPAY_PAYMENT_LINK)
                outcome = DetailedRecoveryOutcomeSchema(
                    outcome_id=outcome_id,
                    opportunity_id=record.opportunity_id,
                    is_recovered=not is_plink,  # Payment link is awaiting payment until customer pays
                    recovered_amount=amount if not is_plink else 0.0,
                    recovered_at=record.executed_at if not is_plink else None,
                    recovery_window="30d",
                    recovery_source=RecoverySourceType.TEST_MODE_EXECUTED_RECOVERY,
                    action_that_preceded_recovery=record.action,
                    intervention_count=1,
                    total_intervention_cost=record.intervention_cost,
                    net_recovery_value=round(net_val, 2) if not is_plink else 0.0
                )
                self.outcomes_store[record.opportunity_id] = outcome

                if not is_plink:
                    timeline_events.append(
                        OpportunityTimelineEvent(
                            timestamp=record.executed_at,
                            event_type="RECOVERY_OBSERVED",
                            title=f"Test-Mode Recovery Observed: ₹{amount:,.2f}",
                            description=f"Recovery outcome recorded via action {record.action.value}. Net Value=₹{net_val:,.2f}",
                            metadata={"recovered_amount": amount, "net_value": net_val, "source": RecoverySourceType.TEST_MODE_EXECUTED_RECOVERY.value}
                        )
                    )

        else:
            record.execution_status = provider_result.execution_state
            record.failure_code = provider_result.failure_code
            record.failure_reason = provider_result.failure_reason

            timeline_events.append(
                OpportunityTimelineEvent(
                    timestamp=record.executed_at,
                    event_type="ACTION_EXECUTION_FAILED",
                    title=f"Action Failed: {record.action.value}",
                    description=f"Provider execution failed. Code={provider_result.failure_code}, Reason={provider_result.failure_reason}",
                    metadata={"failure_code": provider_result.failure_code, "failure_reason": provider_result.failure_reason}
                )
            )

            audit_events.append({
                "id": f"AUD_{uuid.uuid4().hex[:8].upper()}",
                "opportunity_id": record.opportunity_id,
                "event_type": "ACTION_EXECUTION_FAILED",
                "actor": "EXECUTION_ENGINE",
                "details": f"Action {record.action.value} failed. Reason={provider_result.failure_reason}",
                "timestamp": record.executed_at
            })

        logger.info(
            f"Processed result for Execution ID={record.execution_id}: Status={record.execution_status.value}"
        )
        return record

    def get_outcome(self, opportunity_id: str) -> Optional[DetailedRecoveryOutcomeSchema]:
        """Fetch recovery outcome for opportunity."""
        return self.outcomes_store.get(opportunity_id)

    def get_timeline(self, opportunity_id: str) -> List[OpportunityTimelineEvent]:
        """Fetch opportunity timeline events."""
        return self.timeline_store.get(opportunity_id, [])

    def get_audit_trail(self, opportunity_id: str) -> List[Dict[str, Any]]:
        """Fetch audit events for opportunity."""
        return self.audit_store.get(opportunity_id, [])

    def get_all_audit_events(self) -> List[Dict[str, Any]]:
        """
        Fetch all portfolio-level audit events across all opportunities,
        sorted chronologically by timestamp (newest first).
        """
        all_events: List[Dict[str, Any]] = []
        for events in self.audit_store.values():
            all_events.extend(events)

        def parse_ts(item):
            ts = item.get("timestamp")
            if hasattr(ts, "isoformat"):
                return ts.isoformat()
            return str(ts or "")

        all_events.sort(key=parse_ts, reverse=True)
        return all_events

    def update_payment_settlement(
        self,
        record: ExecutionRecordSchema,
        razorpay_data: Dict[str, Any]
    ) -> Tuple[ExecutionRecordSchema, DetailedRecoveryOutcomeSchema]:
        """
        Updates payment settlement outcome when Razorpay Payment Link status is fetched.
        Truthfully transitions AWAITING_PAYMENT -> RECOVERED only if Razorpay status is 'paid'.
        Idempotent: Prevents duplicate timeline/audit events or double counting.
        """
        opportunity_id = record.opportunity_id
        timeline_events = self.timeline_store.setdefault(opportunity_id, [])
        audit_events = self.audit_store.setdefault(opportunity_id, [])
        outcome = self.outcomes_store.get(opportunity_id)

        status = str(razorpay_data.get("status", "created")).lower()
        amount_paid_paise = razorpay_data.get("amount_paid", 0) or 0
        amount_paid_rupees = round(float(amount_paid_paise) / 100.0, 2)
        if amount_paid_rupees <= 0 and status == "paid":
            amount_paid_rupees = round(float(razorpay_data.get("amount", 0) or 0) / 100.0, 2)

        # Handle UNPAID state (created / pending / cancelled)
        if status != "paid":
            if outcome is None:
                net_val = 0.0 - record.intervention_cost
                outcome = DetailedRecoveryOutcomeSchema(
                    outcome_id=f"OUT_{uuid.uuid4().hex[:8].upper()}",
                    opportunity_id=opportunity_id,
                    is_recovered=False,
                    recovered_amount=0.0,
                    recovered_at=None,
                    recovery_window="30d",
                    recovery_source=RecoverySourceType.TEST_MODE_EXECUTED_RECOVERY,
                    action_that_preceded_recovery=record.action,
                    intervention_count=1,
                    total_intervention_cost=record.intervention_cost,
                    net_recovery_value=round(net_val, 2)
                )
                self.outcomes_store[opportunity_id] = outcome
            return record, outcome

        # Handle PAID state (Idempotency Check)
        already_settled = outcome is not None and outcome.is_recovered
        if already_settled:
            logger.info(f"Opportunity ID={opportunity_id} payment already settled as RECOVERED. Returning current outcome.")
            return record, outcome

        now = datetime.now(timezone.utc)
        record.metadata["payment_status"] = "PAID"
        record.metadata["recovery_status"] = "RECOVERED"
        record.metadata["amount_paid"] = amount_paid_rupees
        record.metadata["paid_at"] = razorpay_data.get("paid_at") or now.isoformat()

        net_val = round(amount_paid_rupees - record.intervention_cost, 2)

        if outcome is None:
            outcome = DetailedRecoveryOutcomeSchema(
                outcome_id=f"OUT_{uuid.uuid4().hex[:8].upper()}",
                opportunity_id=opportunity_id,
                is_recovered=True,
                recovered_amount=amount_paid_rupees,
                recovered_at=now,
                recovery_window="30d",
                recovery_source=RecoverySourceType.TEST_MODE_EXECUTED_RECOVERY,
                action_that_preceded_recovery=record.action,
                intervention_count=1,
                total_intervention_cost=record.intervention_cost,
                net_recovery_value=net_val
            )
            self.outcomes_store[opportunity_id] = outcome
        else:
            outcome.is_recovered = True
            outcome.recovered_amount = amount_paid_rupees
            outcome.recovered_at = now
            outcome.net_recovery_value = net_val

        # Add RECOVERY_OBSERVED Timeline Event (Created exactly once)
        timeline_events.append(
            OpportunityTimelineEvent(
                timestamp=now,
                event_type="RECOVERY_OBSERVED",
                title=f"Razorpay Payment Verified: ₹{amount_paid_rupees:,.2f}",
                description=f"Payment of ₹{amount_paid_rupees:,.2f} confirmed via Razorpay Payment Links API. Net Recovery=₹{net_val:,.2f}",
                metadata={
                    "recovered_amount": amount_paid_rupees,
                    "net_value": net_val,
                    "provider_ref": record.provider_reference,
                    "payment_status": "PAID",
                    "recovery_status": "RECOVERED",
                    "source": "RAZORPAY_PAYMENT_LINK"
                }
            )
        )

        # Add PAYMENT_RECEIVED_SUCCESS Audit Event (Created exactly once)
        audit_events.append({
            "id": f"AUD_{uuid.uuid4().hex[:8].upper()}",
            "opportunity_id": opportunity_id,
            "event_type": "PAYMENT_RECEIVED_SUCCESS",
            "actor": "EXECUTION_ENGINE",
            "details": f"Razorpay Payment Link {record.provider_reference} verified PAID. Recovered amount=₹{amount_paid_rupees:,.2f}. NetValue=₹{net_val:,.2f}",
            "timestamp": now
        })

        logger.info(f"Settlement complete for Opportunity ID={opportunity_id}: RECOVERED ₹{amount_paid_rupees:,.2f}")
        return record, outcome
