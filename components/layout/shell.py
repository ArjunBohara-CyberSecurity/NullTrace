from __future__ import annotations


def render_shell(
    *,
    title: str,
    content: str,
    css: str,
    state_json: str,
    client_runtime: str,
) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>{css}</style>
</head>
<body>
  <canvas id="atmosphere" aria-hidden="true"></canvas>
  <div class="scanline" aria-hidden="true"></div>
  <div class="noise" aria-hidden="true"></div>
  <header class="top-command">
    <div class="brand-mark" aria-hidden="true">
      <svg viewBox="0 0 44 44" role="img">
        <path d="M22 3 39 13v18L22 41 5 31V13L22 3Z"/>
        <path d="M14 22h16M22 14v16M11 12l22 20M33 12 11 32"/>
      </svg>
    </div>
    <div>
      <p class="eyebrow">AI-Powered Incident Intelligence</p>
      <h1>NULLTRACE :: INCIDENT WAR ROOM</h1>
    </div>
    <div class="top-command__right">
      <span class="status-light idle"></span>
      <span>NO INCIDENT LOADED</span>
      <time data-clock>SYNCING</time>
    </div>
  </header>
  {content}
  <script>window.NULLTRACE_STATE = {state_json};</script>
  <script>{client_runtime}</script>
</body>
</html>"""
