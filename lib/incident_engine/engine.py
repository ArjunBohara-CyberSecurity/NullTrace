from __future__ import annotations

from typing import Any, Iterable


def analyze_incident(context: dict[str, Any]) -> dict[str, Any]:
    signals = context.get("signalLedger", [])
    logs = context.get("logs", [])
    connectors = context.get("connectors", [])
    real_items = signals or logs

    if not real_items:
        return {
            "rootCause": "No root cause available until real telemetry is connected.",
            "confidence": 0,
            "evidence": ["No vendor logs, alerts, metrics, traces, or incidents have been imported."],
            "remediation": ["No fix generated without evidence."],
            "blastRadius": [],
            "summary": "NULLTRACE is idle. Connect a monitoring provider and sync real telemetry to begin analysis.",
            "candidates": [],
            "playbooks": [],
            "nextChecks": [
                "Connect Datadog, Grafana, or New Relic with valid credentials.",
                "Sync telemetry from the connected provider.",
                "Run analysis after real signals appear in the ledger.",
            ],
            "integrationSummary": _integration_summary(connectors),
        }

    candidates = _rank_real_signal_candidates(signals or _logs_to_signals(logs))
    winner = candidates[0]
    evidence = winner["evidence"]
    remediation = [
        f"Open the source alert or trace for {winner['service']} in the reporting monitoring tool.",
        "Check recent deploys, config changes, and dependency health for the affected service.",
        "Confirm impact with another independent signal before taking a destructive action.",
    ]

    return {
        "rootCause": f"Most likely investigation area: {winner['service']}",
        "confidence": winner["score"],
        "evidence": evidence,
        "remediation": remediation,
        "blastRadius": [candidate["service"] for candidate in candidates[:5]],
        "summary": (
            f"NULLTRACE analyzed {len(real_items)} imported real signal(s). "
            f"The strongest evidence currently points to {winner['service']}, "
            "but the app will not label it as confirmed root cause without stronger corroboration."
        ),
        "candidates": candidates,
        "playbooks": _build_evidence_playbooks(winner["service"]),
        "nextChecks": [
            "Pull the source alert details from the original monitoring tool.",
            "Compare this signal against logs, traces, and deployment history.",
            "Run another sync after mitigation to confirm the signal count drops.",
        ],
        "integrationSummary": _integration_summary(connectors),
    }


def token_stream_from_analysis(analysis: dict[str, Any]) -> Iterable[str]:
    lines = [
        "ROOT CAUSE:\n",
        analysis["rootCause"] + "\n\n",
        "CONFIDENCE:\n",
        f"{analysis['confidence']}%\n\n",
        "EVIDENCE:\n",
    ]
    lines.extend(f"- {item}\n" for item in analysis["evidence"])
    lines.append("\nSUGGESTED ACTIONS:\n")
    lines.extend(f"- {item}\n" for item in analysis["remediation"])
    if analysis.get("candidates"):
        lines.append("\nRANKED CANDIDATES:\n")
        lines.extend(
            f"- {item['score']}% {item['title']}\n" for item in analysis["candidates"][:3]
        )
    if analysis.get("playbooks"):
        lines.append("\nFIX PLAYBOOKS:\n")
        lines.extend(
            f"- {item['name']}: {item['command']}\n" for item in analysis["playbooks"][:3]
        )
    lines.append("\nOPERATIONAL SUMMARY:\n")
    lines.append(analysis["summary"] + "\n")
    return lines


def _rank_real_signal_candidates(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for signal in signals:
        service = str(signal.get("service") or "unknown")
        grouped.setdefault(service, []).append(signal)

    candidates = []
    for service, service_signals in grouped.items():
        sources = sorted({str(item.get("source", "unknown")) for item in service_signals})
        critical_count = sum(1 for item in service_signals if str(item.get("severity", "")).lower() == "critical")
        warning_count = sum(1 for item in service_signals if str(item.get("severity", "")).lower() == "warning")
        score = min(88, 35 + critical_count * 14 + warning_count * 8 + len(sources) * 8)
        evidence = [
            f"{item.get('source', 'monitoring')} {item.get('kind', 'signal')}: {item.get('message', '')}"
            for item in service_signals[:4]
        ]
        candidates.append(
            {
                "title": f"{service} has {len(service_signals)} imported signal(s)",
                "service": service,
                "score": int(score),
                "confidence": _confidence_label(score),
                "sourceAgreement": sources,
                "why": "This ranking is based only on imported vendor signals and their severity/source agreement.",
                "evidence": evidence,
            }
        )
    return sorted(candidates, key=lambda item: item["score"], reverse=True)


def _build_evidence_playbooks(service: str) -> list[dict[str, str]]:
    return [
        {
            "name": "Open source evidence",
            "command": f"Inspect the original alert/log/trace for {service}",
            "owner": "incident commander",
            "risk": "low",
            "impact": "keeps mitigation tied to verified telemetry",
        },
        {
            "name": "Check recent change history",
            "command": f"Review deploys, config changes, and feature flags for {service}",
            "owner": "service owner",
            "risk": "low",
            "impact": "finds likely causal changes without assuming one",
        },
        {
            "name": "Verify with second signal",
            "command": "Sync another provider or query adjacent telemetry before mitigation",
            "owner": "sre",
            "risk": "low",
            "impact": "reduces false-positive root-cause calls",
        },
    ]


def _integration_summary(connectors: list[dict[str, Any]]) -> str:
    connected = sum(1 for item in connectors if item.get("status") == "connected")
    total_signals = sum(int(item.get("signalCount") or 0) for item in connectors)
    if not connectors:
        return "No monitoring connectors registered"
    return f"{connected}/{len(connectors)} connectors connected; {total_signals:,} imported signal(s)"


def _source_agreement(signals: list[dict[str, Any]], service: str) -> list[str]:
    related = {
        str(signal.get("source"))
        for signal in signals
        if signal.get("service") == service
        or service in str(signal.get("message", ""))
        or service.split("-")[0] in str(signal.get("message", ""))
    }
    return sorted(source for source in related if source and source != "None")


def _slope(values: list[float], window: int = 5) -> float:
    if len(values) < 2:
        return 0.0
    tail = values[-window:]
    return float(tail[-1]) - float(tail[0])


def _confidence_label(score: float) -> str:
    if score >= 88:
        return "high"
    if score >= 72:
        return "medium"
    return "low"


def _dedupe(items: list[str]) -> list[str]:
    deduped: list[str] = []
    for item in items:
        if item not in deduped:
            deduped.append(item)
    return deduped


def _logs_to_signals(logs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "source": "imported log",
            "kind": "log",
            "service": item.get("service", "unknown"),
            "severity": item.get("severity", "info"),
            "message": item.get("message", ""),
        }
        for item in logs
    ]
