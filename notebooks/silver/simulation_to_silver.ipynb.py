# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# DBTITLE 1,Setup and Imports
import sys
import uuid
from datetime import datetime
from pyspark.sql import functions as F

# Add simulation directory to path
sys.path.append('/Workspace/Users/aaryan.shrivastav1403@gmail.com/wipfli-agentic-ai/src/simulation')

print("✓ Imports complete")

# COMMAND ----------

# DBTITLE 1,Load Simulation Runner
# MAGIC %run /Users/aaryan.shrivastav1403@gmail.com/wipfli-agentic-ai/src/simulation/simulator_runner

# COMMAND ----------

# DBTITLE 1,Load Bronze Sales Data
# Load sales data from bronze - this will be used as input for simulation
from pyspark.sql import functions as F

# Read the sales_raw table and unpivot to get sales by product, store, and date
sales_df = spark.table("agentdb.bronze.sales_raw")

# Extract product_id from item_id (e.g., "HOBBIES_1_001" -> extract numeric ID)
# For now, we'll create a simplified sales DataFrame for the simulation
# The simulation needs: product_id, store_id, sales_qty

# Convert store_id from string (e.g., "CA_1") to numeric
# Extract numeric part from store_id
from pyspark.sql.types import IntegerType

sales_df = sales_df.withColumn(
    "store_id_num",
    F.regexp_extract(F.col("store_id"), r"(\d+)", 1).cast(IntegerType())
)

# Create a product_id by hashing the item_id (simple approach)
sales_df = sales_df.withColumn(
    "product_id",
    F.abs(F.hash(F.col("item_id")) % 1000) + 1
)

# Unpivot the daily sales columns (d_1 to d_1913) - take a recent subset for simulation
# For demonstration, we'll aggregate the last 30 days of sales
day_cols = [f"d_{i}" for i in range(1884, 1914)]  # Last 30 days

# Calculate average daily sales over the period
sales_df = sales_df.withColumn(
    "sales_qty",
    sum([F.coalesce(F.col(c), F.lit(0)) for c in day_cols]) / len(day_cols)
)

# Select and rename columns for simulation
sales_for_sim = sales_df.select(
    F.col("product_id"),
    F.col("store_id_num").alias("store_id"),
    F.col("sales_qty")
).toPandas()

print(f"Loaded {len(sales_for_sim)} sales records for simulation")
print(f"Products: {sales_for_sim['product_id'].nunique()}, Stores: {sales_for_sim['store_id'].nunique()}")

# COMMAND ----------

# DBTITLE 1,Create Products DataFrame
# Create a products DataFrame from the sales data
import pandas as pd

products_df = sales_for_sim[['product_id']].drop_duplicates().copy()
products_df['supplier_id'] = None  # Will be assigned by simulation

print(f"Created {len(products_df)} products for simulation")

# COMMAND ----------

# DBTITLE 1,Run Simulation
# Initialize and run the simulation
print("\n" + "="*50)
print("RUNNING SUPPLY CHAIN SIMULATION")
print("="*50)

runner = SimulationRunner()

results = runner.run(
    products_df=products_df,
    sales_df=sales_for_sim
)

print("\n" + "="*50)
print("SIMULATION COMPLETE")
print("="*50)
print(f"\nGenerated:")
print(f"  - Suppliers: {len(results['suppliers'])}")
print(f"  - Distribution Centers: {len(results['distribution_centers'])}")
print(f"  - Products with Suppliers: {len(results['products'])}")
print(f"  - Store Inventory Records: {len(results['store_inventory'])}")
print(f"  - DC Inventory Records: {len(results['dc_inventory'])}")
print(f"  - Purchase Orders: {len(results['purchase_orders'])}")
print(f"  - Disruptions: {len(results['disruptions'])}")

# COMMAND ----------

# DBTITLE 1,Write Suppliers to Silver
# Transform and write suppliers to silver.supplier
print("\nWriting suppliers to agentdb.silver.supplier...")

