# Agentic Governed GenAI Lakehouse

A production-style **agentic analytics system** that investigates KPI anomalies using **governed SQL tool-use**, **RAG-grounded explanations**, and **role-based access control (RBAC)** — with auditability and a daily monitoring job.

This is built like an **operational data product**, not a chatbot demo.

---

## What you can ask

> **"Why did revenue drop yesterday?"**

The agent:
1. Detects the anomaly from KPI tables
2. Checks data freshness
3. Investigates missing SKUs (if role permits)
4. Grounds explanation using internal docs (RAG)
5. Logs every tool call with run lineage

---

## Key features

- **Agentic tool orchestration**: SQL tools + RAG retrieval called in an intentional order
- **Governance & security**:
  - `finance` → allowed SKU-level details
  - `ops` → aggregate-only metrics
- **RAG (Retrieval-Augmented Generation)**: Qdrant vector search over internal markdown docs
- **Audit & lineage**: agent runs + tool calls logged in Postgres
- **Daily monitoring pipeline**: threshold-based anomaly detection + alert event logging

---

## Architecture (high level)

- **PostgreSQL**: gold tables + audit schema (+ alerts schema if enabled)
- **Qdrant**: vector database for RAG
- **Python**:
  - `agents/` planner agent
  - `tools/` governed SQL tools + RAG retriever
  - `pipelines/` daily monitor job
  - `governance/` RBAC + lineage logger

---

## Prerequisites

- Docker Desktop installed and running
- Python 3.10+ (3.11 recommended)
- On Docker v2, use: **`docker compose`** (not `docker-compose`)

---

## Quickstart (copy/paste)

```bash
# 1) Start infra
docker compose up -d

# 2) Create venv + install deps
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3) Build RAG index + run the agent
python rag/embedding_pipeline.py
python test_permissions.py
python agents/planner_agent.py --role finance --question "Why did revenue drop yesterday?"
