# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# DBTITLE 1,Table Generation Title
# MAGIC %md
# MAGIC # Table Generation from SQL Files
# MAGIC
# MAGIC This notebook executes SQL files from the `database/` directory to create Unity Catalog tables in the `agentdb` catalog.
# MAGIC
# MAGIC **Purpose:**
# MAGIC - Automate table creation by executing SQL scripts organized by schema
# MAGIC - Support schema-based organization (bronze, silver, gold, etc.)
# MAGIC - Create schemas and tables in Unity Catalog for centralized data management
# MAGIC
# MAGIC **Structure:**
# MAGIC - Each folder in `database/` becomes a schema in the `agentdb` catalog
# MAGIC - Each `.sql` file in a folder contains table creation DDL
# MAGIC - Example: `database/bronze/customers.sql` → Executes to create tables in `agentdb.bronze`
# MAGIC
# MAGIC **Process:**
# MAGIC 1. Discover SQL files in the database/ directory organized by schema folders
# MAGIC 2. Create schemas in the agentdb catalog
# MAGIC 3. Execute each SQL file to create tables
# MAGIC 4. Verify table creation across all schemas

# COMMAND ----------

# DBTITLE 1,Import Libraries
import os
from pathlib import Path
import re

# COMMAND ----------

# DBTITLE 1,Configuration Variables
# Configuration
DATABASE_DIR = "../database/"  # Relative path to database directory
CATALOG = "agentdb"  # Unity Catalog name
# Schemas will be derived from folder names in database/

print(f"Configuration:")
print(f"  Database Directory: {DATABASE_DIR}")
print(f"  Catalog: {CATALOG}")
print(f"  Schemas: Auto-detected from folders in {DATABASE_DIR}")
print(f"  SQL Files: Will be executed to create tables")

# COMMAND ----------

# DBTITLE 1,Create Schema
# Create catalog if it doesn't exist
try:
    spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
    print(f"✓ Catalog {CATALOG} is ready")
    print(f"  Schemas will be created from folder structure")
except Exception as e:
    print(f"✗ Error creating catalog: {str(e)}")
    raise

# COMMAND ----------

# DBTITLE 1,Discover Data Files
def discover_sql_files_by_schema(directory):
    """
    Discover all SQL files organized by schema (folder name).
    
    Args:
        directory (str): Path to the database directory
    
    Returns:
        dict: Dictionary mapping schema names to lists of SQL file paths
    """
    schema_files = {}
    
    base_path = Path(directory)
    
    if not base_path.exists():
        print(f"⚠ Directory not found: {directory}")
        return schema_files
    
    # Find all subdirectories (schemas)
    for schema_dir in sorted(base_path.iterdir()):
        if schema_dir.is_dir():
            schema_name = schema_dir.name.lower().replace('-', '_').replace(' ', '_')
            files = []
            
            # Find all SQL files in this schema directory
            for file_path in schema_dir.rglob("*.sql"):
                if file_path.is_file():
                    files.append(file_path)
            
            if files:
                schema_files[schema_name] = sorted(files)
    
    return schema_files

# Test the function
schema_sql_files = discover_sql_files_by_schema(DATABASE_DIR)
print(f"\nDiscovered {len(schema_sql_files)} schema(s) with SQL files:")
for schema, files in schema_sql_files.items():
    print(f"\n  Schema: {schema}")
    for f in files:
        print(f"    - {f.name}")

# COMMAND ----------

# DBTITLE 1,Infer Table Name
def execute_sql_file(file_path, catalog, schema):
    """
    Read and execute a SQL file with proper USE statement.
    
    Args:
        file_path (Path): Path to the SQL file
        catalog (str): Unity Catalog name
        schema (str): Schema name
    
    Returns:
        tuple: (success: bool, message: str, tables_created: list)
    """
    try:
        # Read SQL file
        with open(file_path, 'r') as f:
            sql_content = f.read()
        
        if not sql_content.strip():
            return False, f"Empty SQL file: {file_path.name}", []
        
        # Set the current schema context
        spark.sql(f"USE {catalog}.{schema}")
        
        # Split SQL statements by semicolon
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        tables_created = []
        
        for i, statement in enumerate(statements, 1):
            try:
                # Execute the statement
                spark.sql(statement)
                
                # Try to extract table name from CREATE TABLE statements
                create_match = re.search(r'CREATE\s+(?:OR\s+REPLACE\s+)?(?:TEMPORARY\s+)?TABLE(?:\s+IF\s+NOT\s+EXISTS)?\s+(?:`?([\w.]+)`?)', statement, re.IGNORECASE)
                if create_match:
                    table_name = create_match.group(1).split('.')[-1]  # Get last part if fully qualified
                    tables_created.append(table_name)
                    
            except Exception as e:
                return False, f"Error in statement {i} of {file_path.name}: {str(e)}", tables_created
        
        if tables_created:
            return True, f"Executed {file_path.name} - Created {len(tables_created)} table(s): {', '.join(tables_created)}", tables_created
        else:
            return True, f"Executed {file_path.name} - {len(statements)} statement(s) executed", []
        
    except Exception as e:
        return False, f"Error reading {file_path.name}: {str(e)}", []

