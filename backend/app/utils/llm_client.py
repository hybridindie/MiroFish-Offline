"""
LLM Client Wrapper
Unified OpenAI format API calls
Supports Ollama num_ctx parameter to prevent prompt truncation
"""

import json
import os
import re
from typing import Optional, Dict, Any, List
from openai import OpenAI

from ..config import Config
from ..utils.logger import get_logger


logger = get_logger('mirofish.llm_client')


class LLMClient:
    """LLM Client"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None
    ):
        self.api_key = (api_key or Config.LLM_API_KEY or '').strip()
        self.base_url = (base_url or Config.LLM_BASE_URL or '').strip()
        self.model = (model or Config.LLM_MODEL_NAME or '').strip()
        # Keep LLM calls bounded so API routes fail fast and can apply fallback logic.
        self.timeout = float(timeout if timeout is not None else os.environ.get('LLM_TIMEOUT_SECONDS', '120'))

        if not self.api_key:
            raise ValueError("LLM_API_KEY not configured")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )

        # Ollama context window size — prevents prompt truncation.
        # Read from env OLLAMA_NUM_CTX, default 8192 (Ollama default is only 2048).
        self._num_ctx = int(os.environ.get('OLLAMA_NUM_CTX', '8192'))

    def _is_ollama(self) -> bool:
        """Check if we're talking to an Ollama server."""
        return '11434' in (self.base_url or '')

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        Send chat request

        Args:
            messages: Message list
            temperature: Temperature parameter
            max_tokens: Max token count
            response_format: Response format (e.g., JSON mode)

        Returns:
            Model response text
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format:
            kwargs["response_format"] = response_format

        # For Ollama: pass num_ctx via extra_body to prevent prompt truncation
        if self._is_ollama() and self._num_ctx:
            kwargs["extra_body"] = {
                "options": {"num_ctx": self._num_ctx}
            }

        response = self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        # Some models (like MiniMax M2.5) include <think>thinking content in response, need to remove
        content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
        return content

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Send chat request and return JSON

        Args:
            messages: Message list
            temperature: Temperature parameter
            max_tokens: Max token count

        Returns:
            Parsed JSON object
        """
        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )

        # Parse once (strict JSON mode path).
        parsed = self._parse_json_response(response)
        if parsed is not None:
            return parsed

        # Do not perform another long model call here. Upstream callers may apply
        # deterministic fallback behavior when JSON output is invalid.
        cleaned_preview = self._clean_text_response(response)
        raise ValueError(f"Invalid JSON format from LLM: {cleaned_preview[:500]}")

    def _clean_text_response(self, response: Optional[str]) -> str:
        """Normalize response text before JSON parsing."""
        text = (response or '').strip()
        text = re.sub(r'^```(?:json)?\s*\n?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\n?```\s*$', '', text)
        return text.strip()

    def _extract_json_object(self, text: str) -> Optional[str]:
        """Extract first balanced JSON object from noisy model text."""
        start = text.find('{')
        if start == -1:
            return None

        depth = 0
        in_string = False
        escape = False

        for i in range(start, len(text)):
            ch = text[i]

            if in_string:
                if escape:
                    escape = False
                elif ch == '\\':
                    escape = True
                elif ch == '"':
                    in_string = False
                continue

            if ch == '"':
                in_string = True
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]

        return None

    def _parse_json_response(self, response: Optional[str]) -> Optional[Dict[str, Any]]:
        """Try strict and extracted-object JSON parsing; return None on failure."""
        cleaned = self._clean_text_response(response)
        if not cleaned:
            return None

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                return parsed
            return None
        except json.JSONDecodeError:
            pass

        extracted = self._extract_json_object(cleaned)
        if not extracted:
            return None

        try:
            parsed = json.loads(extracted)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None
