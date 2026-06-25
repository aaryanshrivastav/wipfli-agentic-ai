# AgentDB: AI-Powered Supply Chain Decision Intelligence

AgentDB is an end-to-end supply chain decision intelligence system that transforms retail sales data into actionable inventory and procurement decisions. Built on Databricks, it combines demand forecasting, risk scoring, and agentic AI to automate supply chain planning and prevent stockouts while optimizing inventory levels.

The system addresses critical supply chain challenges: stockout risk (lost revenue), excess inventory (carrying costs), supplier disruption (delayed orders), and forecast uncertainty (demand volatility). By routing decisions through a hybrid AI agent — deterministic rules for simple cases, LLM reasoning for complex scenarios — AgentDB delivers fast, explainable, cost-optimized recommendations at scale.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA INGESTION (Bronze)                          │
│  M5 Forecasting Competition Dataset → Raw Delta Tables                  │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────────┐
│                      DATA TRANSFORMATION (Silver)                        │
│  Normalization, SCD Type 2, Unpivoting, Data Quality                   │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────────┐
│                     DIMENSIONAL MODELING (Gold)                          │
│  Star Schema: 5 Dimensions + 8 Fact Tables                             │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────────┐
│                       FEATURE ENGINEERING (Features)                     │
│  10 Pre-computed Feature Tables: Lag, Rolling Averages, Seasonality    │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────────┐
│                        FORECASTING (Forecasting)                         │
│  Prophet + XGBoost → MLflow Registry → Predictions                      │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────────┐
│                      INTELLIGENCE LAYER (Intelligence)                   │
│  Inventory Risk | Supplier Risk | Recommendation Registry              │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────────┐
│                          AGENTIC DECISION LAYER                          │
│  Tools → Context → Agent (Rule/LLM/Hybrid) → Validation → Logging      │
│  Actions: EXPEDITE_PO | REORDER | SUPPLIER_ALERT | NO_ACTION           │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────────┐
│                    EVALUATION & REPORTING (Evaluation)                   │
│  Agent Comparison | Business Metrics | Decision Explanation            │
└─────────────────────────────────────────────────────────────────────────┘
```

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Data Platform** | Databricks (Unity Catalog, Delta Lake) |
| **Processing** | Apache Spark 3.x (PySpark) |
| **Language** | Python 3.10+ |
| **Forecasting** | Prophet, XGBoost |
| **ML Ops** | MLflow (Model Registry, Tracking) |
| **LLM** | Llama 3.3 70B Instruct (Databricks Foundation Models) |
| **Agent Framework** | LangChain, LangGraph |
| **Database** | 50+ Delta tables across 8 schema zones |

## Features

* **Medallion Architecture**: Bronze → Silver → Gold → Features → Intelligence pipeline with full lineage tracking
* **Demand Forecasting**: Multi-horizon forecasts (7d, 14d, 30d) using Prophet and XGBoost with MLflow model registry
* **Risk Scoring**: Automated inventory risk and supplier risk computation with 4-level severity classification
* **Hybrid Agent System**: Intelligent routing between deterministic rules (93% of cases) and LLM reasoning (7% complex cases)
* **Decision Explanation**: Full provenance tracking with audit trail for every recommendation
* **Business Metrics**: Real-time tracking of stockouts prevented, fill rate, service level, and inventory optimization
* **Evaluation Framework**: Agent comparison (Rule vs LLM), decision quality metrics, and outcome tracking
* **Extensible Tools**: 5 pluggable tools for inventory, supplier, forecast, recommendation, and purchase order retrieval

## Repository Structure

```
wipfli-agentic-ai/
├── database/                   # 50+ SQL DDL files across 8 schema zones
│   ├── bronze/                # Raw data ingestion tables
│   ├── silver/                # Normalized entities + agent logs
│   ├── gold/                  # Star schema (5 dims, 8 facts)
│   ├── features/              # Pre-computed feature tables
│   ├── forecasting/           # Prediction storage + metrics
│   ├── intelligence/          # Risk scoring + recommendations
│   ├── reporting/             # Executive dashboards
│   └── evaluation/            # Agent performance metrics
│
├── deployment/                # DDL execution scripts
│   └── deploy_tables.py       # Orchestrates DDL deployment
│
├── notebooks/                 # Databricks notebooks (pipeline stages)
│   ├── setup/                 # Catalog, permissions, schema creation
│   ├── bronze/                # Data ingestion
│   ├── silver/                # Data transformation
│   ├── gold/                  # Dimensional modeling
│   ├── features/              # Feature engineering
│   ├── forecasting/           # ML model training + prediction
│   ├── intelligence/          # Risk scoring
│   └── agent/                 # Agent invocation
│
├── src/
│   ├── agents/                # Core agent system
│   │   ├── decision/          # Agent implementations (Rule, LLM, Hybrid)
│   │   ├── orchestrator/      # Context builder, tool registry, validator
│   │   ├── tools/             # 5 data retrieval tools
│   │   ├── memory/            # Run, tool, and action loggers
│   │   ├── services/          # Memory services
│   │   ├── evaluation/        # Comparison framework, metrics, explanations
│   │   ├── models/            # Data models
│   │   └── schemas/           # JSON schemas
│   │
│   ├── simulation/            # Synthetic supply chain data generators
│   └── tests/                 # 19 test files
│
├── scripts/                   # Utility scripts
├── docs/                      # Documentation (see links below)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Prerequisites

