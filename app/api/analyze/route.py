from __future__ import annotations

import queue
import threading
import time
from typing import Any, Iterable

from lib.incident_engine.engine import analyze_incident, token_stream_from_analysis
from lib.openrouter.client import OpenRouterClient
from lib.realtime.telemetry import get_realtime_feed


def analyze_payload(payload: dict[str, Any]) -> dict[str, Any]:
    context = payload.get("context") or get_realtime_feed().advance()
    requested_model = payload.get("model")
    force_openrouter = payload.get("forceOpenRouter", True)
    local_analysis = analyze_incident(context)
    client = OpenRouterClient(model=requested_model)

    if not context.get("signalLedger") and not context.get("logs"):
        return {
            "source": "local",
            "status": "no_telemetry",
            "analysis": local_analysis,
        }

    if force_openrouter is False:
        return {"source": "local", "status": "requested_local", "analysis": local_analysis}

    if not client.configured:
        response = {
            "source": "openrouter",
            "status": "not_configured",
            "model": client.model,
            "error": "OPENROUTER_API_KEY is not configured in .env.local",
            "analysis": local_analysis,
        }
        if force_openrouter:
            return response
        return {"source": "local", "status": "fallback", "analysis": local_analysis}

    if client.configured:
        try:
            ai_analysis = client.analyze_context(context, local_analysis)
            return {
                "source": "openrouter",
                "status": "ok",
                "model": client.model,
                "analysis": ai_analysis,
            }
        except Exception as exc:
            local_analysis["upstream"] = {
                "status": "degraded",
                "detail": str(exc),
                "fallback": "local incident engine",
            }
            return {
                "source": "openrouter",
                "status": "upstream_error",
                "model": client.model,
                "error": str(exc),
                "analysis": local_analysis,
            }

    return {"source": "local", "status": "fallback", "analysis": local_analysis}


def stream_events(model: str | None = None) -> Iterable[dict[str, Any]]:
    context = get_realtime_feed().advance()
    local_analysis = analyze_incident(context)
    client = OpenRouterClient(model=model)

    if not context.get("signalLedger") and not context.get("logs"):
        yield {
            "type": "done",
            "source": "local",
            "status": "no_telemetry",
            "analysis": local_analysis,
        }
        return

    yield {
        "type": "status",
        "source": "openrouter",
        "configured": client.configured,
        "model": client.model,
        "text": "secure OpenRouter channel initialized",
    }

    if not client.configured:
        yield {
            "type": "status",
            "source": "openrouter",
            "configured": False,
            "text": "OPENROUTER_API_KEY is not configured; live AI analysis blocked",
        }
        yield {"type": "done", "source": "openrouter", "status": "not_configured", "analysis": local_analysis}
        return

    result_queue: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=1)

    def analyze_with_openrouter() -> None:
        try:
            analysis = client.analyze_context(context, local_analysis)
            result_queue.put({"status": "ok", "analysis": analysis, "model": client.model})
        except Exception as exc:
            result_queue.put(
                {
                    "status": "upstream_error",
                    "error": str(exc),
                    "analysis": local_analysis,
                    "model": client.model,
                }
            )

    thread = threading.Thread(target=analyze_with_openrouter, daemon=True)
    thread.start()

    thinking_lines = [
        "OpenRouter request accepted; live telemetry snapshot sealed",
        "correlating deployment anomaly against metrics and traces",
        "asking upstream model to infer root cause and blast radius",
        "waiting for structured remediation plan from OpenRouter",
        "maintaining live channel while upstream model reasons",
    ]
    cursor = 0

    while True:
        try:
            result = result_queue.get(timeout=1.4)
            break
        except queue.Empty:
            yield {
                "type": "status",
                "source": "openrouter",
                "configured": True,
                "model": client.model,
                "text": thinking_lines[cursor % len(thinking_lines)],
            }
            cursor += 1

    if result["status"] != "ok":
        yield {
            "type": "status",
            "source": "openrouter",
            "configured": True,
            "model": result["model"],
            "text": f"OpenRouter upstream error: {result['error']}",
        }
        yield {
            "type": "done",
            "source": "openrouter",
            "status": "upstream_error",
            "model": result["model"],
            "error": result["error"],
            "analysis": result["analysis"],
        }
        return

    for token in token_stream_from_analysis(result["analysis"]):
        yield {
            "type": "token",
            "source": "openrouter",
            "model": result["model"],
            "text": token,
        }
        time.sleep(0.08)

    yield {
        "type": "done",
        "source": "openrouter",
        "status": "ok",
        "model": result["model"],
        "analysis": result["analysis"],
    }
