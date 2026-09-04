import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from app.schemas.execution import (
    ExecutionRequest,
    ExecutionRecordSchema,
    ExecutionState,
    ProviderType,
    ProviderScenario,
    OpportunityTimelineResponse
)
from app.schemas.canonical import ActionType
from app.services.execution.action_validator import ActionValidator
from app.services.execution.provider import (
    BaseExecutionProvider,
    RazorpayTestModeProvider,
    RazorpayPaymentLinkProvider,
    ProviderExecutionResult
)
from app.services.execution.idempotency import IdempotencyStore
from app.services.execution.result_processor import ExecutionResultProcessor
from app.services.decision_engine import DecisionEngine
from app.services.economic_engine import EconomicEngine
from app.core.config import settings
from app.core.logging import logger


class BoundedRecoveryExecutionEngine:
    """
    Bounded Recovery Execution Engine for RecoverAI.
    Orchestrates the target workflow:
    Opportunity -> Prediction -> Economic Evaluation -> Policy Validation -> Action Decision
    -> Execution Validation -> Provider Execution -> Result Processing -> Audit Event.
    
    GUARANTEE: The ExecutionEngine NEVER bypasses Policy validation.
    """

    def __init__(
        self,
        validator: Optional[ActionValidator] = None,
        provider: Optional[BaseExecutionProvider] = None,
        idempotency_store: Optional[IdempotencyStore] = None,
        result_processor: Optional[ExecutionResultProcessor] = None,
        decision_engine: Optional[DecisionEngine] = None
    ):
        self.validator = validator or ActionValidator()
        self.provider = provider or self._resolve_default_provider()
        self.idempotency_store = idempotency_store or IdempotencyStore()
        self.result_processor = result_processor or ExecutionResultProcessor()
        self.decision_engine = decision_engine or DecisionEngine()
        self.execution_records: Dict[str, ExecutionRecordSchema] = {}

    def _resolve_default_provider(self) -> BaseExecutionProvider:
        p_type = getattr(settings.execution, "RAZORPAY_PROVIDER_TYPE", "TEST_MODE")
        if str(p_type).upper() == "RAZORPAY_PAYMENT_LINK":
            logger.info("Initializing RazorpayPaymentLinkProvider from configuration settings.")
            return RazorpayPaymentLinkProvider()
        return RazorpayTestModeProvider()

    def reset_engine_state(self) -> None:
        """Reset all internal execution engine state."""
        self.provider.reset()
        self.idempotency_store.reset()
        self.result_processor.reset()
        self.execution_records.clear()
        logger.info("BoundedRecoveryExecutionEngine state reset.")

    def execute_opportunity_action(
        self,
        request: ExecutionRequest,
        amount: float = 10000.0,
        natural_prob: float = 0.35,
        customer_id: str = "CUST_DEFAULT",
        invoice_id: str = "INV_DEFAULT",
        is_disputed: bool = False,
        is_opted_out: bool = False,
        retry_count: int = 0,
        total_interventions: int = 0,
        hours_since_last_intervention: Optional[float] = None,
        days_overdue: int = 0,
        is_recovered: bool = False,
        is_expired: bool = False
    ) -> ExecutionRecordSchema:
        """
        Execute bounded action for an opportunity.
        """
        requested_action = request.action

        # 1. Idempotency Key Generation & Check
        idem_key = self.idempotency_store.generate_idempotency_key(
            opportunity_id=request.opportunity_id,
            action=requested_action.value,
            attempt_number=total_interventions + 1,
            client_key=request.idempotency_key
        )

        cached_rec = self.idempotency_store.get(idem_key)
        if cached_rec:
            logger.info(f"Duplicate execution request detected for Opportunity ID={request.opportunity_id}. Returning cached record.")
            cached_rec.is_idempotent_replay = True
            return cached_rec

        # Create Initial Pending Execution Record
        exec_id = f"EXEC_{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc)
        
        cost_map = {ActionType.NO_ACTION: 0.0, ActionType.REMINDER: 0.50, ActionType.RETRY: 2.00, ActionType.ESCALATE: 50.00}
        intervention_cost = cost_map.get(requested_action, 0.0)

        record = ExecutionRecordSchema(
            execution_id=exec_id,
            opportunity_id=request.opportunity_id,
            customer_id=customer_id,
            invoice_id=invoice_id,
            action=requested_action,
            provider=request.provider,
            idempotency_key=idem_key,
            requested_at=now,
            execution_status=ExecutionState.PENDING,
            intervention_cost=intervention_cost,
            policy_snapshot={"is_disputed": is_disputed, "is_opted_out": is_opted_out, "retry_count": retry_count},
            economic_snapshot={"amount": amount, "natural_prob": natural_prob, "action": requested_action.value}
        )

        # 2. Independent Action Validation Check (NEVER BYPASSED)
        record.execution_status = ExecutionState.VALIDATING
        val_res = self.validator.validate_execution_request(
            opportunity_id=request.opportunity_id,
            action=requested_action,
            amount=amount,
            natural_prob=natural_prob,
            is_disputed=is_disputed,
            is_opted_out=is_opted_out,
            retry_count=retry_count,
            total_interventions=total_interventions,
            hours_since_last_intervention=hours_since_last_intervention,
            days_overdue=days_overdue,
            is_recovered=is_recovered,
            is_expired=is_expired
        )

        if not val_res.is_valid:
            record.execution_status = ExecutionState.BLOCKED
            record.failure_code = "EXECUTION_POLICY_BLOCKED"
            record.failure_reason = val_res.blocking_reason
            record.executed_at = datetime.now(timezone.utc)
            
            self.idempotency_store.put(idem_key, record)
            self.execution_records[exec_id] = record
            return record

        # 3. Provider Pathway Execution
        record.execution_status = ExecutionState.EXECUTING

        if requested_action == ActionType.NO_ACTION:
            provider_res = ProviderExecutionResult(
                success=True,
                provider=ProviderType.TEST_MODE,
                provider_reference=f"NO_ACTION_SKIPPED_{uuid.uuid4().hex[:6].upper()}",
                execution_state=ExecutionState.SKIPPED
            )
        else:
            provider_res = self.provider.execute_action(
                opportunity_id=request.opportunity_id,
                action=requested_action,
                amount=amount,
                customer_id=customer_id,
                scenario=request.provider_scenario
            )

        # 4. Result Processing & Timeline/Audit Generation
        final_record = self.result_processor.process_result(
            record=record,
            provider_result=provider_res,
            amount=amount,
            simulate_recovery=request.simulate_recovery_on_success
        )

        # 5. Save in Stores
        self.idempotency_store.put(idem_key, final_record)
        self.execution_records[exec_id] = final_record

        return final_record

    def get_execution(self, execution_id: str) -> Optional[ExecutionRecordSchema]:
        """Fetch execution record by ID."""
        return self.execution_records.get(execution_id)

    def sync_opportunity_payment(self, opportunity_id: str) -> Dict[str, Any]:
        """
        Synchronizes payment status for an opportunity with Razorpay API.
        STRICT GUARANTEE: Read-only check & status settlement. Never re-executes action or creates payment links.
        Resolution Order:
        1. Search in-memory execution_records.
        2. Search idempotency_store.
        3. Fallback: Query Razorpay Payment Links API by reference_id (RECOVERAI_<opportunity_id>) and reconstruct record.
        """
        # A. Find matching execution record for opportunity
        matching_recs = [r for r in self.execution_records.values() if r.opportunity_id == opportunity_id]
        
        # B. Fallback check in idempotency store
        if not matching_recs:
            matching_recs = self.idempotency_store.get_records_for_opportunity(opportunity_id)

        # C. Provider Reconciliation Fallback via reference_id
        if not matching_recs:
            ref_id = f"RECOVERAI_{opportunity_id}"
            logger.info(f"Execution record not found in memory for Opportunity ID={opportunity_id}. Attempting provider reference correlation for ref_id={ref_id}")
            rzp_search = self.provider.fetch_payment_link_by_reference_id(ref_id)
            
            if rzp_search.get("success") and "payment_link" in rzp_search:
                plink = rzp_search["payment_link"]
                plink_id = plink.get("id")
                short_url = plink.get("short_url", f"https://rzp.io/i/{plink_id}")
                notes = plink.get("notes", {})
                act_val = notes.get("action", "RETRY")
                
                # Reconstruct minimum execution record needed for settlement
                exec_id = f"EXEC_{uuid.uuid4().hex[:8].upper()}"
                rec_action = ActionType(act_val) if act_val in [a.value for a in ActionType] else ActionType.RETRY
                cost = 2.0 if rec_action == ActionType.RETRY else (0.5 if rec_action == ActionType.REMINDER else 50.0)
                
                reconstructed_record = ExecutionRecordSchema(
                    execution_id=exec_id,
                    opportunity_id=opportunity_id,
                    customer_id=notes.get("customer_id", "CUST_RECON"),
                    invoice_id=opportunity_id,
                    action=rec_action,
                    provider=getattr(self.provider, "provider_name", ProviderType.RAZORPAY_PAYMENT_LINK),
                    idempotency_key=f"IDEM_RECON_{uuid.uuid4().hex[:6].upper()}",
                    requested_at=datetime.now(timezone.utc),
                    executed_at=datetime.now(timezone.utc),
                    execution_status=ExecutionState.SUCCEEDED,
                    provider_reference=plink_id,
                    intervention_cost=cost,
                    metadata={
                        "payment_link_url": short_url,
                        "razorpay_reference_id": ref_id,
                        "payment_status": "PENDING",
                        "recovery_status": "AWAITING_PAYMENT"
                    }
                )
                
                # Store reconstructed record in memory for remainder of process life
                self.execution_records[exec_id] = reconstructed_record
                self.idempotency_store.put(reconstructed_record.idempotency_key, reconstructed_record)
                matching_recs = [reconstructed_record]
                logger.info(f"Successfully reconstructed execution record {exec_id} from Razorpay Payment Link {plink_id}")

        if not matching_recs:
            return {
                "success": False,
                "error_code": "EXECUTION_RECORD_NOT_FOUND",
                "error_message": f"No execution record found for opportunity ID={opportunity_id}."
            }

        # Sort by executed_at descending
        record = sorted(matching_recs, key=lambda x: x.executed_at or datetime.min, reverse=True)[0]
        plink_id = record.provider_reference

        if not plink_id:
            return {
                "success": False,
                "error_code": "PAYMENT_LINK_NOT_FOUND",
                "error_message": f"Execution record {record.execution_id} does not have a valid Razorpay Payment Link ID.",
                "opportunity_id": opportunity_id,
                "provider_reference": plink_id
            }

        # Query Razorpay API status
        rzp_res = self.provider.fetch_payment_link_status(plink_id)
        if not rzp_res.get("success", False):
            return {
                "success": False,
                "error_code": rzp_res.get("error_code", "STATUS_FETCH_FAILED"),
                "error_message": rzp_res.get("error_message", "Failed to fetch Payment Link status from Razorpay."),
                "opportunity_id": opportunity_id,
                "provider_reference": plink_id
            }

        # Update settlement state in result processor
        rec, outcome = self.result_processor.update_payment_settlement(record, rzp_res)

        return {
            "success": True,
            "opportunity_id": opportunity_id,
            "provider_reference": plink_id,
            "payment_status": rec.metadata.get("payment_status", "PENDING"),
            "recovery_status": rec.metadata.get("recovery_status", "AWAITING_PAYMENT"),
            "is_recovered": outcome.is_recovered if outcome else False,
            "recovered_amount": outcome.recovered_amount if outcome else 0.0,
            "payment_link_url": rec.metadata.get("payment_link_url"),
            "amount_paid": float(rzp_res.get("amount_paid", 0)) / 100.0 if rzp_res.get("amount_paid") else 0.0,
            "message": "Payment verified and recovery recorded successfully." if (outcome and outcome.is_recovered) else "Payment status checked. Link remains awaiting payment."
        }
