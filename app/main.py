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
from google.adk.sessions.in_memory_session_service import InMemorySessionService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.main")

# Initialize ADK Session Service for Local
# Using Google ADK's native InMemorySessionService
session_service = InMemorySessionService()

# Setup App with Google ADK CLI utility
# This sets up A2A routes for agents found in 'app/agents'
# We pass the session_service instance to ensure get_fast_api_app uses it
app = get_fast_api_app(
    agents_dir="app/agents",
    session_service_uri="memory://", # ADK uses 'memory://' for InMemorySessionService
    web=True, 
    a2a=True
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
# We import the same agent instance and pass the session service
ag_ui_agent = ADKAgent(
    adk_agent=dq_root_agent,
    app_name="dq-agent-app",
    user_id="default-user",
    session_service=session_service
)

# Add endpoint for AG UI (e.g., /chat or /agent)
add_adk_fastapi_endpoint(app, ag_ui_agent, path="/agent")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
