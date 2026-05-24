from __future__ import annotations

import json
import os
from typing import Any, Iterable
from urllib import error
from urllib import request

from lib.ai.prompts import SYSTEM_PROMPT, build_user_prompt


DEFAULT_MODEL = "deepseek/deepseek-chat-v3-0324:free"
FALLBACK_MODELS = [
    DEFAULT_MODEL,
    "qwen/qwen3-32b:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "deepseek/deepseek-v4-flash:free",
    "liquid/lfm-2.5-1.2b-instruct:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "minimax/minimax-m2.5:free",
    "baidu/cobuddy:free",
]
_FREE_MODEL_CACHE: list[str] | None = None
_WORKING_MODEL: str | None = None


class OpenRouterClient:
    def __init__(self, model: str | None = None) -> None:
        self.api_key = os.environ.get("OPENROUTER_API_KEY", "")
        self.base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
        self.explicit_model = model is not None
        self.env_model = os.environ.get("OPENROUTER_MODEL")
        self.requested_model = model or self.env_model
        self.model = self.requested_model or DEFAULT_MODEL

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.api_key != "your_api_key")

    def status(self) -> dict[str, Any]:
        return {
            "configured": self.configured,
            "baseUrl": self.base_url,
            "model": self.model,
            "requestedModel": self.requested_model,
            "availableFreeModels": FALLBACK_MODELS,
        }

    def analyze_context(self, context: dict[str, Any], local_analysis: dict[str, Any]) -> dict[str, Any]:
        last_error: Exception | None = None
        for model in self._candidate_models():
            self.model = model
            try:
                payload = self._payload(context, local_analysis, stream=False)
                response = self._post(payload)
                data = json.loads(response.decode("utf-8"))
                content = data["choices"][0]["message"].get("content", "")
                if isinstance(content, list):
                    content = "".join(
                        part.get("text", "") if isinstance(part, dict) else str(part) for part in content
                    )
                self._remember_working_model(model)
                return self._parse_json_content(content, local_analysis)
            except Exception as exc:
                last_error = exc
                if "HTTP 401" in str(exc) or "HTTP 403" in str(exc):
                    break
        raise RuntimeError(f"OpenRouter failed for available free models: {last_error}") from last_error

    def stream_analysis(
        self,
        context: dict[str, Any],
        local_analysis: dict[str, Any],
    ) -> Iterable[str]:
        last_error: Exception | None = None
        for model in self._candidate_models():
            self.model = model
            payload = self._payload(context, local_analysis, stream=True)
            req = self._request(payload)
            try:
                with request.urlopen(req, timeout=45) as response:
                    for raw_line in response:
                        line = raw_line.decode("utf-8", errors="ignore").strip()
                        if not line.startswith("data:"):
                            continue
                        data = line[5:].strip()
                        if data == "[DONE]":
                            return
                        try:
                            event = json.loads(data)
                        except json.JSONDecodeError:
                            continue
                        token = event.get("choices", [{}])[0].get("delta", {}).get("content")
                        if token:
                            self._remember_working_model(model)
                            yield token
                return
            except error.HTTPError as exc:
                last_error = RuntimeError(self._http_error_message(exc))
                if exc.code in (401, 403):
                    break
            except error.URLError as exc:
                last_error = RuntimeError(f"OpenRouter network error: {exc.reason}")
        raise RuntimeError(f"OpenRouter streaming failed for available free models: {last_error}") from last_error

    def _payload(
        self,
        context: dict[str, Any],
        local_analysis: dict[str, Any],
        *,
        stream: bool,
    ) -> dict[str, Any]:
        return {
            "model": self.model,
            "stream": stream,
            "temperature": 0.18,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(context, local_analysis)},
            ],
        }

    def _post(self, payload: dict[str, Any]) -> bytes:
        req = self._request(payload)
        try:
            with request.urlopen(req, timeout=45) as response:
                return response.read()
        except error.HTTPError as exc:
            raise RuntimeError(self._http_error_message(exc)) from exc
        except error.URLError as exc:
            raise RuntimeError(f"OpenRouter network error: {exc.reason}") from exc

    def _request(self, payload: dict[str, Any]) -> request.Request:
        body = json.dumps(payload).encode("utf-8")
        return request.Request(
            f"{self.base_url}/chat/completions",
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": os.environ.get("NEXT_PUBLIC_APP_NAME", "NULLTRACE"),
                "User-Agent": "NULLTRACE Python Incident Intelligence",
            },
        )

    def _candidate_models(self) -> list[str]:
        if _WORKING_MODEL:
            return [_WORKING_MODEL]

        if self.explicit_model and self.requested_model:
            return [self.requested_model]

        live_free = self._live_free_models()
        if not live_free:
            return self._dedupe([self.requested_model, *FALLBACK_MODELS])

        candidates: list[str] = []
        if self.requested_model and self.requested_model in live_free:
            candidates.append(self.requested_model)
        for model in FALLBACK_MODELS:
            if model in live_free and model not in candidates:
                candidates.append(model)
        for model in live_free:
            if model not in candidates:
                candidates.append(model)
        return candidates

    def _dedupe(self, models: list[str | None]) -> list[str]:
        deduped: list[str] = []
        for model in models:
            if model and model not in deduped:
                deduped.append(model)
        return deduped

    def _remember_working_model(self, model: str) -> None:
        global _WORKING_MODEL
        _WORKING_MODEL = model

    def _live_free_models(self) -> list[str]:
        global _FREE_MODEL_CACHE
        if _FREE_MODEL_CACHE is not None:
            return _FREE_MODEL_CACHE

        req = request.Request(
            f"{self.base_url}/models",
            method="GET",
            headers={
                "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
                "User-Agent": "NULLTRACE Python Incident Intelligence",
            },
        )
        try:
            with request.urlopen(req, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            _FREE_MODEL_CACHE = []
            return _FREE_MODEL_CACHE

        models = payload.get("data", [])
        _FREE_MODEL_CACHE = [
            item["id"]
            for item in models
            if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"].endswith(":free")
        ]
        return _FREE_MODEL_CACHE

    def _http_error_message(self, exc: error.HTTPError) -> str:
        try:
            body = exc.read().decode("utf-8", errors="replace")
            data = json.loads(body)
            detail = data.get("error", {}).get("message") or data.get("message") or body
        except Exception:
            detail = exc.reason
        return f"OpenRouter HTTP {exc.code}: {detail}"

    def _parse_json_content(self, content: str, fallback: dict[str, Any]) -> dict[str, Any]:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.removeprefix("json").strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            cleaned = cleaned[start : end + 1]
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            parsed = fallback.copy()
            parsed["rawOpenRouterResponse"] = content
            return parsed

        merged = fallback.copy()
        for key in (
            "rootCause",
            "confidence",
            "evidence",
            "remediation",
            "blastRadius",
            "summary",
            "candidates",
            "playbooks",
            "nextChecks",
            "integrationSummary",
        ):
            if key in parsed:
                merged[key] = parsed[key]
        return merged
