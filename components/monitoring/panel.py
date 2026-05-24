from __future__ import annotations

from html import escape
from typing import Any


def render_connector_panel(context: dict[str, Any]) -> str:
    connectors = context.get("connectors", [])
    signals = context.get("signalLedger", [])
    pipeline = context.get("agentPipeline", [])
    return f"""
    <article class="panel connector-panel">
      <div class="panel-heading">
        <span>MODULE 02</span>
        <h2>Monitoring Connectors</h2>
      </div>
      <div class="connector-grid" data-connector-grid>
        {''.join(_render_connector(connector) for connector in connectors)}
      </div>
      <div class="agent-pipeline" data-agent-pipeline>
        {''.join(_render_pipeline_stage(stage) for stage in pipeline)}
      </div>
      <div class="signal-ledger" data-signal-ledger>
        {''.join(_render_signal(signal) for signal in signals[-6:]) if signals else '<div class="empty-state">No real signals imported.</div>'}
      </div>
      <div class="connector-status" data-connector-status></div>
    </article>
    """


def render_root_cause_panel(analysis: dict[str, Any]) -> str:
    candidates = analysis.get("candidates", [])
    playbooks = analysis.get("playbooks", [])
    next_checks = analysis.get("nextChecks", [])
    return f"""
    <article class="panel root-cause-panel">
      <div class="panel-heading">
        <span>MODULE 04</span>
        <h2>Root Cause Agent</h2>
      </div>
      <div class="cause-verdict">
        <span data-integration-summary>{escape(str(analysis.get("integrationSummary", "connector summary pending")))}</span>
        <strong data-cause-title>{escape(str(analysis["rootCause"]))}</strong>
        <em data-cause-confidence>{escape(str(analysis["confidence"]))}% CONFIDENCE</em>
      </div>
      <div class="candidate-list" data-candidate-list>
        {''.join(_render_candidate(candidate) for candidate in candidates[:4]) if candidates else '<div class="empty-state">No candidates until real telemetry is imported.</div>'}
      </div>
      <div class="playbook-list" data-playbook-list>
        {''.join(_render_playbook(playbook) for playbook in playbooks[:4]) if playbooks else '<div class="empty-state">No playbooks generated without evidence.</div>'}
      </div>
      <div class="next-checks" data-next-checks>
        {''.join(f"<span>{escape(str(check))}</span>" for check in next_checks[:4])}
      </div>
    </article>
    """


def _render_connector(connector: dict[str, Any]) -> str:
    status = escape(str(connector.get("status", "unknown")))
    provider = escape(str(connector.get("id", "")))
    latency = connector.get("ingestLatencyMs")
    latency_label = "--" if latency is None else f"{int(latency)}ms"
    signal_count = int(connector.get("signalCount") or 0)
    return f"""
    <div class="connector-card" data-connector-id="{provider}" data-status="{status}">
      <div>
        <span>{escape(str(connector.get("name", "Connector")))}</span>
        <strong>{escape(str(connector.get("kind", "telemetry")))}</strong>
      </div>
      <em>{status} / {escape(str(connector.get("mode", "live")))}</em>
      <p>{escape(str(connector.get("lastSignal", "waiting for signal")))}</p>
      <footer>
        <span>{latency_label}</span>
        <span>{signal_count:,} signals</span>
        <span>{escape(str(connector.get("lastSync", "--")))}</span>
      </footer>
      <div class="connector-actions">
        <button class="small-command-button" type="button" data-connect-toggle="{provider}">Connect</button>
        <button class="small-command-button" type="button" data-sync-connector="{provider}">Sync</button>
        <button class="small-command-button subtle" type="button" data-disconnect-connector="{provider}">Disconnect</button>
      </div>
      {_render_connector_form(connector)}
    </div>
    """


def _render_connector_form(connector: dict[str, Any]) -> str:
    provider = escape(str(connector.get("id", "")))
    defaults = connector.get("defaults", {})
    if connector.get("id") == "datadog":
        return f"""
        <form class="connector-form" data-connector-form="{provider}" hidden>
          <label>Site<input name="site" value="{escape(str(defaults.get("site", "datadoghq.com")))}" autocomplete="off"></label>
          <label>API Key<input name="apiKey" type="password" autocomplete="off"></label>
          <label>Application Key<input name="appKey" type="password" autocomplete="off"></label>
          <button class="small-command-button" type="submit">Validate</button>
        </form>
        """
    if connector.get("id") == "grafana":
        return f"""
        <form class="connector-form" data-connector-form="{provider}" hidden>
          <label>Base URL<input name="baseUrl" value="{escape(str(defaults.get("baseUrl", "")))}" autocomplete="off"></label>
          <label>Service Account Token<input name="token" type="password" autocomplete="off"></label>
          <button class="small-command-button" type="submit">Validate</button>
        </form>
        """
    if connector.get("id") == "newrelic":
        return f"""
        <form class="connector-form" data-connector-form="{provider}" hidden>
          <label>Region<select name="region"><option value="us">US</option><option value="eu">EU</option></select></label>
          <label>Account ID<input name="accountId" autocomplete="off"></label>
          <label>API Key<input name="apiKey" type="password" autocomplete="off"></label>
          <button class="small-command-button" type="submit">Validate</button>
        </form>
        """
    return ""


def _render_signal(signal: dict[str, Any]) -> str:
    severity = escape(str(signal.get("severity", "info")).lower())
    return f"""
    <div class="signal-row severity-{severity}">
      <span>{escape(str(signal.get("time", "--")))}</span>
      <strong>{escape(str(signal.get("source", "unknown")))}</strong>
      <em>{escape(str(signal.get("kind", "signal")))}</em>
      <p>{escape(str(signal.get("message", "")))}</p>
    </div>
    """


def _render_pipeline_stage(stage: dict[str, Any]) -> str:
    return f"""
    <div class="pipeline-stage" data-state="{escape(str(stage.get("state", "waiting")))}">
      <span>{escape(str(stage.get("stage", "Stage")))}</span>
      <strong>{escape(str(stage.get("state", "waiting")))}</strong>
      <p>{escape(str(stage.get("detail", "")))}</p>
    </div>
    """


def _render_candidate(candidate: dict[str, Any]) -> str:
    sources = ", ".join(str(source) for source in candidate.get("sourceAgreement", [])) or "local telemetry"
    return f"""
    <div class="candidate-card" data-score="{int(candidate.get("score", 0))}">
      <span>{int(candidate.get("score", 0))}% / {escape(str(candidate.get("confidence", "medium"))).upper()}</span>
      <strong>{escape(str(candidate.get("title", "candidate")))}</strong>
      <p>{escape(str(candidate.get("why", "")))}</p>
      <em>{escape(sources)}</em>
    </div>
    """


def _render_playbook(playbook: dict[str, Any]) -> str:
    return f"""
    <div class="playbook-card">
      <span>{escape(str(playbook.get("owner", "sre")))} / {escape(str(playbook.get("risk", "low")))} risk</span>
      <strong>{escape(str(playbook.get("name", "Fix action")))}</strong>
      <code>{escape(str(playbook.get("command", "")))}</code>
      <p>{escape(str(playbook.get("impact", "")))}</p>
    </div>
    """
