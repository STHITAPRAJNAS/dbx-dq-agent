from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class AgentRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    protocol: Optional[str] = Field(default="a2a", description="Protocol: 'a2a' or 'agui'")

class AgentResponse(BaseModel):
    response: str
    metadata: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None

class DqCheckResult(BaseModel):
    check_name: str
    status: str  # "pass", "fail", "error"
    details: str
    timestamp: str

class DqCheckRequest(BaseModel):
    catalog: str
    schema_name: str
    table_name: Optional[str] = None
    check_type: str = "schema"  # "schema", "table", "data"
