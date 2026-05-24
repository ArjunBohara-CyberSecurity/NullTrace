from __future__ import annotations

from typing import Any


def render_metrics_panel(metrics: dict[str, list[float]]) -> str:
    cpu = _latest(metrics.get("cpu", []), suffix="%", integer=True)
    memory = _latest(metrics.get("memory", []), suffix="%", integer=True)
    throughput = _latest(metrics.get("throughput", []), suffix="/s", integer=True)
    return f"""
    <article class="panel metrics-panel">
      <div class="panel-heading">
        <span>MODULE 06</span>
        <h2>Metrics Visualization</h2>
      </div>
      <div class="metric-strip">
        <div><span>CPU</span><strong data-metric="cpu">{cpu}</strong></div>
        <div><span>MEMORY</span><strong>{memory}</strong></div>
        <div><span>THROUGHPUT</span><strong>{throughput}</strong></div>
      </div>
      <canvas id="metricsCanvas" aria-label="Realtime monochrome infrastructure metrics"></canvas>
      <div class="legend-row">
        <span>LATENCY</span>
        <span>ERROR RATE</span>
        <span>CPU</span>
        <span>DB SATURATION</span>
      </div>
    </article>
    """


def _latest(values: list[float], *, suffix: str = "", integer: bool = False) -> str:
    if not values:
        return "--"
    value = values[-1]
    if integer:
        return f"{int(value)}{suffix}"
    return f"{value}{suffix}"
