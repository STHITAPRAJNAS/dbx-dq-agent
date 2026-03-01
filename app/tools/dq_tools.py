from typing import List, Dict, Any
from app.services.databricks_service import DatabricksService

db_service = DatabricksService()

def list_catalogs() -> List[str]:
    """Lists all available catalogs."""
    return db_service.list_catalogs()

def list_schemas(catalog: str) -> List[str]:
    """Lists schemas in a catalog."""
    return db_service.list_schemas(catalog)

def list_tables(catalog: str, schema: str) -> List[str]:
    """Lists tables in a specific schema."""
    return db_service.list_tables(catalog, schema)

def execute_sql(query: str) -> List[Dict[str, Any]]:
    """Executes a SQL query and returns results."""
    return db_service.run_sql(query)

def invoke_genie_agent(query: str, space_id: str = "default-space") -> str:
    """Invokes a Databricks Genie agent to answer natural language questions about data."""
    return db_service.invoke_genie_space(space_id, query)

def run_dqx_checks(table_name: str) -> List[Dict[str, Any]]:
    """Runs automated proactive Data Quality (DQX) checks on a given table."""
    return db_service.run_dqx_checks(table_name)
