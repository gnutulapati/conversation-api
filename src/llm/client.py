import httpx
import json
import logging
from typing import AsyncGenerator, List, Dict, Any, Optional
from src.config.settings import settings

logger = logging.getLogger(__name__)

class LLMClient:
    async def stream_chat(
        self, 
        messages: List[Dict[str, str]], 
        model: str, 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        raise NotImplementedError

class GroqClient(LLMClient):
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        if not self.api_key:
            logger.warning("GROQ_API_KEY is not set. LLM features will not work.")

    async def stream_chat(
        self, 
        messages: List[Dict[str, str]], 
        model: str, 
        temperature: float = 0.7, 
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Yields chunks of the response from Groq API.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "temperature": temperature
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient() as client:
            try:
                async with client.stream("POST", self.base_url, headers=headers, json=payload, timeout=60.0) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        logger.error(f"Groq API Error: {response.status_code} - {error_text}")
                        yield {"error": f"Provider returned {response.status_code}"}
                        return

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                delta = data["choices"][0]["delta"]
                                content = delta.get("content", "")
                                if content:
                                    yield {"content": content, "finish_reason": None}
                                finish_reason = data["choices"][0].get("finish_reason")
                                if finish_reason:
                                     yield {"content": "", "finish_reason": finish_reason}
                                     
                            except json.JSONDecodeError:
                                continue
            except httpx.RequestError as e:
                logger.error(f"Request error: {e}")
                yield {"error": str(e)}

# Factory to get client
def get_llm_client() -> LLMClient:
    # We can switch providers here based on config or model name
    return GroqClient()
