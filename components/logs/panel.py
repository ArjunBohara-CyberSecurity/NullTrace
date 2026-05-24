from __future__ import annotations

from typing import Any


def render_log_stream(logs: list[dict[str, Any]]) -> str:
    rows = "".join(render_log(log) for log in logs[-10:])
    return f"""
    <article class="panel log-panel">
      <div class="panel-heading">
        <span>MODULE 05</span>
        <h2>Live Event Stream</h2>
      </div>
      <div class="terminal-bar">
        <span></span><span></span><span></span>
        <strong>OBSERVABILITY TERMINAL</strong>
      </div>
      <div class="log-stream" data-log-stream>
        {rows if rows else '<div class="empty-state">No logs imported.</div>'}
      </div>
    </article>
    """


def render_log(log: dict[str, str]) -> str:
    return f"""
    <div class="log-line severity-{log["severity"].lower()}">
      <span>{log["time"]}</span>
      <strong>{log["service"]}</strong>
      <em>{log["severity"]}</em>
      <span>{log["message"]}</span>
    </div>
    """