# Function is ready to use in main execution
print("\n✓ SQL execution function ready")

# COMMAND ----------

# DBTITLE 1,Create Table from File
# This cell is no longer needed - deleted in favor of execute_sql_file function

# COMMAND ----------

# DBTITLE 1,Main Execution - Create All Tables
# Main execution loop
print("=" * 70)
print("EXECUTING SQL FILES TO CREATE TABLES")
print("=" * 70)

# Discover all SQL files organized by schema
schema_sql_files = discover_sql_files_by_schema(DATABASE_DIR)

if not schema_sql_files:
    print(f"\n⚠ No schemas with SQL files found in {DATABASE_DIR}")
    print("Please create folders in database/ directory and add .sql files.")
    print("\nExpected structure:")
    print("  database/")
    print("    ├── bronze/")
    print("    │   ├── raw_customers.sql")
    print("    │   └── raw_orders.sql")
    print("    ├── silver/")
    print("    │   └── cleaned_data.sql")
    print("    └── gold/")
    print("        └── aggregated_metrics.sql")
else:
    total_files = sum(len(files) for files in schema_sql_files.values())
    print(f"\nFound {len(schema_sql_files)} schema(s) with {total_files} SQL file(s) to process\n")
    
    # Process each schema
    files_executed = 0
    files_failed = 0
    schemas_created = 0
    total_tables_created = 0
    
    for schema_name, sql_files in schema_sql_files.items():
        print("=" * 70)
        print(f"SCHEMA: {CATALOG}.{schema_name}")
        print("=" * 70)
        
        # Create schema
        try:
            spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{schema_name}")
            print(f"✓ Created schema: {CATALOG}.{schema_name}")
            schemas_created += 1
        except Exception as e:
            print(f"✗ Error creating schema {schema_name}: {str(e)}")
            continue
        
        print(f"\nExecuting {len(sql_files)} SQL file(s)...\n")
        
        # Execute each SQL file in this schema
        for i, sql_file in enumerate(sql_files, 1):
            print(f"  [{i}/{len(sql_files)}] {sql_file.name}")
            
            success, message, tables = execute_sql_file(sql_file, CATALOG, schema_name)
            
            if success:
                print(f"    ✓ {message}")
                files_executed += 1
                total_tables_created += len(tables)
            else:
                print(f"    ✗ {message}")
                files_failed += 1
        
        print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Schemas created: {schemas_created}")
    print(f"SQL files executed successfully: {files_executed}")
    print(f"SQL files failed: {files_failed}")
    print(f"Total tables created: {total_tables_created}")
    print("=" * 70)

# COMMAND ----------

# DBTITLE 1,Verify Tables Created
# Verify tables were created
print("\n" + "=" * 70)
print(f"TABLES IN CATALOG: {CATALOG}")
print("=" * 70 + "\n")

try:
    # Get all schemas in the catalog
    schemas_df = spark.sql(f"SHOW SCHEMAS IN {CATALOG}")
    schemas = [row.databaseName for row in schemas_df.collect()]
    
    if not schemas:
        print(f"No schemas found in catalog {CATALOG}")
    else:
        total_tables = 0
        
        for schema in sorted(schemas):
            print(f"\nSchema: {CATALOG}.{schema}")
            print("-" * 50)
            
            try:
                tables_df = spark.sql(f"SHOW TABLES IN {CATALOG}.{schema}")
                tables = tables_df.collect()
                
                if tables:
                    for row in tables:
                        table_name = row.tableName
                        # Get row count for each table
                        try:
                            count_df = spark.sql(f"SELECT COUNT(*) as count FROM {CATALOG}.{schema}.{table_name}")
                            row_count = count_df.collect()[0].count
                            print(f"  • {table_name}: {row_count:,} rows")
                            total_tables += 1
                        except Exception as e:
                            print(f"  • {table_name}: Error getting count ({str(e)})")
                            total_tables += 1
                else:
                    print("  (no tables)")
                    
            except Exception as e:
                print(f"  Error listing tables: {str(e)}")
        
        print("\n" + "=" * 70)
        print(f"Total tables across all schemas: {total_tables}")
        print("=" * 70)
        
