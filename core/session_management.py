import uuid
from typing import Dict, Optional
from datetime import datetime, timedelta

class Session:
    def __init__(self, user_id: str, expiration_minutes: int = 30):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(minutes=expiration_minutes)

    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    def create_session(self, user_id: str, expiration_minutes: int = 30) -> Session:
        session = Session(user_id, expiration_minutes)
        self.sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        session = self.sessions.get(session_id)
        if session and not session.is_expired():
            return session
        return None

    def delete_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def cleanup_expired_sessions(self):
        current_time = datetime.now()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if current_time > session.expires_at
        ]
        for session_id in expired_sessions:
            del self.sessions[session_id]

session_manager = SessionManager()