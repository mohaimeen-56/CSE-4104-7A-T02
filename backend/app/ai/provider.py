from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class AIProvider(ABC):
    @abstractmethod
    async def generate_insight(self, context_data: Dict[str, Any]) -> str:
        """Generate structured business summary and narrative insights based on sales metrics."""
        pass

    @abstractmethod
    async def chat_response(self, user_query: str, db_context: Dict[str, Any]) -> str:
        """Generate a natural language response for a conversational query grounded in database context."""
        pass
