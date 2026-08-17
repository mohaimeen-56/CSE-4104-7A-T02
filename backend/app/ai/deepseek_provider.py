from app.ai.openai_provider import OpenAIProvider
from app.core.config import settings


class DeepSeekProvider(OpenAIProvider):
    """DeepSeek Chat — OpenAI-compatible API, free tier via api.deepseek.com."""

    def __init__(self):
        super().__init__()
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"
