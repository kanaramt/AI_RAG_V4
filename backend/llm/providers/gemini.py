import os
import httpx
from typing import Any, AsyncGenerator

from llm.config import LLMConfig
from llm.providers.base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini LLM Provider supporting official Gemini 2.5, 2.0, and 1.5 models.
    Supports official Google Generative AI SDK with automatic REST API fallback.
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self.model = config.model or "gemini-2.5-flash"
        
        # Resolve key from config, os.environ, or .env
        api_k = config.api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_k:
            try:
                from pathlib import Path
                from dotenv import dotenv_values
                env_file = Path(__file__).resolve().parent.parent.parent.parent / ".env"
                if env_file.exists():
                    env_dict = dotenv_values(env_file)
                    api_k = env_dict.get("GEMINI_API_KEY") or env_dict.get("GOOGLE_API_KEY")
            except Exception:
                pass
        self.api_key = api_k

    async def _chat_rest(self, messages: list[dict[str, str]], temperature: float) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        params = {"key": self.api_key}
        
        contents = []
        system_instruction = None
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "system":
                system_instruction = {"parts": [{"text": content}]}
            else:
                contents.append({
                    "role": "user" if role == "user" else "model",
                    "parts": [{"text": content}]
                })
        
        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {"temperature": temperature}
        }
        if system_instruction:
            payload["systemInstruction"] = system_instruction

        print(f"[GEMINI REST] Calling model={self.model}")

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                url,
                params=params,
                json=payload
            )

            print(f"[GEMINI REST] Status Code={resp.status_code}")
    
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API error ({resp.status_code}): {resp.text}")
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    async def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY is not set. Please configure your key in Settings.")

        temp = kwargs.get("temperature", self.config.temperature or 0.2)

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            system_instruction = None
            gemini_contents = []
            for msg in messages:
                role = msg.get("role")
                content = msg.get("content", "")
                if role == "system":
                    system_instruction = content
                else:
                    gemini_contents.append({
                        "role": "user" if role == "user" else "model",
                        "parts": [content]
                    })

            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=system_instruction
            )
            
            response = await model.generate_content_async(
                contents=gemini_contents,
                generation_config=genai.types.GenerationConfig(temperature=temp)
            )
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"[Gemini SDK Note]: {e}. Falling back to Gemini REST API endpoint...")

        # Fallback to direct HTTP REST API
        return await self._chat_rest(messages, temp)

    async def stream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        full_text = await self.chat(messages, **kwargs)
        yield full_text

    async def health_check(self) -> bool:
        return bool(self.api_key)
