import os
from dotenv import load_dotenv

# Load env vars before importing agents that might depend on them
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from google.adk.cli.fast_api import get_fast_api_app
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
import uvicorn
import logging
from app.agents.dq_agent.agent import agent as dq_root_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.main")

# Setup App with Google ADK CLI utility
# This sets up A2A routes for agents found in 'app/agents'
# Note: 'web' parameter enables developer UI and A2A services
app = get_fast_api_app(
    agents_dir="app/agents",
    web=True, # Set to True if you want the ADK Web UI dev endpoint
    a2a=True   # Enable A2A capabilities
)

# Add Middleware
# We must add it to the app returned by get_fast_api_app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

# 1. AG UI Endpoint
# Wrap the ADK agent with AG UI Middleware
# We import the same agent instance that get_fast_api_app (via AgentLoader) should use
ag_ui_agent = ADKAgent(
    adk_agent=dq_root_agent,
    app_name="dq-agent-app",
    user_id="default-user"
)

# Add endpoint for AG UI (e.g., /chat or /agent)
add_adk_fastapi_endpoint(app, ag_ui_agent, path="/agent")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
