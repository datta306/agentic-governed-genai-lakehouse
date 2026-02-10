# Agentic Governed GenAI Lakehouse

A production-style **agentic analytics system** that investigates KPI anomalies using **governed SQL tool-use**, **RAG-grounded explanations**, and **role-based access control**, with full auditability and daily monitoring.

This project demonstrates how modern GenAI systems should be built **safely, observably, and reproducibly** — not as a chat demo, but as an **operational data product**.

---

## 🔍 Example Question

> **Why did revenue drop yesterday?**

The agent:
1. Detects a revenue anomaly
2. Checks data freshness
3. Investigates missing SKUs (if role permits)
4. Grounds the explanation using internal documentation (RAG)
5. Logs every action for audit & compliance

---

## 🧠 Key Features

### 1) Agentic Tool Orchestration
- LLM-style planner logic that decides **which tools to call and in what order**
- SQL tools for KPIs, freshness checks, SKU investigation
- RAG retrieval for trusted explanations

### 2) Governance & Security
- Role-based access control:
  - **finance** → SKU-level visibility
  - **ops** → aggregate-only metrics
- Permission checks enforced at the **tool layer**
- All tool calls audited with run lineage

### 3) RAG (Retrieval-Augmented Generation)
- Internal markdown documentation embedded into Qdrant
- Semantic retrieval using sentence-transformers
- Retrieved context is filtered by user role
- Agent outputs include **document sources**

### 4) Audit, Lineage & Observability
- PostgreSQL-backed audit tables:
  - agent runs
  - tool calls
  - alert events
- Every answer is traceable to:
  - SQL queries
  - documents used
  - timestamps

### 5) Daily Anomaly Monitoring Pipeline
- Scheduled “daily job” checks revenue drops
- Threshold-based alert creation
- Triggers deeper agent investigation when anomalies are detected

---