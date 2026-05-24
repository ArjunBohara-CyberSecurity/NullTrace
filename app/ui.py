from __future__ import annotations

import json
from typing import Any

from app.client_runtime import build_client_runtime
from components.ai.panel import render_ai_panel, render_summary_panel
from components.blast_radius.panel import render_blast_radius_panel
from components.dashboard.panel import render_command_panel, render_service_matrix
from components.layout.shell import render_shell
from components.logs.panel import render_log_stream
from components.metrics.panel import render_metrics_panel
from components.monitoring.panel import render_connector_panel, render_root_cause_panel
from components.timeline.panel import render_timeline_panel
from styles.theme import build_css


def build_index(context: dict[str, Any], analysis: dict[str, Any]) -> str:
    state = {
        "context": context,
        "analysis": analysis,
    }
    content = f"""
    <main class="war-room" aria-label="NULLTRACE Incident War Room">
      <section class="command-grid">
        {render_command_panel(context)}
        {render_ai_panel(analysis)}
      </section>
      <section class="systems-grid">
        {render_connector_panel(context)}
        {render_root_cause_panel(analysis)}
      </section>
      <section class="systems-grid">
        {render_log_stream(context["logs"])}
        {render_metrics_panel(context["metrics"])}
      </section>
      <section class="systems-grid lower-grid">
        {render_blast_radius_panel(context["infrastructureGraph"])}
        <div class="timeline-summary-stack">
          {render_timeline_panel(context["timeline"])}
          {render_summary_panel(analysis)}
        </div>
      </section>
      {render_service_matrix(context["serviceHealth"])}
    </main>
    """
    state_json = json.dumps(state, ensure_ascii=False)
    return render_shell(
        title="NULLTRACE :: INCIDENT WAR ROOM",
        content=content,
        css=build_css(),
        state_json=state_json,
        client_runtime=build_client_runtime(),
    )
