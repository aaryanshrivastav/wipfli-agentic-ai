# Agent Decision Layer - Strategy Pattern

## Overview

The decision layer uses the **Strategy Pattern** to support multiple pluggable agent implementations without changing orchestration code.

This allows you to:
- ✅ Swap between rule-based and LLM-based agents
- ✅ A/B test different decision engines
- ✅ Gradually migrate from rules to LLM
- ✅ Add new agent types without modifying existing code
- ✅ Easily roll back if an agent underperforms

## Architecture

```
decision/
├── base_agent.py           # Abstract interface (BaseSupplyChainAgent)
├── rule_based_agent.py     # Deterministic business rules
└── llama_agent.py          # LLM-powered reasoning (Databricks Foundation Models)
```

### Base Agent Interface

All agents implement `BaseSupplyChainAgent`:

```python
class BaseSupplyChainAgent(ABC):
    @abstractmethod
    def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Args:
            context: {
                "inventory_risk": {...},
                "supplier_risk": {...},
                "forecast": {...},
                "recommendation": {...},
                "purchase_orders": {...}
            }
        
        Returns:
            {
                "action": "EXPEDITE_PO | REORDER | SUPPLIER_ALERT | NO_ACTION",
                "priority": "CRITICAL | HIGH | MEDIUM | LOW",
                "confidence": 0.0 to 1.0,
                "reasoning": "Explanation..."
            }
        """
        pass
```

## Agent Implementations

### 1. Rule-Based Agent

**File:** `rule_based_agent.py`

Uses deterministic if-then rules:

```python
from decision.rule_based_agent import RuleBasedAgent

agent = RuleBasedAgent()
result = agent.decide(context)
```

**Decision Logic:**
1. If `days_to_stockout < 7` → `EXPEDITE_PO` (CRITICAL)
2. If `supplier_risk_level in [HIGH, CRITICAL]` → `SUPPLIER_ALERT` (HIGH)
3. If `inventory_risk_level in [HIGH, CRITICAL]` → `REORDER` (HIGH)
4. Otherwise → `NO_ACTION` (LOW)

**Pros:**
- Deterministic and explainable
- No API costs
- Fast execution
- No hallucination risk

**Cons:**
- Rigid logic
- Can't learn from data
- Hard to capture complex patterns

---

### 2. Llama Agent (LLM-Powered)

**File:** `llama_agent.py`

Uses Databricks Foundation Models for intelligent reasoning:

```python
from decision.llama_agent import LlamaSupplyChainAgent

agent = LlamaSupplyChainAgent(
    model_name="databricks-meta-llama-3-1-70b-instruct",
    temperature=0.1,
    max_tokens=500
)
result = agent.decide(context)
```

**Key Design Principles:**
- ✅ **NO direct data access** - receives pre-computed context only
- ✅ **NO SQL queries** - all data retrieved by tools first
- ✅ **NO forecast computation** - uses existing forecasts
- ✅ **Pure reasoning** - only decides based on structured input
- ✅ **Structured JSON output** - validated by orchestrator

**Prompt Structure:**

```
You are a supply chain planner.

INVENTORY RISK:
- Current Quantity: 150
- Risk Level: HIGH
- Days to Stockout: 8
- 7-day Forecast Demand: 40

SUPPLIER RISK:
- Risk Level: LOW
- On-Time Delivery Rate: 95%

PURCHASE ORDERS:
- Open PO Count: 1

Return ONLY JSON:
{
  "action": "...",
  "priority": "...",
  "confidence": 0.0,
  "reasoning": "..."
}
```

**Pros:**
- Nuanced reasoning
- Adapts to context
- Natural language explanations
- Can handle edge cases

**Cons:**
- API costs
- Slower than rules
- Requires validation
- Potential for hallucination (mitigated by strict JSON schema)

---

## Usage

### Basic Usage

