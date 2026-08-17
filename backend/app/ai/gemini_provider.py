import asyncio
import json
import logging
from typing import Dict, Any, Optional
from google import genai
from google.genai import types, errors
from app.ai.provider import AIProvider
from app.ai.grounded_engine import GroundedAIEngine
from app.core.config import settings

logger = logging.getLogger("SalesIQ.ai.gemini")

SYSTEM_PERSONA = (
    "You are SalesIQ AI, a professional, concise, friendly business assistant embedded in a sales "
    "analytics dashboard for a Bangladesh-based business (currency BDT, symbol ৳). "
    "You handle two kinds of requests: (1) normal conversation — greetings, thanks, questions about "
    "what you can do, and plain-English explanations of dashboard/business metrics; and (2) questions "
    "about the business's real sales data, whose facts are given to you as structured JSON context. "
    "For (2), you must answer using ONLY the numbers in that context and never invent or estimate a "
    "figure that isn't present there. Keep replies short (2-4 sentences unless more detail is clearly "
    "needed), use **bold** for key figures, and never sound robotic or say things like 'Invalid query.' "
    "If the provided context has no relevant data, say so plainly instead of guessing."
)


class GeminiProvider(AIProvider):
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL or "gemini-flash-latest"
        self.fallback = GroundedAIEngine()
        self._client: Optional[genai.Client] = None
        if self.api_key:
            try:
                self._client = genai.Client(
                    api_key=self.api_key,
                    http_options=types.HttpOptions(timeout=12000),  # ms
                )
            except Exception:
                logger.exception("Failed to initialize Gemini client")
                self._client = None
        else:
            logger.warning("GEMINI_API_KEY not set; Gemini provider will use the offline fallback engine.")

    async def _generate(self, prompt: str) -> Optional[str]:
        if not self._client:
            return None
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(self._client.models.generate_content, model=self.model, contents=prompt),
                timeout=15.0,
            )
            text = (getattr(response, "text", None) or "").strip()
            if not text:
                logger.warning("Gemini returned an empty response for model %s", self.model)
                return None
            return text
        except asyncio.TimeoutError:
            logger.error("Gemini request timed out after 15s (model=%s)", self.model)
            return None
        except errors.ClientError as e:
            code = getattr(e, "code", None)
            if code == 400:
                logger.error("Gemini rejected the request (invalid API key or bad request): %s", e)
            elif code == 403:
                logger.error("Gemini permission denied (check API key restrictions/billing): %s", e)
            elif code == 429:
                logger.warning("Gemini quota/rate limit exceeded: %s", e)
            else:
                logger.error("Gemini client error (%s): %s", code, e)
            return None
        except errors.ServerError as e:
            logger.error("Gemini server-side error: %s", e)
            return None
        except Exception:
            logger.exception("Unexpected Gemini failure")
            return None

    async def generate_insight(self, context_data: Dict[str, Any]) -> str:
        prompt = (
            f"{SYSTEM_PERSONA}\n\n"
            "Analyze this structured business data and produce a concise, professional executive summary "
            "(2-3 paragraphs, highlight percentages, revenue in BDT ৳, and specific action items):\n"
            f"{json.dumps(context_data, indent=2, default=str)}"
        )
        result = await self._generate(prompt)
        return result if result else await self.fallback.generate_insight(context_data)

    async def chat_response(self, user_query: str, db_context: Dict[str, Any]) -> str:
        mode = db_context.get("mode", "analytics")

        if mode == "conversation":
            history = db_context.get("history", [])
            grounding = db_context.get("grounding")
            history_text = ""
            if history:
                lines = [f"User: {t['query']}\nSalesIQ AI: {t['response']}" for t in history[-6:] if t.get("response")]
                if lines:
                    history_text = "Recent conversation for context:\n" + "\n\n".join(lines) + "\n\n"
            grounding_text = (
                f"Relevant live business figures (mention only if naturally helpful, don't force them in): "
                f"{json.dumps(grounding, default=str)}\n\n" if grounding else ""
            )
            prompt = f"{SYSTEM_PERSONA}\n\n{history_text}{grounding_text}User: {user_query}\nSalesIQ AI:"
        else:
            prompt = (
                f"{SYSTEM_PERSONA}\n\n"
                f"User Query: {user_query}\n"
                f"Structured database context (the ONLY facts you may reference): "
                f"{json.dumps(db_context.get('data', {}), default=str)}\n"
                "Answer concisely and factually using ONLY the provided context. Use bold and BDT currency (৳)."
            )

        result = await self._generate(prompt)
        return result if result else await self.fallback.chat_response(user_query, db_context)
