from typing import Dict, Any, Optional
import uuid

class SessionService:
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {
            "history": [],
            "context": {},
            "metadata": metadata or {}
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._sessions.get(session_id)

    def update_context(self, session_id: str, context: Dict[str, Any]):
        if session_id in self._sessions:
            self._sessions[session_id]["context"].update(context)

    def add_history(self, session_id: str, message: Dict[str, str]):
        if session_id in self._sessions:
            self._sessions[session_id]["history"].append(message)
            
    def clear_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]
