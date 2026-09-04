# RecoverAI — Agent Engineering Rules

## 1. Source of Truth

Before modifying the project, read:

- PROJECT_SPEC.md
- AGENT_RULES.md

PROJECT_SPEC.md defines WHAT the system must be.

AGENT_RULES.md defines HOW the implementation agent must work.

---

## 2. Do Not Overbuild

The deadline is September 3, 2026.

Prioritize a complete working MVP over theoretical completeness.

Do not introduce:

- unnecessary microservices
- unnecessary AI agents
- unnecessary LLMs
- reinforcement learning
- complex infrastructure
- premature optimization

---

## 3. Never Fabricate

Never fabricate:

- datasets
- model metrics
- recovery results
- financial outcomes
- causal claims
- Razorpay behavior
- production results

If something is simulated, label it simulated.

If something is assumed, label it assumed.

If something is unknown, say unknown.

---

## 4. ML Discipline

Never use future information as a feature.

Always separate:

features
labels
future outcomes

Run leakage checks before model training.

---

## 5. Economic Discipline

Never select an intervention solely because it has the highest probability.

Always consider:

natural recovery
incremental recovery
intervention cost
policy constraints

---

## 6. Action Safety

ML predictions must never directly execute financial actions.

Required chain:

Prediction
→ Economics
→ Policy
→ Executor

---

## 7. Testing

Every new service requires tests.

Every major workflow must have an integration test.

Do not report a feature as complete if it has not been tested.

---

## 8. Existing Code

Do not rewrite working infrastructure without reason.

Inspect existing code first.

Reuse existing:

- FastAPI setup
- PostgreSQL setup
- Redis setup
- SQLAlchemy
- Alembic
- configuration
- logging

---

## 9. Database

Use migrations.

Do not manually modify production schema.

Every schema change must have an Alembic migration.

---

## 10. Documentation

When architecture changes, update PROJECT_SPEC.md or DECISIONS.md.

When completing a task, update AGENT_PROGRESS.md.

---

## 11. Task Completion Report

Every task must end with:

### IMPLEMENTED
What was created or changed.

### TESTED
Tests executed and exact results.

### FAILED
Anything that failed.

### ASSUMPTIONS
Any assumptions made.

### CHANGED
Files changed.

### NEXT STEP
The smallest logical next task.

---

## 12. Scope Control

Do not start the next major phase automatically.

Finish the requested phase first.

Do not build frontend while the backend/data foundation is incomplete.

Do not build Razorpay integration before the recovery engine works locally.

---

## 13. Engineering Principle

Build the smallest system that convincingly proves:

Detect
→ Diagnose
→ Predict
→ Economically decide
→ Execute
→ Stop
→ Measure