suppliers_spark = spark.createDataFrame(results['suppliers'])

# Drop supplier_id as it's an identity column in the target table
suppliers_spark = suppliers_spark.select(
    "supplier_code",
    "supplier_name",
    "supplier_category",
    F.col("lead_time_days").cast("int"),
    F.col("risk_score").cast("double"),
    "supplier_status",
    F.col("effective_start_date").cast("timestamp"),
    F.col("effective_end_date").cast("timestamp"),
    "is_current",
    F.col("created_at").cast("timestamp"),
    F.col("updated_at").cast("timestamp"),
    "change_type",
    "is_deleted"
)

# Write to silver table
suppliers_spark.write.mode("overwrite").saveAsTable("agentdb.silver.supplier")

print(f"✓ Inserted {len(results['suppliers'])} suppliers")

# COMMAND ----------

# DBTITLE 1,Write Distribution Centers to Silver
# Transform and write distribution centers to silver.distribution_center
print("\nWriting distribution centers to agentdb.silver.distribution_center...")

dcs_spark = spark.createDataFrame(results['distribution_centers'])

# Add missing columns and drop dc_id (identity column)
# Map state_id from dc_code (e.g., "DC_EAST" -> "EAST")
dcs_spark = dcs_spark.withColumn(
    "state_id",
    F.regexp_replace(F.col("dc_code"), "DC_", "")
)

dcs_spark = dcs_spark.select(
    "dc_code",
    "dc_name",
    "state_id",
    F.col("capacity_units").cast("long"),
    F.col("effective_start_date").cast("timestamp"),
    F.col("effective_end_date").cast("timestamp"),
    "is_current",
    F.col("created_at").cast("timestamp"),
    F.col("updated_at").cast("timestamp"),
    "change_type",
    "is_deleted"
)

# Write to silver table
dcs_spark.write.mode("overwrite").saveAsTable("agentdb.silver.distribution_center")

print(f"✓ Inserted {len(results['distribution_centers'])} distribution centers")

# COMMAND ----------

# DBTITLE 1,Write Purchase Orders to Silver
# Transform and write purchase orders to silver.purchase_order
print("\nWriting purchase orders to agentdb.silver.purchase_order...")

# Generate batch_id for this load
batch_id = str(uuid.uuid4())

if len(results['purchase_orders']) == 0:
    print("⚠ No purchase orders generated (no inventory below reorder point)")
else:
    pos_spark = spark.createDataFrame(results['purchase_orders'])
    
    # Add dc_id (randomly assign to one of the 4 DCs for now)
    pos_spark = pos_spark.withColumn(
        "dc_id",
        (F.rand() * 4).cast("int") + 1
    )
    
    # Add load_batch_id
    pos_spark = pos_spark.withColumn("load_batch_id", F.lit(batch_id))
    
    # Drop purchase_order_id (identity column) and select columns
    pos_spark = pos_spark.select(
        "po_number",
        F.col("supplier_id").cast("long"),
        F.col("dc_id").cast("long"),
        F.col("product_id").cast("long"),
        F.col("ordered_qty").cast("int"),
        F.col("received_qty").cast("int"),
        F.col("lead_time_days").cast("int"),
        F.col("order_date").cast("date"),
        F.col("expected_delivery_date").cast("date"),
        F.col("actual_delivery_date").cast("date"),
        "po_status",
        F.col("created_at").cast("timestamp"),
        F.col("updated_at").cast("timestamp"),
        "load_batch_id"
    )
    
    # Write to silver table
    pos_spark.write.mode("overwrite").saveAsTable("agentdb.silver.purchase_order")
    
    print(f"✓ Inserted {len(results['purchase_orders'])} purchase orders")

# COMMAND ----------

# DBTITLE 1,Write Store Inventory to Silver
# Transform and write store inventory to silver.store_inventory_snapshot
print("\nWriting store inventory to agentdb.silver.store_inventory_snapshot...")

store_inv_spark = spark.createDataFrame(results['store_inventory'])

