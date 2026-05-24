from __future__ import annotations

from typing import Any


def render_ai_panel(analysis: dict[str, Any]) -> str:
    evidence = "".join(f"<p>{item}</p>" for item in analysis["evidence"])
    remediation = "".join(f"<p>{item}</p>" for item in analysis["remediation"])
    return f"""
    <article class="panel ai-panel">
      <div class="panel-heading">
        <span>MODULE 03</span>
        <h2>AI Neural Analysis Engine</h2>
      </div>
      <div class="ai-status-row">
        <span data-ai-source>OPENROUTER STATUS :: VERIFYING</span>
        <span data-telemetry-source>TELEMETRY :: SERVER STREAM</span>
      </div>
      <pre class="thinking-stream" data-thinking-stream></pre>
      <div class="ai-output" data-ai-output>
        <div class="ai-kv"><span>ROOT CAUSE</span><strong>{analysis["rootCause"]}</strong></div>
        <div class="ai-kv"><span>CONFIDENCE</span><strong>{analysis["confidence"]}%</strong></div>
        <div class="ai-list"><span>EVIDENCE</span>{evidence}</div>
        <div class="ai-list"><span>SUGGESTED ACTIONS</span>{remediation}</div>
      </div>
      <button class="command-button" type="button" data-run-analysis>ANALYZE REAL TELEMETRY</button>
      <pre class="openrouter-stream" data-openrouter-stream aria-label="Streaming AI reasoning"></pre>
    </article>
    """


def render_summary_panel(analysis: dict[str, Any]) -> str:
    return f"""
    <article class="panel summary-panel">
      <div class="panel-heading">
        <span>MODULE 09</span>
        <h2>Incident Summary Generator</h2>
      </div>
      <p data-summary-text>{analysis["summary"]}</p>
      <div class="summary-actions">
        <span>POSTMORTEM READY</span>
        <span>SLACK BRIEF READY</span>
        <span>JIRA DRAFT READY</span>
      </div>
    </article>
    """
