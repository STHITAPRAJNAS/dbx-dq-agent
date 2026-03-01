# DBX Data Quality Agent

An intelligent, multi-agent Data Quality (DQ) framework built with **Google ADK**, **FastAPI**, and **Databricks**. It supports **Agent-to-Agent (A2A)** communication and the **AG UI Protocol**.

## 🚀 Features

*   **Multi-Agent Architecture**:
    *   **Planning Agent**: Analyzes requests and identifies schemas/tables.
    *   **Coding Agent**: Generates SQL for Databricks or SQLite.
    *   **Execution Agent**: Runs queries and reports results.
*   **Databricks & Local Support**:
    *   Seamlessly switches between a real Databricks workspace and a local SQLite fallback.
    *   Auto-seeds local DB with sample "good" and "bad" data for testing.
*   **Modern Agent Protocols**:
    *   **A2A (Agent-to-Agent)**: Exposes agent capabilities via standard RPC for other agents to consume.
    *   **AG UI Protocol**: Provides a rich, standardized interface for frontend applications.
*   **Google ADK Integration**: Built using the Google Agent Development Kit for robust session management and tool execution.

## 🏗 Architecture Decision Records (ADR)

### 1. Framework Selection: Google ADK & FastAPI
*   **Context**: We needed a Python-based agent framework that supports structured tools, history management, and easy API exposure.
*   **Decision**: Use **Google ADK** (Agent Development Kit) wrapped in **FastAPI**.
*   **Rationale**: ADK provides built-in patterns for multi-agent orchestration (sub-agents) and integrates well with `google-generativeai`. FastAPI allows us to serve both A2A and AG UI endpoints from a single process.

### 2. Dual Protocol Support
*   **Context**: The agent needs to be usable by humans (via UI) and other agents (via API).
*   **Decision**: Implement both **AG UI** middleware and **A2A** RPC.
*   **Implementation**: 
    *   Used `google.adk.cli.fast_api.get_fast_api_app` to bootstrap the A2A endpoints automatically.
    *   Used `add_adk_fastapi_endpoint` to attach the AG UI listener to the same app instance.

### 3. Local/Cloud Hybrid Mode
*   **Context**: Development should not require a live Databricks cluster for every test run.
*   **Decision**: Abstract the data layer via `DatabricksService`.
*   **Mechanism**: If `DATABRICKS_HOST` is missing or `RUN_MODE=local`, the service swaps the backend for a local SQLite file (`local_test.db`). It automatically seeds this DB with sample data (users/orders) containing intentional DQ issues for demonstration.

## 🛠 Local Setup

### Prerequisites
*   Python 3.10+
*   `uv` (recommended) or `pip`
*   A Google Gemini API Key (get one from [Google AI Studio](https://aistudio.google.com/))

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/STHITAPRAJNAS/dbx-dq-agent.git
    cd dbx-dq-agent
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    # OR
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    Copy the example env file and add your key.
    ```bash
    cp .env.example .env
    ```
    Edit `.env`:
    ```ini
    GOOGLE_API_KEY=your_actual_gemini_key_here
    RUN_MODE=local
    ```

### Running the App

Start the server using `uv`:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

*   The local SQLite database will be created and seeded automatically on the first run.

### Testing Endpoints

*   **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
*   **AG UI Endpoint**: `http://localhost:8000/agent` (Connect your AG UI frontend here)
*   **A2A Agent Card**: [http://localhost:8000/a2a/dq_agent/.well-known/agent-card.json](http://localhost:8000/a2a/dq_agent/.well-known/agent-card.json)

### Example Query
Connect a client and ask:
> "Run data quality checks for the users table. Check for null names and invalid ages."

The agent will:
1.  Plan the check.
2.  Generate SQL (e.g., `SELECT * FROM users WHERE name IS NULL`).
3.  Execute it against SQLite (or Databricks).
4.  Report the results.
