"""
LLM Client Wrapper
Unified OpenAI format API calls
Supports Ollama num_ctx parameter and streamed reads for reasoning models
"""

import httpx
import json
import os
import re
from urllib.parse import urlsplit, urlunsplit
from typing import Any, Dict, List, Optional
from openai import OpenAI
import urllib3

from ..config import Config
from ..utils.logger import get_logger

# Suppress SSL warnings when verify=False (for self-signed certs on k3s)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
        raw_timeout = timeout if timeout is not None else os.environ.get('LLM_TIMEOUT_SECONDS', '120')
        try:
            self.timeout = float(raw_timeout)
        except (TypeError, ValueError):
            logger.warning("Invalid LLM_TIMEOUT_SECONDS value %r, defaulting to 120 s", raw_timeout)
            self.timeout = 120.0

        if not self.api_key:
            raise ValueError("LLM_API_KEY not configured")

        # Streamed responses use this timeout between chunks instead of waiting for
        # the entire completion body to be buffered by the server.
        http_timeout = httpx.Timeout(self.timeout, connect=min(self.timeout, 10.0))

        # Create HTTP client with SSL verification disabled (for self-signed certs on k3s)
        http_client = httpx.Client(verify=False, timeout=http_timeout)
        self.http_client = http_client
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=http_timeout,
            http_client=http_client,
        )

        # Ollama context window size — prevents prompt truncation.
        # Read from env OLLAMA_NUM_CTX, default 8192 (Ollama default is only 2048).
        self._num_ctx = int(os.environ.get('OLLAMA_NUM_CTX', '8192'))

    def _ollama_native_base_url(self) -> str:
        """Convert OpenAI-compatible base URL to the native Ollama API base."""
        if not self.base_url:
            return ''

        parsed = urlsplit(self.base_url)
        path = parsed.path.rstrip('/')
        if path.endswith('/v1'):
            path = path[:-3]
        return urlunsplit((parsed.scheme, parsed.netloc, path, '', ''))

    def _chat_json_via_ollama_native(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Use Ollama's native chat API so think=false is honored for structured calls."""
        base_url = self._ollama_native_base_url()
        if not base_url:
            raise ValueError('Ollama base URL is not configured')

        payload: Dict[str, Any] = {
            'model': self.model,
            'messages': messages,
            'stream': False,
            'think': False,
            'options': {
                'temperature': temperature,
                'num_ctx': self._num_ctx,
                'num_predict': max_tokens,
            },
        }

        response = self.http_client.post(f'{base_url}/api/chat', json=payload)
        response.raise_for_status()
        body = response.json()
        message = body.get('message') or {}
        content = message.get('content') or ''
        return self._normalize_content(content, max_tokens)

    def _is_ollama(self) -> bool:
        """Check if we're talking to an Ollama server."""
        base = (self.base_url or '').lower()
        return '11434' in base or 'ollama' in base

    def _is_reasoning_model(self) -> bool:
        """Best-effort detection for models that emit long reasoning traces."""
        model = (self.model or '').lower()
        return any(token in model for token in ('qwen3', 'qwq', 'deepseek-r1', 'o1', 'o3'))

    def _should_stream_responses(self) -> bool:
        """Decide whether to use streamed chat completions."""
        configured = (Config.LLM_STREAM_RESPONSES or 'auto').strip().lower()
        if configured in {'1', 'true', 'yes', 'on'}:
            return True
        if configured in {'0', 'false', 'no', 'off'}:
            return False
        return self._is_ollama() or self._is_reasoning_model()

    def _coerce_chunk_text(self, value: Any) -> str:
        """Flatten streaming delta payloads into plain text."""
        if value is None:
            return ''
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            parts = []
            for item in value:
                if isinstance(item, str):
                    parts.append(item)
                    continue
                if isinstance(item, dict):
                    text = item.get('text') or item.get('content') or ''
                    if text:
                        parts.append(str(text))
                    continue
                text = getattr(item, 'text', None) or getattr(item, 'content', None) or ''
                if text:
                    parts.append(str(text))
            return ''.join(parts)
        return str(value)

    def _read_streamed_content(self, stream: Any) -> str:
        """Collect text from a streamed chat completion."""
        parts: List[str] = []
        try:
            for chunk in stream:
                choices = getattr(chunk, 'choices', None) or []
                if not choices:
                    continue
                delta = getattr(choices[0], 'delta', None)
                if delta is None:
                    continue

                content_text = self._coerce_chunk_text(getattr(delta, 'content', None))
                if content_text:
                    parts.append(content_text)

                reasoning_text = self._coerce_chunk_text(
                    getattr(delta, 'reasoning_content', None) or getattr(delta, 'reasoning', None)
                )
                if reasoning_text:
                    parts.append(reasoning_text)
        finally:
            close = getattr(stream, 'close', None)
            if callable(close):
                close()

        return ''.join(parts)

    def _normalize_content(self, content: Optional[str], max_tokens: int = 4096) -> str:
        """Remove reasoning traces and normalize whitespace."""
        has_think = bool(re.search(r'<think>[\s\S]*?</think>', content or '', re.IGNORECASE))
        cleaned = re.sub(r'<think>[\s\S]*?</think>', '', content or '', flags=re.IGNORECASE).strip()
        if has_think and not cleaned:
            logger.warning(
                "LLM response contained only <think> content — token budget exhausted by "
                "reasoning trace. Increase this call's max_tokens (currently %d) or reduce prompt size.",
                max_tokens,
            )
        return cleaned

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

        # Only use response_format for non-Ollama providers (OpenAI, Claude, etc.)
        # Ollama doesn't support json_object mode and returns empty string if we pass it
        if response_format and not self._is_ollama():
            kwargs["response_format"] = response_format

        # For Ollama: pass num_ctx via extra_body to prevent prompt truncation
        if self._is_ollama() and self._num_ctx:
            kwargs["extra_body"] = {
                "options": {"num_ctx": self._num_ctx}
            }

        if self._should_stream_responses():
            kwargs["stream"] = True
            response = self.client.chat.completions.create(**kwargs)
            content = self._read_streamed_content(response)
            logger.debug("LLM streamed content before cleaning: %s", repr(content)[:200])
            return self._normalize_content(content, max_tokens)

        response = self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        logger.debug("LLM raw response: %s", repr(response)[:200])
        logger.debug("LLM content before cleaning: %s", repr(content)[:200])
        return self._normalize_content(content, max_tokens)

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        expected_keys: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Send chat request and return JSON

        Args:
            messages: Message list
            temperature: Temperature parameter
            max_tokens: Max token count
            expected_keys: Preferred top-level keys for noisy JSON extraction

        Returns:
            Parsed JSON object
        """
        if self._is_ollama():
            response = self._chat_json_via_ollama_native(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:
            response = self.chat(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )

        # Parse once (strict JSON mode path).
        parsed = self._parse_json_response(response, expected_keys=expected_keys)
        if parsed is not None:
            return parsed

        # Do not perform another long model call here. Upstream callers may apply
        # deterministic fallback behavior when JSON output is invalid.
        cleaned_preview = self._clean_text_response(response)
        logger.warning("LLM returned non-JSON output (raw): %s", repr(response)[:500])
        logger.warning("LLM returned non-JSON output (cleaned): %s", cleaned_preview[:200])
        raise ValueError(f"Invalid JSON format from LLM: {cleaned_preview[:500]}")

    def _clean_text_response(self, response: Optional[str]) -> str:
        """Normalize response text before JSON parsing."""
        text = (response or '').strip()
        text = re.sub(r'^```(?:json)?\s*\n?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\n?```\s*$', '', text)
        return text.strip()

    def _extract_json_objects(self, text: str) -> List[str]:
        """Extract balanced JSON objects from noisy model text."""
        objects: List[str] = []
        depth = 0
        in_string = False
        escape = False
        start: Optional[int] = None

        for i, ch in enumerate(text):
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
                if depth == 0:
                    start = i
                depth += 1
            elif ch == '}':
                if depth == 0:
                    continue
                depth -= 1
                if depth == 0 and start is not None:
                    objects.append(text[start:i + 1])
                    start = None

        return objects

    def _parse_json_response(
        self,
        response: Optional[str],
        expected_keys: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
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

        candidates = []
        for extracted in self._extract_json_objects(cleaned):
            try:
                parsed = json.loads(extracted)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                candidates.append(parsed)

        if not candidates:
            return None

        if expected_keys:
            expected = {key for key in expected_keys if key}
            for candidate in candidates:
                if expected.issubset(candidate.keys()):
                    return candidate
            for candidate in candidates:
                if expected.intersection(candidate.keys()):
                    return candidate

        return candidates[-1]
