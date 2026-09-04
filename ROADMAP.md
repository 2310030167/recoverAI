
# RecoverAI — Execution Roadmap

Target submission: September 3, 2026

---

# PHASE 1 — DATA + DATABASE

## Day 1

- [ ] Create canonical data schemas
- [ ] Build data loaders
- [ ] Build cleaning pipeline
- [ ] Validate timestamps
- [ ] Validate monetary fields
- [ ] Detect leakage candidates
- [ ] Create database models
- [ ] Create initial Alembic migration
- [ ] Load small development dataset
- [ ] Tests

## Day 2

- [ ] Build canonical invoice table
- [ ] Build customer features
- [ ] Build payment features
- [ ] Build receivable features
- [ ] Point-in-time feature generation
- [ ] Feature validation
- [ ] Leakage tests

---

# PHASE 2 — ML

## Day 3

- [ ] Define prediction targets
- [ ] Build temporal train/validation/test split
- [ ] Train baseline model
- [ ] Evaluate
- [ ] Calibration
- [ ] Feature importance
- [ ] Save model artifact

## Day 4

- [ ] Natural recovery model
- [ ] Assisted recovery estimation
- [ ] Treatment/uplift experiment
- [ ] Document causal assumptions
- [ ] Evaluate counterfactual limitations

---

# PHASE 3 — ECONOMICS + POLICY

## Day 5

- [ ] Economic engine
- [ ] Intervention cost model
- [ ] Expected incremental revenue
- [ ] Action ranking
- [ ] Unit tests

## Day 6

- [ ] Policy engine
- [ ] Cooldowns
- [ ] retry limits
- [ ] recovery windows
- [ ] dispute protection
- [ ] stopping rules
- [ ] audit events

---

# PHASE 4 — RECOVERY WORKFLOW

## Day 7

- [ ] Recovery opportunity service
- [ ] intervention service
- [ ] simulator
- [ ] outcome generation
- [ ] end-to-end recovery workflow
- [ ] failure scenario

---

# PHASE 5 — EVALUATION

## Day 8

- [ ] Rule-based baseline
- [ ] RecoverAI batch evaluation
- [ ] recovered revenue
- [ ] incremental revenue
- [ ] intervention cost
- [ ] ROI
- [ ] model metrics

---

# PHASE 6 — FRONTEND

## Day 9

- [ ] Dashboard
- [ ] opportunity list
- [ ] opportunity detail
- [ ] decision explanation
- [ ] audit timeline

---

# PHASE 7 — INTEGRATION

## Day 10

- [ ] Razorpay test-mode integration
- [ ] webhook flow
- [ ] test event
- [ ] bounded action
- [ ] integration testing

---

# PHASE 8 — FINALIZATION

## Day 11

- [ ] Full end-to-end test
- [ ] Remove dead code
- [ ] Fix bugs
- [ ] Verify metrics
- [ ] README
- [ ] Architecture diagram
- [ ] 5-minute demo
- [ ] Failure demonstration
- [ ] Final submission package

---

# Critical Rule

If time becomes limited:

DO NOT cut:

- economic engine
- policy engine
- audit trail
- batch evaluation
- baseline comparison

Cut advanced features first.