except Exception as e:
    print(f"Error listing schemas: {str(e)}")

# COMMAND ----------

# DBTITLE 1,Next Steps
# MAGIC %md
# MAGIC ## Next Steps
# MAGIC
# MAGIC ### Directory Structure
# MAGIC
# MAGIC This notebook executes SQL files from folder names in the `database/` directory:
# MAGIC
# MAGIC ```
# MAGIC database/
# MAGIC ├── bronze/              →  agentdb.bronze schema
# MAGIC │   ├── raw_customers.sql   →  Executed in agentdb.bronze
# MAGIC │   └── raw_orders.sql      →  Executed in agentdb.bronze
# MAGIC ├── silver/              →  agentdb.silver schema
# MAGIC │   └── cleaned_data.sql    →  Executed in agentdb.silver
# MAGIC └── gold/                →  agentdb.gold schema
# MAGIC     └── metrics.sql         →  Executed in agentdb.gold
# MAGIC ```
# MAGIC
# MAGIC ### SQL File Format
# MAGIC
# MAGIC Each SQL file should contain one or more CREATE TABLE statements:
# MAGIC
# MAGIC ```sql
# MAGIC -- Example: database/bronze/customers.sql
# MAGIC CREATE OR REPLACE TABLE customers (
# MAGIC   id BIGINT,
# MAGIC   name STRING,
# MAGIC   email STRING,
# MAGIC   created_at TIMESTAMP
# MAGIC )
# MAGIC USING DELTA;
# MAGIC
# MAGIC -- You can have multiple statements separated by semicolons
# MAGIC CREATE OR REPLACE TABLE orders (
# MAGIC   order_id BIGINT,
# MAGIC   customer_id BIGINT,
# MAGIC   amount DECIMAL(10,2)
# MAGIC )
# MAGIC USING DELTA;
# MAGIC ```
# MAGIC
# MAGIC **Note:** You don't need to specify the full table name (catalog.schema.table) - the notebook automatically sets the context to the correct schema.
# MAGIC
# MAGIC ### Querying the Tables
# MAGIC
# MAGIC You can now query the created tables using:
# MAGIC
# MAGIC ```sql
# MAGIC SELECT * FROM agentdb.<schema_name>.<table_name> LIMIT 10;
# MAGIC ```
# MAGIC
# MAGIC Example:
# MAGIC ```sql
# MAGIC SELECT * FROM agentdb.bronze.customers LIMIT 10;
# MAGIC SELECT * FROM agentdb.silver.cleaned_data LIMIT 10;
# MAGIC ```
# MAGIC
# MAGIC ### Adding More Tables
# MAGIC
# MAGIC To add more schemas and tables:
# MAGIC 1. Create folders in the `database/` directory (folder names become schemas)
# MAGIC 2. Add `.sql` files with CREATE TABLE statements in these folders
# MAGIC 3. Re-run this notebook
# MAGIC 4. Tables will be created or replaced based on your SQL statements
# MAGIC
# MAGIC ### Naming Conventions
# MAGIC
# MAGIC **Schemas (folder names):**
# MAGIC - Converted to lowercase
# MAGIC - Hyphens and spaces replaced with underscores
# MAGIC - Example: `Customer-Data` → `customer_data`
# MAGIC
# MAGIC **Tables:**
# MAGIC - Defined in your SQL files
# MAGIC - Can use any valid table name
# MAGIC - Will be created in the schema matching the folder name
# MAGIC
# MAGIC ### Supported SQL Statements
# MAGIC
# MAGIC - `CREATE TABLE`
# MAGIC - `CREATE OR REPLACE TABLE`
# MAGIC - `CREATE TABLE IF NOT EXISTS`
# MAGIC - Multiple statements per file (separated by semicolons)
# MAGIC - Comments using `--` or `/* */`
# MAGIC
# MAGIC ### Troubleshooting
# MAGIC
# MAGIC If tables aren't created:
# MAGIC - Check that the `database/` directory exists relative to this notebook
# MAGIC - Verify folders exist in `database/` (each folder becomes a schema)
# MAGIC - Ensure files have `.sql` extension
# MAGIC - Verify SQL syntax is correct
# MAGIC - Check that CREATE TABLE statements don't include catalog.schema prefix
# MAGIC - Review error messages in the execution output above