```python
from decision.rule_based_agent import RuleBasedAgent
from orchestrator.run_supply_chain_agent_v2 import run_supply_chain_agent

# Create agent
agent = RuleBasedAgent()

# Run orchestrator
result = run_supply_chain_agent(
    spark=spark,
    agent=agent,
    product_key=101,
    store_key=5,
    supplier_key=42
)

print(result)
# {
#   "action": "EXPEDITE_PO",
#   "priority": "CRITICAL",
#   "confidence": 0.95,
#   "reasoning": "Projected stockout within 3 days."
# }
```

### Swapping Agents at Runtime

```python
# Start with rule-based
agent = RuleBasedAgent()
result = run_supply_chain_agent(spark, agent, product_key, store_key, supplier_key)

# Switch to LLM - NO OTHER CODE CHANGES
agent = LlamaSupplyChainAgent()
result = run_supply_chain_agent(spark, agent, product_key, store_key, supplier_key)
```

### Configuration-Driven Selection

```python
# Feature flag / config
agent_type = dbutils.widgets.get("agent_type")  # "rule_based" or "llama"

if agent_type == "rule_based":
    agent = RuleBasedAgent()
elif agent_type == "llama":
    agent = LlamaSupplyChainAgent()

result = run_supply_chain_agent(spark, agent, product_key, store_key, supplier_key)
```

### A/B Testing

```python
import random

# 90% rule-based, 10% LLM for A/B test
if random.random() < 0.9:
    agent = RuleBasedAgent()
    experiment_group = "control"
else:
    agent = LlamaSupplyChainAgent()
    experiment_group = "treatment"

result = run_supply_chain_agent(spark, agent, product_key, store_key, supplier_key)

# Log which agent was used
result["experiment_group"] = experiment_group
```

---

## Adding New Agents

To add a new agent type:

1. **Create a new file** in `decision/`
2. **Inherit from `BaseSupplyChainAgent`**
3. **Implement `decide(context)` method**
4. **Use in orchestrator** - no other changes needed!

Example - Hybrid Agent:

```python
from .base_agent import BaseSupplyChainAgent
from .rule_based_agent import RuleBasedAgent
from .llama_agent import LlamaSupplyChainAgent

class HybridAgent(BaseSupplyChainAgent):
    """Uses rules for simple cases, LLM for complex cases."""
    
    def __init__(self):
        self.rule_agent = RuleBasedAgent()
        self.llama_agent = LlamaSupplyChainAgent()
    
    def decide(self, context):
        # Use rules for clear-cut cases
        days_to_stockout = context.get("inventory_risk", {}).get("projected_days_to_stockout")
        if days_to_stockout is not None and days_to_stockout < 7:
            return self.rule_agent.decide(context)
        
        # Use LLM for nuanced decisions
        return self.llama_agent.decide(context)
```

---

## Testing

Run the strategy pattern tests:

```python
%run /Workspace/Users/aaryan.shrivastav1403@gmail.com/wipfli-agentic-ai/src/tests/test_agent_strategy.py
```

This validates:
- ✅ Both agents implement the interface
- ✅ Both produce valid decisions
- ✅ Agents can be swapped at runtime
- ✅ Polymorphism works correctly

---

## Production Considerations

### When to Use Rule-Based Agent
- ✅ Business logic is well-defined
- ✅ Speed is critical
- ✅ Zero API cost required
- ✅ 100% deterministic behavior needed

### When to Use Llama Agent
- ✅ Complex reasoning required
- ✅ Edge cases are common
- ✅ Natural language explanations valued
- ✅ Learning from patterns is important

### Migration Strategy

1. **Start with Rules** - Validate baseline behavior
2. **Add LLM A/B Test** - Run 10% traffic on LLM
3. **Monitor Metrics** - Compare decision quality, latency, cost
4. **Gradual Rollout** - Increase LLM percentage if performing well
5. **Full Migration** - Switch default to LLM when confident
6. **Keep Rules as Fallback** - If LLM fails, fall back to rules

---

## Files

- `base_agent.py` - Abstract interface
- `rule_based_agent.py` - Rule-based implementation
- `llama_agent.py` - LLM-powered implementation
- `../orchestrator/run_supply_chain_agent_v2.py` - Updated orchestrator supporting Strategy Pattern
- `../tests/test_agent_strategy.py` - Strategy pattern tests
