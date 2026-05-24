from __future__ import annotations

from typing import Any


def render_command_panel(context: dict[str, Any]) -> str:
    incidents = context["alerts"]
    critical_count = sum(1 for alert in incidents if alert["severity"] == "CRITICAL")
    impacted = ", ".join(context["impact"]["regions"]) or "no regions"
    error_rate = _latest(context["metrics"].get("errorRate", []), suffix="%")
    latency = _latest(context["metrics"].get("latencyMs", []), suffix="ms", integer=True)
    return f"""
    <article class="panel command-panel">
      <div class="panel-heading">
        <span>MODULE 01</span>
        <h2>Incident War Room</h2>
      </div>
      <div class="incident-hero">
        <div>
          <p class="metric-label">ACTIVE INCIDENT</p>
          <strong>{context["incident"]["title"]}</strong>
          <span>{context["incident"]["id"]} / {context["incident"]["severity"]} / {impacted}</span>
        </div>
        <div class="severity-orbit" aria-hidden="true">
          <i></i><i></i><i></i>
          <b>{critical_count}</b>
        </div>
      </div>
      <div class="kpi-grid">
        <div><span>INCIDENTS</span><strong>{len(incidents)}</strong></div>
        <div><span>AFFECTED SERVICES</span><strong>{context["impact"]["affectedServices"]}</strong></div>
        <div><span>ERROR RATE</span><strong data-metric="errors">{error_rate}</strong></div>
        <div><span>P95 LATENCY</span><strong data-metric="latency">{latency}</strong></div>
      </div>
      <div class="ops-alerts">
        {''.join(render_alert(alert) for alert in incidents[:4])}
      </div>
    </article>
    """


def render_alert(alert: dict[str, str]) -> str:
    return f"""
    <div class="ops-alert severity-{alert["severity"].lower()}">
      <span>{alert["time"]}</span>
      <strong>{alert["service"]}</strong>
      <em>{alert["severity"]}</em>
      <p>{alert["message"]}</p>
    </div>
    """


def render_service_matrix(service_health: dict[str, dict[str, Any]]) -> str:
    cells = []
    for service, health in service_health.items():
        load = health["load"]
        cells.append(
            f"""
            <div class="service-cell" data-service-cell data-load="{load}" data-state="{health["state"]}" style="--load:{load}%">
              <span>{service}</span>
              <strong>{load}%</strong>
              <i></i>
            </div>
            """
        )

    return f"""
    <section class="service-matrix panel" aria-label="Service Health Matrix">
      <div class="panel-heading">
        <span>INFRASTRUCTURE STATUS</span>
        <h2>Service Health Matrix</h2>
      </div>
      <div class="service-grid">
        {''.join(cells) if cells else '<div class="empty-state">No service health imported.</div>'}
      </div>
    </section>
    """


def _latest(values: list[float], *, suffix: str = "", integer: bool = False) -> str:
    if not values:
        return "--"
    value = values[-1]
    if integer:
        return f"{int(value)}{suffix}"
    if isinstance(value, float):
        return f"{value:.1f}{suffix}"
    return f"{value}{suffix}"
