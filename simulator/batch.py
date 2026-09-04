import random
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from simulator.state import SimulationOutcome, RecoveryStatus
from simulator.engine import RecoverySimulatorEngine
from app.schemas.canonical import ActionType
from app.services.data_loader import DataLoader
from app.services.decision_engine import DecisionEngine
from app.services.treatment_estimator import TreatmentEstimator
from app.core.logging import logger


class BatchSimulationResult(BaseModel):
    """
    Batch Simulation Comparison Report: Baseline (NO_ACTION) vs RecoverAI (Policy-Driven Strategy).
    DISCLAIMER: All values represent SIMULATED BATCH RESULTS USING EMPIRICAL INVOICE STATES.
    """
    total_opportunity_count: int
    total_invoice_value: float
    
    # Baseline (NO_ACTION) Metrics
    baseline_recovered_amount: float = Field(..., description="Simulated Baseline Recovered Revenue")
    baseline_intervention_cost: float
    baseline_net_recovered_value: float
    baseline_recovery_rate: float = Field(..., description="Simulated Baseline Recovery Rate")
    
    # RecoverAI Policy-Driven Metrics
    recoverai_recovered_amount: float = Field(..., description="Simulated RecoverAI Recovered Revenue")
    recoverai_intervention_cost: float
    recoverai_net_recovered_value: float
    recoverai_recovery_rate: float = Field(..., description="Simulated RecoverAI Recovery Rate")
    
    # Incremental Gains
    incremental_recovered_amount: float = Field(..., description="Simulated Incremental Revenue")
    net_incremental_revenue: float = Field(..., description="Simulated Net Incremental Revenue")
    
    # Window Recovery Rates (RecoverAI Strategy)
    recovery_rate_3d: float
    recovery_rate_7d: float
    recovery_rate_30d: float
    
    # Operational Metrics
    avg_interventions_per_opportunity: float
    total_interventions_executed: int
    blocked_interventions_count: int
    stopped_interventions_count: int
    
    # Details per opportunity
    opportunity_comparisons: List[Dict[str, Any]] = Field(default_factory=list)