Before setting up AgentDB, ensure you have:

* **Databricks Workspace**: Unity Catalog enabled, Databricks Runtime 14.3+ (or ML Runtime 14.3+)
* **Foundation Model Endpoint**: `databricks-meta-llama-3-3-70b-instruct` enabled in your workspace
* **M5 Forecasting Dataset**: Download from [Kaggle M5 Forecasting Accuracy](https://www.kaggle.com/c/m5-forecasting-accuracy/data)
* **Catalog Permissions**: `CREATE CATALOG`, `CREATE SCHEMA`, `CREATE TABLE` on Unity Catalog
* **Python Environment**: Python 3.10+ with `pip` installed

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd wipfli-agentic-ai
   ```

2. **Deploy database schema**
   ```python
   # Run in Databricks notebook
   %run /Workspace/path/to/deployment/deploy_tables.py
   ```

3. **Load M5 dataset**
   - Place CSV files in `/Workspace/data/raw/`
   - Run bronze ingestion notebooks

4. **Execute pipeline notebooks** (in order)
   - Bronze → Silver → Gold → Features → Forecasting → Intelligence

5. **Invoke the agent**
   ```python
   from agents.orchestrator.run_supply_chain_agent_v2 import run_agent
   
   result = run_agent(
       agent_type="hybrid",
       product_key=1001,
       store_key=1,
       supplier_key=101
   )
   
   print(f"Action: {result['action']}")
   print(f"Priority: {result['priority']}")
   print(f"Reasoning: {result['reasoning']}")
   ```

6. **Verify setup**
   - Check that all 50+ tables are created: `SHOW TABLES IN agentdb.*`
   - Run `test_hybrid_agent.py` to validate agent routing

## Documentation

* **Architecture**
  - [End-to-End Workflow](docs/architecture/end_to_end_workflow.md) — Complete data-to-decision pipeline
  - [Agent Architecture](docs/architecture/agent_architecture.md) — Deep dive into agent design

* **Setup**
  - [Installation Guide](docs/setup/installation_guide.md) — Step-by-step setup instructions

* **Presentation**
  - [Demo Guide](docs/presentation/demo_guide.md) — Live demo preparation and execution

## Database Schema Zones

AgentDB organizes data into 8 logical zones:

| Zone | Schema | Tables | Purpose |
|------|--------|--------|---------|
| **Bronze** | `agentdb.bronze` | 3 | Raw M5 dataset ingestion |
| **Silver** | `agentdb.silver` | 15 | Normalized entities + agent operational logs |
| **Gold** | `agentdb.gold` | 13 | Star schema (5 dims, 8 facts) |
| **Features** | `agentdb.features` | 10 | Pre-computed ML features |
| **Forecasting** | `agentdb.forecasting` | 5 | Predictions, metrics, model registry |
| **Intelligence** | `agentdb.intelligence` | 3 | Risk scoring, recommendations |
| **Reporting** | `agentdb.reporting` | 10 | Executive dashboards |
| **Evaluation** | `agentdb.evaluation` | 5 | Agent performance metrics |

## Agent Actions

The agent system outputs one of four actions:

| Action | Priority | Trigger |
|--------|----------|---------|
| **EXPEDITE_PO** | CRITICAL | Stockout < 7 days, HIGH/CRITICAL inventory risk |
| **REORDER** | HIGH/MEDIUM | Stockout < 14 days, inventory below safety stock |
| **SUPPLIER_ALERT** | HIGH | CRITICAL supplier risk, disruption probability > 50% |
| **NO_ACTION** | LOW | Inventory healthy, no intervention needed |

## License

Proprietary — Wipfli LLP Internal Use Only

## Contact

For questions or issues, contact the project maintainers.