# Add load_batch_id
store_inv_spark = store_inv_spark.withColumn("load_batch_id", F.lit(batch_id))

# Drop inventory_snapshot_id (identity column) and select columns
store_inv_spark = store_inv_spark.select(
    F.col("product_id").cast("long"),
    F.col("store_id").cast("long"),
    F.col("snapshot_date").cast("date"),
    F.col("inventory_qty").cast("int"),
    F.col("days_of_cover").cast("double"),
    F.col("created_at").cast("timestamp"),
    "load_batch_id"
)

# Write to silver table
store_inv_spark.write.mode("overwrite").saveAsTable("agentdb.silver.store_inventory_snapshot")

print(f"✓ Inserted {len(results['store_inventory'])} store inventory records")

# COMMAND ----------

# DBTITLE 1,Write DC Inventory to Silver
# Transform and write DC inventory to silver.dc_inventory_snapshot
print("\nWriting DC inventory to agentdb.silver.dc_inventory_snapshot...")

dc_inv_spark = spark.createDataFrame(results['dc_inventory'])

# Add load_batch_id
dc_inv_spark = dc_inv_spark.withColumn("load_batch_id", F.lit(batch_id))

# Drop dc_inventory_snapshot_id (identity column) and select columns
dc_inv_spark = dc_inv_spark.select(
    F.col("product_id").cast("long"),
    F.col("dc_id").cast("long"),
    F.col("snapshot_date").cast("date"),
    F.col("inventory_qty").cast("int"),
    F.col("created_at").cast("timestamp"),
    "load_batch_id"
)

# Write to silver table
dc_inv_spark.write.mode("overwrite").saveAsTable("agentdb.silver.dc_inventory_snapshot")

print(f"✓ Inserted {len(results['dc_inventory'])} DC inventory records")

# COMMAND ----------

# DBTITLE 1,Write Supplier Disruptions to Silver
# Transform and write disruptions to silver.supplier_disruption
print("\nWriting supplier disruptions to agentdb.silver.supplier_disruption...")

disruptions_spark = spark.createDataFrame(results['disruptions'])

# Add load_batch_id
disruptions_spark = disruptions_spark.withColumn("load_batch_id", F.lit(batch_id))

# Drop disruption_id (identity column) and select columns
disruptions_spark = disruptions_spark.select(
    F.col("supplier_id").cast("long"),
    "disruption_type",
    F.col("disruption_start_date").cast("date"),
    F.col("disruption_end_date").cast("date"),
    F.col("severity_score").cast("double"),
    F.col("delay_days").cast("int"),
    "disruption_status",
    F.col("created_at").cast("timestamp"),
    "load_batch_id"
)

# Write to silver table
disruptions_spark.write.mode("overwrite").saveAsTable("agentdb.silver.supplier_disruption")

print(f"✓ Inserted {len(results['disruptions'])} supplier disruptions")

# COMMAND ----------

# DBTITLE 1,Summary and Verification
# Summary
print("\n" + "="*50)
print("DATA LOAD SUMMARY")
print("="*50)
print(f"Batch ID: {batch_id}")
print(f"\nRecords written to silver layer:")
print(f"  - silver.supplier: {len(results['suppliers'])}")
print(f"  - silver.distribution_center: {len(results['distribution_centers'])}")
print(f"  - silver.purchase_order: {len(results['purchase_orders'])}")
print(f"  - silver.store_inventory_snapshot: {len(results['store_inventory'])}")
print(f"  - silver.dc_inventory_snapshot: {len(results['dc_inventory'])}")
print(f"  - silver.supplier_disruption: {len(results['disruptions'])}")
print("\n✓ All data successfully loaded to silver layer!")

# Quick verification queries
print("\nVerification:")
print(f"  - Suppliers in silver: {spark.table('agentdb.silver.supplier').count()}")
print(f"  - DCs in silver: {spark.table('agentdb.silver.distribution_center').count()}")
print(f"  - Purchase orders in silver: {spark.table('agentdb.silver.purchase_order').count()}")
