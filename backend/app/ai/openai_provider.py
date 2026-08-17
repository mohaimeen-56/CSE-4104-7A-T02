import json
import logging
import httpx
from typing import Dict, Any
from app.ai.provider import AIProvider
from app.ai.grounded_engine import GroundedAIEngine
from app.ai.gemini_provider import SYSTEM_PERSONA
from app.core.config import settings

logger = logging.getLogger("SalesIQ.ai.openai")


class OpenAIProvider(AIProvider):
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"
        self.model = "gpt-4o-mini"
        self.fallback = GroundedAIEngine()

    async def _complete(self, system: str, user: str) -> Any:
        if not self.api_key:
            return None
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "max_tokens": 400,
        }
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["choices"][0]["message"]["content"].strip()
                    return text or None
                if resp.status_code == 401:
                    logger.error("OpenAI rejected the API key (401)")
                elif resp.status_code == 429:
                    logger.warning("OpenAI quota/rate limit exceeded (429)")
                else:
                    logger.error("OpenAI request failed (%s): %s", resp.status_code, resp.text[:300])
        except httpx.TimeoutException:
            logger.error("OpenAI request timed out")
        except Exception:
            logger.exception("Unexpected OpenAI failure")
        return None

    async def generate_insight(self, context_data: Dict[str, Any]) -> str:
        result = await self._complete(
            SYSTEM_PERSONA,
            f"Analyze this structured business data and produce a concise executive summary "
            f"(2-3 paragraphs, BDT ৳ currency, specific action items):\n{json.dumps(context_data, indent=2, default=str)}",
        )
        return result if result else await self.fallback.generate_insight(context_data)

    async def chat_response(self, user_query: str, db_context: Dict[str, Any]) -> str:
        mode = db_context.get("mode", "analytics")
        if mode == "conversation":
            grounding = db_context.get("grounding")
            grounding_text = f"\nRelevant live figures (use only if helpful): {json.dumps(grounding, default=str)}" if grounding else ""
            user_msg = f"User: {user_query}{grounding_text}"
        else:
            user_msg = (
                f"Query: {user_query}\n"
                f"Structured database context (the ONLY facts you may reference): {json.dumps(db_context.get('data', {}), default=str)}"
            )
        result = await self._complete(SYSTEM_PERSONA, user_msg)
        return result if result else await self.fallback.chat_response(user_query, db_context)
