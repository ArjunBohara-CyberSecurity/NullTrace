from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from typing import Any
from urllib import error, parse, request


CONNECTOR_DEFINITIONS: dict[str, dict[str, Any]] = {
    "datadog": {
        "id": "datadog",
        "name": "Datadog",
        "kind": "logs + metrics",
        "fields": ["site", "apiKey", "appKey"],
        "defaults": {"site": "datadoghq.com"},
    },
    "grafana": {
        "id": "grafana",
        "name": "Grafana",
        "kind": "dashboards + alerts",
        "fields": ["baseUrl", "token"],
        "defaults": {"baseUrl": "https://grafana.example.com"},
    },
    "newrelic": {
        "id": "newrelic",
        "name": "New Relic",
        "kind": "apm + traces",
        "fields": ["region", "accountId", "apiKey"],
        "defaults": {"region": "us"},
    },
}


class ConnectorRegistry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._states = {
            provider: self._initial_state(definition)
            for provider, definition in CONNECTOR_DEFINITIONS.items()
        }
        self._credentials: dict[str, dict[str, str]] = {}

    def statuses(self) -> list[dict[str, Any]]:
        with self._lock:
            return [dict(state) for state in self._states.values()]

    def connect(self, provider: str, credentials: dict[str, Any]) -> dict[str, Any]:
        definition = self._definition(provider)
        clean_credentials = self._clean_credentials(credentials)
        missing = [
            field
            for field in definition["fields"]
            if not clean_credentials.get(field)
        ]
        if missing:
            return self._update(
                provider,
                status="error",
                mode="not connected",
                lastSignal=f"Missing required field(s): {', '.join(missing)}",
                lastError=f"Missing required field(s): {', '.join(missing)}",
            )

        try:
            self._validate(provider, clean_credentials)
        except Exception as exc:
            return self._update(
                provider,
                status="error",
                mode="not connected",
                lastSignal=f"Connection validation failed: {exc}",
                lastError=str(exc),
            )

        with self._lock:
            self._credentials[provider] = clean_credentials
        return self._update(
            provider,
            status="connected",
            mode="validated API connection",
            lastSync=_utc_now(),
            lastSignal="Credentials validated by vendor API. No telemetry has been imported yet.",
            lastError="",
        )

    def disconnect(self, provider: str) -> dict[str, Any]:
        definition = self._definition(provider)
        with self._lock:
            self._credentials.pop(provider, None)
        return self._update(
            provider,
            **self._initial_state(definition),
        )

    def sync(self, provider: str) -> dict[str, Any]:
        self._definition(provider)
        with self._lock:
            credentials = dict(self._credentials.get(provider, {}))
        if not credentials:
            state = self._update(
                provider,
                status="not_connected",
                mode="credentials required",
                lastSignal="Connect this provider before syncing telemetry.",
            )
            return {"state": state, "signals": []}

        try:
            signals = self._fetch_signals(provider, credentials)
        except Exception as exc:
            state = self._update(
                provider,
                status="error",
                lastSignal=f"Telemetry sync failed: {exc}",
                lastError=str(exc),
            )
            return {"state": state, "signals": []}

        state = self._update(
            provider,
            status="connected",
            mode="validated API connection",
            lastSync=_utc_now(),
            signalCount=len(signals),
            lastSignal=f"Imported {len(signals)} real signal(s) from vendor API.",
            lastError="",
        )
        return {"state": state, "signals": signals}

    def _definition(self, provider: str) -> dict[str, Any]:
        if provider not in CONNECTOR_DEFINITIONS:
            raise ValueError(f"Unknown connector: {provider}")
        return CONNECTOR_DEFINITIONS[provider]

    def _initial_state(self, definition: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": definition["id"],
            "name": definition["name"],
            "kind": definition["kind"],
            "status": "not_connected",
            "mode": "credentials required",
            "ingestLatencyMs": None,
            "signalCount": 0,
            "lastSync": "--",
            "lastSignal": "Not connected.",
            "lastError": "",
            "fields": list(definition["fields"]),
            "defaults": dict(definition.get("defaults", {})),
        }

    def _update(self, provider: str, **changes: Any) -> dict[str, Any]:
        with self._lock:
            current = dict(self._states[provider])
            current.update(changes)
            self._states[provider] = current
            return dict(current)

    def _clean_credentials(self, credentials: dict[str, Any]) -> dict[str, str]:
        return {
            str(key): str(value).strip()
            for key, value in credentials.items()
            if value is not None and str(value).strip()
        }

    def _validate(self, provider: str, credentials: dict[str, str]) -> None:
        if provider == "datadog":
            self._validate_datadog(credentials)
            return
        if provider == "grafana":
            self._validate_grafana(credentials)
            return
        if provider == "newrelic":
            self._validate_newrelic(credentials)
            return
        raise ValueError(f"Unknown connector: {provider}")

    def _fetch_signals(self, provider: str, credentials: dict[str, str]) -> list[dict[str, Any]]:
        if provider == "datadog":
            return self._fetch_datadog_signals(credentials)
        if provider == "grafana":
            return self._fetch_grafana_signals(credentials)
        if provider == "newrelic":
            return self._fetch_newrelic_signals(credentials)
        raise ValueError(f"Unknown connector: {provider}")

    def _validate_datadog(self, credentials: dict[str, str]) -> None:
        site = credentials["site"].removeprefix("https://").removeprefix("http://").strip("/")
        req = request.Request(
            f"https://api.{site}/api/v1/validate",
            headers={"DD-API-KEY": credentials["apiKey"]},
            method="GET",
        )
        payload = _read_json(req)
        if payload.get("valid") is not True:
            raise RuntimeError("Datadog rejected the API key")

    def _validate_grafana(self, credentials: dict[str, str]) -> None:
        base_url = credentials["baseUrl"].rstrip("/")
        req = request.Request(
            f"{base_url}/api/health",
            headers={"Authorization": f"Bearer {credentials['token']}"},
            method="GET",
        )
        _read_json(req)

    def _validate_newrelic(self, credentials: dict[str, str]) -> None:
        try:
            int(credentials["accountId"])
        except ValueError as exc:
            raise RuntimeError("New Relic account ID must be numeric") from exc
        endpoint = _newrelic_endpoint(credentials.get("region", "us"))
        body = json.dumps({"query": "{ actor { user { name } } }"}).encode("utf-8")
        req = request.Request(
            endpoint,
            data=body,
            headers={
                "API-Key": credentials["apiKey"],
                "Content-Type": "application/json",
            },
            method="POST",
        )
        payload = _read_json(req)
        if payload.get("errors"):
            raise RuntimeError(_graphql_error(payload))

    def _fetch_datadog_signals(self, credentials: dict[str, str]) -> list[dict[str, Any]]:
        site = credentials["site"].removeprefix("https://").removeprefix("http://").strip("/")
        query = parse.urlencode({"group_states": "alert,warn,no data"})
        req = request.Request(
            f"https://api.{site}/api/v1/monitor?{query}",
            headers={
                "DD-API-KEY": credentials["apiKey"],
                "DD-APPLICATION-KEY": credentials["appKey"],
            },
            method="GET",
        )
        payload = _read_json(req)
        signals = []
        for monitor in payload if isinstance(payload, list) else []:
            state = str(monitor.get("overall_state", "unknown")).lower()
            if state in ("ok", "unknown"):
                continue
            signals.append(
                {
                    "time": _utc_now(),
                    "source": "Datadog",
                    "kind": "monitor",
                    "service": ",".join(monitor.get("tags", [])[:3]) or "unknown",
                    "severity": "critical" if state == "alert" else "warning",
                    "message": str(monitor.get("name", "Datadog monitor")),
                    "correlation": str(monitor.get("type", "monitor")),
                }
            )
        return signals

    def _fetch_grafana_signals(self, credentials: dict[str, str]) -> list[dict[str, Any]]:
        base_url = credentials["baseUrl"].rstrip("/")
        req = request.Request(
            f"{base_url}/api/alertmanager/grafana/api/v2/alerts",
            headers={"Authorization": f"Bearer {credentials['token']}"},
            method="GET",
        )
        payload = _read_json(req)
        signals = []
        for alert in payload if isinstance(payload, list) else []:
            labels = alert.get("labels", {})
            annotations = alert.get("annotations", {})
            signals.append(
                {
                    "time": _utc_now(),
                    "source": "Grafana",
                    "kind": "alert",
                    "service": labels.get("service") or labels.get("job") or "unknown",
                    "severity": labels.get("severity", "warning"),
                    "message": annotations.get("summary") or annotations.get("description") or labels.get("alertname", "Grafana alert"),
                    "correlation": labels.get("alertname", "alert"),
                }
            )
        return signals

    def _fetch_newrelic_signals(self, credentials: dict[str, str]) -> list[dict[str, Any]]:
        endpoint = _newrelic_endpoint(credentials.get("region", "us"))
        try:
            account_id = int(credentials["accountId"])
        except ValueError as exc:
            raise RuntimeError("New Relic account ID must be numeric") from exc
        nrql = "SELECT count(*) FROM TransactionError SINCE 30 minutes ago FACET appName LIMIT 20"
        body = json.dumps(
            {
                "query": (
                    "{ actor { account(id: "
                    + str(account_id)
                    + ") { nrql(query: "
                    + json.dumps(nrql)
                    + ") { results } } } }"
                )
            }
        ).encode("utf-8")
        req = request.Request(
            endpoint,
            data=body,
            headers={
                "API-Key": credentials["apiKey"],
                "Content-Type": "application/json",
            },
            method="POST",
        )
        payload = _read_json(req)
        if payload.get("errors"):
            raise RuntimeError(_graphql_error(payload))

        results = (
            payload.get("data", {})
            .get("actor", {})
            .get("account", {})
            .get("nrql", {})
            .get("results", [])
        )
        signals = []
        for result in results:
            count = result.get("count")
            if not count:
                continue
            signals.append(
                {
                    "time": _utc_now(),
                    "source": "New Relic",
                    "kind": "nrql",
                    "service": str(result.get("appName", "unknown")),
                    "severity": "critical" if float(count) >= 10 else "warning",
                    "message": f"{count} transaction error(s) in the last 30 minutes",
                    "correlation": "transaction_errors",
                }
            )
        return signals


def _read_json(req: request.Request) -> Any:
    try:
        with request.urlopen(req, timeout=18) as response:
            body = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail[:240]}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc
    return json.loads(body or "{}")


def _newrelic_endpoint(region: str) -> str:
    return "https://api.eu.newrelic.com/graphql" if region.lower() == "eu" else "https://api.newrelic.com/graphql"


def _graphql_error(payload: dict[str, Any]) -> str:
    errors = payload.get("errors") or []
    if not errors:
        return "GraphQL request failed"
    first = errors[0]
    if isinstance(first, dict):
        return str(first.get("message", "GraphQL request failed"))
    return str(first)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


_REGISTRY: ConnectorRegistry | None = None
_REGISTRY_LOCK = threading.Lock()


def get_connector_registry() -> ConnectorRegistry:
    global _REGISTRY
    with _REGISTRY_LOCK:
        if _REGISTRY is None:
            _REGISTRY = ConnectorRegistry()
        return _REGISTRY
