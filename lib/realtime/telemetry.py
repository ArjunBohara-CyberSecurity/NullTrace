from __future__ import annotations

import threading
import time
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from lib.integrations.connectors import get_connector_registry
from lib.mock_data.data import get_observability_context


class RealtimeIncidentFeed:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._context = get_observability_context()
        self._started = time.monotonic()
        self._seq = 0

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            self._refresh_connector_status_locked()
            context = deepcopy(self._context)
        context["runtime"] = self._runtime()
        return context

    def advance(self) -> dict[str, Any]:
        return self.snapshot()

    def sync_provider(self, provider: str) -> dict[str, Any]:
        result = get_connector_registry().sync(provider)
        with self._lock:
            self._refresh_connector_status_locked()
            signals = result.get("signals", [])
            if signals:
                self._context["signalLedger"].extend(signals)
                self._context["logs"].extend(_signals_to_logs(signals))
                self._context["timeline"].extend(_signals_to_timeline(signals))
            self._trim_locked()
            self._refresh_pipeline_locked()
            context = deepcopy(self._context)
            self._seq += 1
        context["runtime"] = self._runtime()
        return {"context": context, "signals": signals, "state": result.get("state")}

    def refresh_connectors(self) -> dict[str, Any]:
        with self._lock:
            self._refresh_connector_status_locked()
            self._refresh_pipeline_locked()
            context = deepcopy(self._context)
            self._seq += 1
        context["runtime"] = self._runtime()
        return context

    def _refresh_connector_status_locked(self) -> None:
        self._context["connectors"] = get_connector_registry().statuses()

    def _refresh_pipeline_locked(self) -> None:
        connected = [
            item for item in self._context["connectors"] if item.get("status") == "connected"
        ]
        signal_count = len(self._context["signalLedger"])
        if not connected:
            self._context["agentPipeline"] = [
                {"stage": "Ingest", "state": "idle", "detail": "No connector is connected."},
                {"stage": "Correlate", "state": "idle", "detail": "Waiting for real logs, metrics, alerts, or traces."},
                {"stage": "Rank", "state": "idle", "detail": "No root-cause candidates are available."},
                {"stage": "Remediate", "state": "idle", "detail": "No fix playbook generated without evidence."},
            ]
            return

        self._context["agentPipeline"] = [
            {
                "stage": "Ingest",
                "state": "ready" if signal_count == 0 else "active",
                "detail": f"{len(connected)} connector(s) validated; {signal_count} real signal(s) imported.",
            },
            {
                "stage": "Correlate",
                "state": "idle" if signal_count == 0 else "active",
                "detail": "Waiting for imported signals." if signal_count == 0 else "Real signals available for analysis.",
            },
            {
                "stage": "Rank",
                "state": "idle" if signal_count == 0 else "ready",
                "detail": "No root-cause candidates are available." if signal_count == 0 else "Root-cause ranking can run on imported signals.",
            },
            {
                "stage": "Remediate",
                "state": "idle",
                "detail": "No fix playbook generated without evidence." if signal_count == 0 else "Run analysis to generate evidence-based remediation.",
            },
        ]

    def _trim_locked(self) -> None:
        self._context["signalLedger"] = self._context["signalLedger"][-50:]
        self._context["logs"] = self._context["logs"][-50:]
        self._context["timeline"] = self._context["timeline"][-50:]

    def _runtime(self) -> dict[str, Any]:
        return {
            "source": "local connector status",
            "sequence": self._seq,
            "uptimeSeconds": int(time.monotonic() - self._started),
            "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        }


def _signals_to_logs(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "time": signal.get("time", "--"),
            "service": signal.get("service", "unknown"),
            "severity": str(signal.get("severity", "info")).upper(),
            "message": signal.get("message", ""),
        }
        for signal in signals
    ]


def _signals_to_timeline(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "time": signal.get("time", "--"),
            "severity": str(signal.get("severity", "info")).lower(),
            "message": f"{signal.get('source', 'monitoring')}: {signal.get('message', '')}",
        }
        for signal in signals
    ]


_FEED: RealtimeIncidentFeed | None = None
_FEED_LOCK = threading.Lock()


def get_realtime_feed() -> RealtimeIncidentFeed:
    global _FEED
    with _FEED_LOCK:
        if _FEED is None:
            _FEED = RealtimeIncidentFeed()
        return _FEED
