"""Supply Chain Agent Orchestrator (Strategy Pattern)

Orchestrates the complete agent workflow with pluggable decision engines.

STRATEGY PATTERN IMPLEMENTATION:
The agent decision logic is pluggable - swap between implementations without
changing orchestration code:

    # Use rule-based agent
    from decision.rule_based_agent import RuleBasedAgent
    agent = RuleBasedAgent()
    result = run_supply_chain_agent(spark, agent, product_key, store_key, supplier_key)
    
    # Switch to LLM agent - NO OTHER CODE CHANGES
    from decision.llama_agent import LlamaSupplyChainAgent
    agent = LlamaSupplyChainAgent()
    result = run_supply_chain_agent(spark, agent, product_key, store_key, supplier_key)

WORKFLOW:
1. Start run → agent_run_log (RUNNING)
2. Execute 5 tools → agent_tool_execution_log (5 records)
3. Build context from tool outputs
4. Agent decides (pluggable strategy)
5. Validate decision structure
6. Log action → agent_action_log
7. Complete run → agent_run_log (SUCCESS)
"""

import sys
import time
from typing import Any, Dict

# Add parent directory to path for imports
sys.path.append('/Workspace/Users/aaryan.shrivastav1403@gmail.com/wipfli-agentic-ai/src/agents')

from decision.base_agent import BaseSupplyChainAgent
from services.memory_services import start_run, finish_run, execute_tool
from orchestrator.context_builder import build_agent_context
from orchestrator.output_validator import validate_agent_output
from orchestrator.tool_registry import TOOL_REGISTRY
from memory.action_logger import log_agent_action


def run_supply_chain_agent(
    spark,
    agent: BaseSupplyChainAgent,
    product_key: int,
    store_key: int,
    supplier_key: int
) -> Dict[str, Any]:
    """Run the complete supply chain agent workflow.
    
    Args:
        spark: SparkSession object
        agent: Agent implementation (ANY class implementing BaseSupplyChainAgent)
        product_key: Product identifier
        store_key: Store identifier
        supplier_key: Supplier identifier
        
    Returns:
        Decision dictionary: {action, priority, confidence, reasoning}
        
    Example:
        from decision.rule_based_agent import RuleBasedAgent
        agent = RuleBasedAgent()
        result = run_supply_chain_agent(spark, agent, 101, 5, 42)
        
    Raises:
        ValueError: If agent decision is invalid
        Exception: If any workflow step fails
    """
    start_time = time.time()
    run_id = None
    
    try:
        # ============================================================
        # STEP 1: Start Run
        # ============================================================
        run_id = start_run(
            spark=spark,
            agent_name=agent.get_name(),
            trigger_type="manual"
        )
        
        # ============================================================
        # STEP 2: Execute Tools (5 tools)
        # ============================================================
        
        # Tool 1: Inventory Risk
        inventory_risk = execute_tool(
            spark=spark,
            run_id=run_id,
            tool_name="get_inventory_risk",
            tool_function=TOOL_REGISTRY["get_inventory_risk"],
            entity_type="inventory",
            entity_id=product_key,
            product_key=product_key,
            store_key=store_key
        )
        
        # Tool 2: Supplier Risk
        supplier_risk = execute_tool(
            spark=spark,
            run_id=run_id,
            tool_name="get_supplier_risk",
            tool_function=TOOL_REGISTRY["get_supplier_risk"],
            entity_type="supplier",
            entity_id=supplier_key,
            supplier_key=supplier_key
        )
        
        # Tool 3: Forecast
        forecast = execute_tool(
            spark=spark,
            run_id=run_id,
            tool_name="get_forecast",
            tool_function=TOOL_REGISTRY["get_forecast"],
            entity_type="forecast",
            entity_id=product_key,
            product_key=product_key,
            store_key=store_key
        )
        
        # Tool 4: Previous Recommendation
        recommendation = execute_tool(
            spark=spark,
            run_id=run_id,
            tool_name="get_recommendation",
            tool_function=TOOL_REGISTRY["get_recommendation"],
            entity_type="recommendation",
            entity_id=product_key,
            product_key=product_key,
            store_key=store_key
        )
        
        # Tool 5: Purchase Orders
        purchase_orders = execute_tool(
            spark=spark,
            run_id=run_id,
            tool_name="get_open_purchase_orders",
            tool_function=TOOL_REGISTRY["get_open_purchase_orders"],
            entity_type="purchase_order",
            entity_id=product_key,
            product_key=product_key
        )
        
        # ============================================================
        # STEP 3: Build Context
        # ============================================================
        context = build_agent_context(
            inventory_risk=inventory_risk,
            supplier_risk=supplier_risk,
            forecast=forecast,
            recommendation=recommendation,
            purchase_orders=purchase_orders
        )
        
        # ============================================================
        # STEP 4: Agent Decides (STRATEGY PATTERN - PLUGGABLE!)
        # ============================================================
        # This is where the magic happens!
        # The agent parameter can be ANY class implementing BaseSupplyChainAgent:
        # - RuleBasedAgent: Deterministic business rules
        # - LlamaSupplyChainAgent: LLM-powered reasoning
        # - HybridAgent: Combination of rules and LLM
        # - Any future implementation
        #
        # The orchestrator doesn't care - it just calls agent.decide(context)
        result = agent.decide(context)
        
        # ============================================================
        # STEP 5: Validate Output
        # ============================================================
        validate_agent_output(result)
        
        # ============================================================
        # STEP 6: Log Action
        # ============================================================
        log_agent_action(
            spark=spark,
            entity_type="inventory",
            entity_id=product_key,
            action_type=result["action"],
            recommendation_reason=result["reasoning"],
            action_status="PENDING"
        )
        
        # ============================================================
        # STEP 7: Complete Run
        # ============================================================
        execution_duration_ms = (time.time() - start_time) * 1000
        finish_run(
            spark=spark,
            run_id=run_id,
            status="SUCCESS",
            execution_duration_ms=execution_duration_ms
        )
        
        return result
        
    except Exception as e:
        # Log failure
        if run_id:
            execution_duration_ms = (time.time() - start_time) * 1000
            finish_run(
                spark=spark,
                run_id=run_id,
                status="FAILED",
                execution_duration_ms=execution_duration_ms,
                error_message=str(e)
            )
        raise
