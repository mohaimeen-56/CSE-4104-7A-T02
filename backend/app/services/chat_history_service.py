import uuid
from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.models.ai_log import AILog


class ChatHistoryService:
    """Reads/writes conversation turns from ai_logs so the chatbot has real multi-turn
    memory within a session, instead of treating every message in isolation."""

    @staticmethod
    def new_conversation_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def get_recent_turns(db: Session, conversation_id: Optional[str], limit: int = 6) -> List[Dict]:
        if not conversation_id:
            return []
        rows = (
            db.query(AILog)
            .filter(AILog.conversation_id == conversation_id)
            .order_by(AILog.created_at.desc())
            .limit(limit)
            .all()
        )
        rows.reverse()
        return [{"query": r.query, "response": r.response, "intent": r.intent, "route": r.route} for r in rows]

    @staticmethod
    def get_last_analytics_intent(db: Session, conversation_id: Optional[str]) -> Optional[str]:
        if not conversation_id:
            return None
        row = (
            db.query(AILog)
            .filter(AILog.conversation_id == conversation_id, AILog.route == "analytics", AILog.intent.isnot(None))
            .order_by(AILog.created_at.desc())
            .first()
        )
        return row.intent if row else None

    @staticmethod
    def log_turn(
        db: Session,
        user_id: int,
        conversation_id: str,
        query: str,
        response: str,
        route: str,
        intent: Optional[str],
    ) -> None:
        db.add(AILog(
            user_id=user_id, conversation_id=conversation_id, query=query, response=response,
            route=route, intent=intent, created_at=datetime.utcnow(),
        ))
        db.commit()
