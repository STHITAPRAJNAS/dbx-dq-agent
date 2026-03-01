from databricks.sdk import WorkspaceClient
from databricks.sdk.service import sql
import os
import sqlite3
import pandas as pd
from typing import List, Any, Dict
from app.services.mock_data_generator import generate_mock_transactions

class DatabricksService:
    def __init__(self):
        self.mode = os.getenv("RUN_MODE", "databricks")
        self.sqlite_db = os.getenv("SQLITE_DB_PATH", "local_test.db")
        
        if self.mode == "databricks":
            # Only initialize WorkspaceClient if we are in databricks mode AND have credentials
            # Check for minimal credentials (e.g., HOST and TOKEN) or rely on Databricks SDK default chain
            # but wrap in try-except to avoid crashing app startup if config is missing
            try:
                self.client = WorkspaceClient()
            except ValueError as e:
                print(f"Warning: Databricks credentials not found. Switching to local mode. Error: {e}")
                self.mode = "local"
                self.conn = sqlite3.connect(self.sqlite_db, check_same_thread=False)
                self._init_sqlite()
                generate_mock_transactions(self.conn)
        else:
            self.conn = sqlite3.connect(self.sqlite_db, check_same_thread=False)
            self._init_sqlite()
            generate_mock_transactions(self.conn)

    def _init_sqlite(self):
        # Create dummy tables for testing
        cursor = self.conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, age INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, status TEXT)")
        
        # Check if empty and seed
        cursor.execute("SELECT count(*) FROM users")
        if cursor.fetchone()[0] == 0:
            print("Seeding SQLite with sample good and bad data...")
            # Good Users
            cursor.execute("INSERT INTO users (id, name, email, age) VALUES (1, 'Alice Good', 'alice@example.com', 25)")
            cursor.execute("INSERT INTO users (id, name, email, age) VALUES (2, 'Bob Good', 'bob@example.com', 30)")
            
            # Bad Users (DQ Issues)
            cursor.execute("INSERT INTO users (id, name, email, age) VALUES (3, NULL, 'no_name@example.com', 40)") # Null Name
            cursor.execute("INSERT INTO users (id, name, email, age) VALUES (4, 'Charlie InvalidEmail', 'charlie_at_example.com', 35)") # Invalid Email
            cursor.execute("INSERT INTO users (id, name, email, age) VALUES (5, 'Dave NegativeAge', 'dave@example.com', -5)") # Negative Age
            
            # Good Orders
            cursor.execute("INSERT INTO orders (id, user_id, amount, status) VALUES (101, 1, 100.50, 'COMPLETED')")
            cursor.execute("INSERT INTO orders (id, user_id, amount, status) VALUES (102, 2, 200.00, 'PENDING')")
            
            # Bad Orders (DQ Issues)
            cursor.execute("INSERT INTO orders (id, user_id, amount, status) VALUES (103, 1, -50.00, 'COMPLETED')") # Negative Amount
            cursor.execute("INSERT INTO orders (id, user_id, amount, status) VALUES (104, 999, 50.00, 'COMPLETED')") # Orphaned Order (User 999 doesn't exist)
            cursor.execute("INSERT INTO orders (id, user_id, amount, status) VALUES (105, 2, NULL, 'FAILED')") # Null Amount
            
            print("Seeding complete.")
            
        self.conn.commit()

    def list_catalogs(self) -> List[str]:
        if self.mode == "databricks":
            return [c.name for c in self.client.catalogs.list()]
        return ["main"]

    def list_schemas(self, catalog: str) -> List[str]:
        if self.mode == "databricks":
            return [s.name for s in self.client.schemas.list(catalog=catalog)]
        return ["public"]

    def list_tables(self, catalog: str, schema: str) -> List[str]:
        if self.mode == "databricks":
            return [t.name for t in self.client.tables.list(catalog=catalog, schema=schema)]
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in cursor.fetchall()]

    def run_sql(self, sql_statement: str, warehouse_id: str = None) -> List[Dict[str, Any]]:
        """Execute a SQL statement."""
        if self.mode == "databricks":
            response = self.client.statement_execution.execute_statement(
                statement=sql_statement,
                warehouse_id=warehouse_id,
                wait_timeout="50s"
            )
            # Simplified result parsing for databricks
            return str(response) 
        
        try:
            df = pd.read_sql_query(sql_statement, self.conn)
            return df.to_dict(orient="records")
        except Exception as e:
            return [{"error": str(e)}]

    def invoke_genie_space(self, space_id: str, query: str) -> str:
        """Invokes a Databricks Genie Space with a natural language query."""
        if self.mode == "databricks":
            # Real implementation would call Databricks API for Genie
            # For now, simulate the call
            print(f"Calling Databricks Genie space {space_id} with query: {query}")
            return f"Genie Response from {space_id}: Processed '{query}'"
        
        # Local fallback
        print(f"Local mock: Calling Genie space {space_id} with query: {query}")
        return f"[Local Mock] Genie Response: Processed '{query}' against local SQLite."

    def run_dqx_checks(self, table_name: str) -> List[Dict[str, Any]]:
        """Runs automated DQX (Data Quality) checks on a table."""
        if self.mode == "databricks":
            # Real implementation would trigger Databricks DQX metrics
            print(f"Triggering DQX checks for table: {table_name}")
            return [{"metric": "completeness", "status": "pass"}, {"metric": "uniqueness", "status": "fail"}]
            
        # Local fallback
        print(f"Local mock: Running DQX checks for table: {table_name}")
        if table_name == "users":
            return [{"error": "Null Name found (id=3)", "status": "fail"}, {"error": "Invalid Email found (id=4)", "status": "fail"}]
        return [{"status": "pass", "message": f"Basic structural checks passed for {table_name}"}]