class BatchSimulator:
    """
    Batch Simulator & Baseline Comparison Engine.
    Executes controlled batch simulations comparing Baseline (NO_ACTION) vs RecoverAI Policy Strategy.
    """

    def __init__(self, raw_data_dir: str = r"d:\recoverai\data\raw"):
        self.loader = DataLoader(raw_dir=raw_data_dir)

    def generate_empirical_opportunity_batch(self, batch_size: int = 100, seed: int = 42) -> List[Dict[str, Any]]:
        """
        Extract a deterministic batch of recovery opportunities from real Customer Invoices data.
        Uses fixed seed for reproducible evaluation without cherry-picking.
        """
        df = self.loader.load_customer_invoices()
        valid_df = df[df["due_in_date"].notna()].copy()
        
        # Sample deterministically
        sampled = valid_df.sample(n=min(batch_size, len(valid_df)), random_state=seed).reset_index(drop=True)

        batch: List[Dict[str, Any]] = []
        for i, row in sampled.iterrows():
            amt = float(row["total_open_amount"]) if row["total_open_amount"] > 0 else 10000.0
            
            # Synthetic dispute/opt-out signals based on fixed hashing for reproducibility
            is_disputed = (i % 17 == 0) # ~5.8% disputed
            is_opted_out = (i % 23 == 0) # ~4.3% opted out

            # Baseline probability estimate
            nat_prob = float(np.clip(0.30 + (i % 10) * 0.05, 0.15, 0.85))

            batch.append({
                "opportunity_id": f"OPP_BATCH_{i+1:04d}",
                "customer_id": str(row["cust_number"]),
                "amount": amt,
                "due_date": row["due_in_date"],
                "natural_prob": nat_prob,
                "is_disputed": is_disputed,
                "is_opted_out": is_opted_out,
            })

        logger.info(f"Generated empirical opportunity batch of {len(batch)} items (Seed={seed}).")
        return batch

    def run_batch_simulation(
        self,
        batch_size: int = 100,
        seed: int = 42,
        custom_opportunities: Optional[List[Dict[str, Any]]] = None,
        custom_action_multipliers: Optional[Dict[str, float]] = None
    ) -> BatchSimulationResult:
        """
        Execute Batch Simulation:
        RUN A: NO_ACTION Baseline Strategy
        RUN B: RecoverAI Policy-Driven Decision Strategy
        """
        if custom_opportunities:
            opps = custom_opportunities
        else:
            opps = self.generate_empirical_opportunity_batch(batch_size=batch_size, seed=seed)

        # Setup custom treatment estimator if multipliers provided
        custom_decision_engine = None
        if custom_action_multipliers:
            t_est = TreatmentEstimator(action_multipliers=custom_action_multipliers)
            custom_decision_engine = DecisionEngine(treatment_estimator=t_est)

        total_count = len(opps)
        total_val = sum(o["amount"] for o in opps)

        baseline_outcomes: List[SimulationOutcome] = []
        recoverai_outcomes: List[SimulationOutcome] = []
        comparisons: List[Dict[str, Any]] = []

        blocked_count = 0
        stopped_count = 0

        for idx, o in enumerate(opps):
            item_seed = seed + idx

            # Generate CRN uniform random draws for 35 daily steps
            rng = random.Random(item_seed)
            crn_draws = [rng.random() for _ in range(35)]

            # RUN A: Baseline (NO_ACTION)
            engine_baseline = RecoverySimulatorEngine(
                decision_engine=custom_decision_engine,
                random_seed=item_seed
            )
            out_base = engine_baseline.run_simulation(
                opportunity_id=o["opportunity_id"],
                customer_id=o["customer_id"],
                amount=o["amount"],
                due_date=o["due_date"],
                natural_prob=o["natural_prob"],
                is_disputed=o["is_disputed"],
                is_opted_out=o["is_opted_out"],
                strategy_override=ActionType.NO_ACTION,
                crn_draws=crn_draws
            )
            baseline_outcomes.append(out_base)

            # RUN B: RecoverAI (Policy-Driven DecisionEngine Strategy)
            engine_recoverai = RecoverySimulatorEngine(
                decision_engine=custom_decision_engine,
                random_seed=item_seed
            )
            out_rec = engine_recoverai.run_simulation(
                opportunity_id=o["opportunity_id"],
                customer_id=o["customer_id"],
                amount=o["amount"],
                due_date=o["due_date"],
                natural_prob=o["natural_prob"],
                is_disputed=o["is_disputed"],
                is_opted_out=o["is_opted_out"],
                crn_draws=crn_draws
            )
            recoverai_outcomes.append(out_rec)

            # Count policy blocks and stops
            for audit in out_rec.audit_trail:
                if audit.policy_status.value == "BLOCKED":
                    blocked_count += 1

            if out_rec.recovery_status.value in ["EXPIRED", "TERMINATED"]:
                stopped_count += 1

            comparisons.append({
                "opportunity_id": o["opportunity_id"],
                "amount": o["amount"],
                "baseline_status": out_base.recovery_status.value,
                "baseline_recovered": out_base.recovered_amount,
                "recoverai_status": out_rec.recovery_status.value,
                "recoverai_recovered": out_rec.recovered_amount,
                "recoverai_actions": [a.value for a in out_rec.selected_actions_history],
                "recoverai_cost": out_rec.total_intervention_cost,
                "net_gain": out_rec.net_recovered_value - out_base.net_recovered_value
            })

        # Aggregations
        b_rec_amt = sum(o.recovered_amount for o in baseline_outcomes)
        b_cost = sum(o.total_intervention_cost for o in baseline_outcomes)
        b_net = b_rec_amt - b_cost
        b_rate = (b_rec_amt / total_val * 100.0) if total_val > 0 else 0.0

        r_rec_amt = sum(o.recovered_amount for o in recoverai_outcomes)
        r_cost = sum(o.total_intervention_cost for o in recoverai_outcomes)
        r_net = r_rec_amt - r_cost
        r_rate = (r_rec_amt / total_val * 100.0) if total_val > 0 else 0.0

        inc_rec = r_rec_amt - b_rec_amt
        net_inc_rev = r_net - b_net

        # Window Recovery Rates for RecoverAI
        rec_3d_cnt = sum(1 for o in recoverai_outcomes if o.recovered_within_3d)
        rec_7d_cnt = sum(1 for o in recoverai_outcomes if o.recovered_within_7d)
        rec_30d_cnt = sum(1 for o in recoverai_outcomes if o.recovered_within_30d)

        rate_3d = (rec_3d_cnt / total_count * 100.0) if total_count > 0 else 0.0
        rate_7d = (rec_7d_cnt / total_count * 100.0) if total_count > 0 else 0.0
        rate_30d = (rec_30d_cnt / total_count * 100.0) if total_count > 0 else 0.0

        total_interventions = sum(o.total_interventions for o in recoverai_outcomes)
        avg_interventions = (total_interventions / total_count) if total_count > 0 else 0.0

        result = BatchSimulationResult(
            total_opportunity_count=total_count,
            total_invoice_value=round(total_val, 2),
            baseline_recovered_amount=round(b_rec_amt, 2),
            baseline_intervention_cost=round(b_cost, 2),
            baseline_net_recovered_value=round(b_net, 2),
            baseline_recovery_rate=round(b_rate, 2),
            recoverai_recovered_amount=round(r_rec_amt, 2),
            recoverai_intervention_cost=round(r_cost, 2),
            recoverai_net_recovered_value=round(r_net, 2),
            recoverai_recovery_rate=round(r_rate, 2),
            incremental_recovered_amount=round(inc_rec, 2),
            net_incremental_revenue=round(net_inc_rev, 2),
            recovery_rate_3d=round(rate_3d, 2),
            recovery_rate_7d=round(rate_7d, 2),
            recovery_rate_30d=round(rate_30d, 2),
            avg_interventions_per_opportunity=round(avg_interventions, 2),
            total_interventions_executed=total_interventions,
            blocked_interventions_count=blocked_count,
            stopped_interventions_count=stopped_count,
            opportunity_comparisons=comparisons
        )

        logger.info(
            f"Simulated Batch Completed ({total_count} opps): Baseline Net=INR {b_net:,.2f}, "
            f"RecoverAI Net=INR {r_net:,.2f}, Simulated Net Incremental Revenue=+INR {net_inc_rev:,.2f}"
        )
        return result
