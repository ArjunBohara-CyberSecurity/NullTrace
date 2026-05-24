from __future__ import annotations

from typing import Any


def render_timeline_panel(timeline: list[dict[str, Any]]) -> str:
    events = "".join(render_event(event) for event in timeline)
    return f"""
    <article class="panel timeline-panel">
      <div class="panel-heading">
        <span>MODULE 08</span>
        <h2>Incident Timeline</h2>
      </div>
      <div class="timeline">
        {events if events else '<div class="empty-state">No incident timeline imported.</div>'}
      </div>
    </article>
    """


def render_event(event: dict[str, str]) -> str:
    return f"""
    <div class="timeline-event severity-{event["severity"].lower()}">
      <time>{event["time"]}</time>
      <span></span>
      <p>{event["message"]}</p>
    </div>
    """
