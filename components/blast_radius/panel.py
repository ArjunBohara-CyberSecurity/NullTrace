from __future__ import annotations

from typing import Any


def render_blast_radius_panel(graph: dict[str, Any]) -> str:
    critical_nodes = sum(1 for node in graph["nodes"] if node["state"] == "critical")
    edge_count = len(graph["edges"])
    return f"""
    <article class="panel blast-panel">
      <div class="panel-heading">
        <span>MODULE 07</span>
        <h2>Blast Radius Engine</h2>
      </div>
      <div class="blast-meta">
        <span>{critical_nodes} CRITICAL NODES</span>
        <span>{edge_count} DEPENDENCY LINKS</span>
        <span>PROPAGATION LIVE</span>
      </div>
      <canvas id="blastCanvas" aria-label="Animated infrastructure dependency graph"></canvas>
    </article>
    """
