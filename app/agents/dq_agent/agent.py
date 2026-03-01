from google.adk.agents import Agent
from app.tools.dq_tools import list_catalogs, list_schemas, list_tables, execute_sql, invoke_genie_agent, run_dqx_checks
import os

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.0-flash")
RUN_MODE = os.getenv("RUN_MODE", "local")

def create_dq_agent() -> Agent:
    """
    Creates the main Data Quality Agent with a dynamically selected toolset
    and context-aware instructions based on the current run mode.
    """
    
    # Define toolsets based on run mode
    base_tools = [list_catalogs, list_schemas, list_tables, execute_sql]
    databricks_tools = [invoke_genie_agent, run_dqx_checks]
    
    tools = base_tools
    if RUN_MODE == "databricks":
        tools.extend(databricks_tools)

    # Create dynamic instructions
    if RUN_MODE == "databricks":
        db_context = "You are connected to a Databricks environment. You have access to specialized tools like `invoke_genie_agent`."
    else:
        db_context = "You are in 'local' mode, connected to a SQLite database. Databricks-specific tools are disabled."

    # A single, powerful agent instead of sub-agents
    dq_agent = Agent(
        name="dq_agent",
        model=MODEL_NAME,
        instruction=f"""
        You are a powerful and versatile database assistant.
        {db_context}

        **Your Capabilities:**
        1.  **Database Exploration:** You can list catalogs, schemas, and tables.
        2.  **Data Quality Analysis:** You can run complex data quality checks by planning, writing SQL, and executing it.

        **PRIORITY 1: Fulfill the User's Request Directly.**
        - If the user asks to "list", "show", "find", or "what are" the tables, schemas, etc., you MUST use your exploration tools (`list_tables`, `list_schemas`) to answer immediately.
        - Do not ask for clarification if the request is for exploration. Just explore.

        ---
        **EXAMPLE:**
        **User:** "Show me all the tables."
        **YOU (Internal Thought):** The user wants to list tables. I will use the `list_tables` tool.
        **YOU (Tool Call):** `list_tables(catalog='main', schema='public')`
        ---

        **PRIORITY 2: Perform Data Quality Checks.**
        - Only when the user asks for a "check", "validation", or "quality report", should you begin the multi-step DQ process.
        - For DQ checks, you must:
            1.  **Plan:** Think step-by-step about the required checks.
            2.  **Generate SQL:** Write the necessary SQL queries.
            3.  **Execute:** Use the `execute_sql` tool to run the queries.
            4.  **Report:** Summarize the findings for the user.
        """,
        tools=tools,
    )
    
    return dq_agent

agent = create_dq_agent()
root_agent = agent
