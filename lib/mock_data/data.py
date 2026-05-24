from __future__ import annotations

from copy import deepcopy

from lib.integrations.connectors import get_connector_registry


EMPTY_METRICS = {
    "cpu": [],
    "memory": [],
    "latencyMs": [],
    "network": [],
    "errorRate": [],
    "throughput": [],
    "uptime": [],
    "dbConnections": [],
}


OBSERVABILITY_CONTEXT = {
    "incident": {
        "id": "UNCONNECTED",
        "title": "No incident loaded",
        "severity": "IDLE",
        "startedAt": "--",
    },
    "impact": {
        "affectedServices": 0,
        "regions": [],
        "customerImpact": "No real monitoring telemetry has been connected.",
    },
    "logs": [],
    "metrics": EMPTY_METRICS,
    "alerts": [],
    "deploymentEvents": [],
    "traces": [],
    "connectors": [],
    "signalLedger": [],
    "agentPipeline": [
        {"stage": "Ingest", "state": "idle", "detail": "No connector is connected."},
        {"stage": "Correlate", "state": "idle", "detail": "Waiting for real logs, metrics, alerts, or traces."},
        {"stage": "Rank", "state": "idle", "detail": "No root-cause candidates are available."},
        {"stage": "Remediate", "state": "idle", "detail": "No fix playbook generated without evidence."},
    ],
    "serviceHealth": {},
    "infrastructureGraph": {
        "nodes": [],
        "edges": [],
    },
    "timeline": [],
}


def get_observability_context() -> dict:
    context = deepcopy(OBSERVABILITY_CONTEXT)
    context["metrics"] = {key: list(values) for key, values in EMPTY_METRICS.items()}
    context["connectors"] = get_connector_registry().statuses()
    return context
