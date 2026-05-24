def build_css() -> str:
    return r"""
:root {
  color-scheme: dark;
  --absolute: #000000;
  --void: #050505;
  --carbon: #0a0a0a;
  --graphite: #111111;
  --obsidian: #161616;
  --white: #ffffff;
  --silver: #d6d6d6;
  --muted: #8f8f8f;
  --line: rgba(255,255,255,0.12);
  --line-soft: rgba(255,255,255,0.07);
  --critical: #ff3648;
  --warning: #e6d3a6;
  --healthy: #adf9ff;
  --ai: #f2efff;
  --panel-radius: 6px;
  --mono: "Geist Mono", "JetBrains Mono", "IBM Plex Mono", "SFMono-Regular", Consolas, monospace;
  --display: "Space Grotesk", "Inter", "Segoe UI", Arial, sans-serif;
}

* {
  box-sizing: border-box;
}

html {
  min-height: 100%;
  background: var(--absolute);
}

body {
  min-height: 100vh;
  margin: 0;
  overflow-x: hidden;
  background:
    radial-gradient(circle at 50% -10%, rgba(255,255,255,0.10), transparent 30rem),
    linear-gradient(135deg, rgba(255,255,255,0.045), transparent 24rem),
    var(--absolute);
  color: var(--white);
  font-family: var(--display);
}

button,
input,
textarea {
  font: inherit;
}

#atmosphere {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  opacity: 0.62;
}

.scanline,
.noise {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 2;
}

.scanline {
  background: repeating-linear-gradient(
    to bottom,
    rgba(255,255,255,0.04) 0,
    rgba(255,255,255,0.04) 1px,
    transparent 1px,
    transparent 4px
  );
  mix-blend-mode: screen;
  opacity: 0.18;
}

.noise {
  background-image:
    linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px),
    linear-gradient(rgba(255,255,255,0.018) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(circle at center, black, transparent 82%);
  opacity: 0.36;
}

.top-command,
.war-room {
  position: relative;
  z-index: 3;
}

.top-command {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 18px;
  width: min(1740px, calc(100% - 32px));
  margin: 0 auto;
  padding: 24px 0 14px;
  border-bottom: 1px solid var(--line);
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 54px;
  height: 54px;
  border: 1px solid rgba(255,255,255,0.22);
  background: radial-gradient(circle, rgba(255,255,255,0.10), rgba(255,255,255,0.02) 68%);
  box-shadow: 0 0 28px rgba(255,255,255,0.10), inset 0 0 24px rgba(255,255,255,0.04);
}

.brand-mark svg {
  width: 36px;
  height: 36px;
  fill: none;
  stroke: rgba(255,255,255,0.86);
  stroke-width: 1.25;
}

.eyebrow,
.panel-heading span,
.metric-label,
.kpi-grid span,
.metric-strip span,
.summary-actions span,
.blast-meta span,
.legend-row span {
  margin: 0;
  color: var(--muted);
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

h1,
h2 {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

h1 {
  margin-top: 4px;
  font-family: var(--mono);
  font-size: 1.05rem;
  font-weight: 700;
}

h2 {
  color: var(--white);
  font-family: var(--mono);
  font-size: 0.9rem;
}

.top-command__right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  color: var(--silver);
  font-family: var(--mono);
  font-size: 0.75rem;
  white-space: nowrap;
}

.status-light {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--silver);
  box-shadow: 0 0 16px rgba(255,255,255,0.6);
}

.status-light.critical {
  background: var(--critical);
  box-shadow: 0 0 22px rgba(255,54,72,0.82);
  animation: pulse-critical 1.4s infinite;
}

.war-room {
  display: grid;
  gap: 14px;
  width: min(1740px, calc(100% - 32px));
  margin: 14px auto 32px;
}

.command-grid,
.systems-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(400px, 0.92fr);
  gap: 14px;
}

.lower-grid {
  grid-template-columns: minmax(0, 1fr) minmax(420px, 0.85fr);
}

.timeline-summary-stack {
  display: grid;
  gap: 14px;
}

.panel {
  position: relative;
  overflow: hidden;
  min-width: 0;
  border: 1px solid var(--line);
  border-radius: var(--panel-radius);
  background:
    linear-gradient(180deg, rgba(255,255,255,0.045), rgba(255,255,255,0.015)),
    rgba(5,5,5,0.88);
  box-shadow: 0 18px 70px rgba(0,0,0,0.54), inset 0 1px 0 rgba(255,255,255,0.08);
}

.panel::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(90deg, transparent, rgba(255,255,255,0.04), transparent),
    linear-gradient(180deg, rgba(255,255,255,0.03), transparent 24%);
  transform: translateX(-100%);
  animation: neural-shimmer 8s linear infinite;
}

.panel-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 54px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--line-soft);
}

.command-panel,
.ai-panel,
.connector-panel,
.root-cause-panel,
.log-panel,
.metrics-panel,
.blast-panel,
.timeline-panel,
.summary-panel,
.service-matrix {
  min-height: 0;
}

.incident-hero {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 18px;
  align-items: center;
  padding: 22px 18px;
}

.incident-hero strong {
  display: block;
  max-width: 760px;
  margin: 8px 0;
  font-family: var(--mono);
  font-size: 1.8rem;
  line-height: 1.1;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.incident-hero span {
  color: var(--silver);
  font-family: var(--mono);
  font-size: 0.78rem;
  letter-spacing: 0.08em;
}

.severity-orbit {
  position: relative;
  display: grid;
  place-items: center;
  width: 142px;
  aspect-ratio: 1;
}

.severity-orbit i {
  position: absolute;
  inset: 8px;
  border: 1px solid rgba(255,54,72,0.32);
  border-radius: 50%;
  animation: orbit 4s linear infinite;
}

.severity-orbit i:nth-child(2) {
  inset: 20px;
  border-color: rgba(255,255,255,0.14);
  animation-duration: 6.5s;
  animation-direction: reverse;
}

.severity-orbit i:nth-child(3) {
  inset: 34px;
  border-color: rgba(255,54,72,0.48);
  animation-duration: 3.2s;
}

.severity-orbit b {
  color: var(--critical);
  font-family: var(--mono);
  font-size: 2rem;
  text-shadow: 0 0 22px rgba(255,54,72,0.78);
}

.kpi-grid,
.metric-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  border-top: 1px solid var(--line-soft);
  border-bottom: 1px solid var(--line-soft);
}

.kpi-grid div,
.metric-strip div {
  min-width: 0;
  padding: 14px 16px;
  border-right: 1px solid var(--line-soft);
}

.kpi-grid div:last-child,
.metric-strip div:last-child {
  border-right: 0;
}

.kpi-grid strong,
.metric-strip strong {
  display: block;
  margin-top: 6px;
  font-family: var(--mono);
  font-size: 1.35rem;
  color: var(--white);
}

.ops-alerts {
  display: grid;
}

.ops-alert {
  display: grid;
  grid-template-columns: 56px 150px 82px 1fr;
  gap: 12px;
  align-items: center;
  min-height: 46px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--line-soft);
  font-family: var(--mono);
  font-size: 0.74rem;
}

.ops-alert:last-child {
  border-bottom: 0;
}

.ops-alert span,
.ops-alert p {
  color: var(--silver);
}

.ops-alert p {
  margin: 0;
}

.ops-alert em,
.log-line em {
  font-style: normal;
  color: var(--muted);
}

.severity-critical em,
.severity-critical time {
  color: var(--critical);
}

.severity-warning em,
.severity-warning time {
  color: var(--warning);
}

.severity-ai em,
.severity-ai time {
  color: var(--ai);
}

.ai-panel {
  display: grid;
}

.thinking-stream,
.openrouter-stream {
  margin: 0;
  white-space: pre-wrap;
  font-family: var(--mono);
}

.ai-status-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--line-soft);
}

.ai-status-row span {
  border: 1px solid var(--line-soft);
  border-radius: 4px;
  padding: 6px 8px;
  color: var(--silver);
  background: rgba(255,255,255,0.035);
  font-family: var(--mono);
  font-size: 0.64rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.thinking-stream {
  min-height: 142px;
  padding: 16px;
  border-bottom: 1px solid var(--line-soft);
  color: var(--silver);
  line-height: 1.65;
  background: rgba(0,0,0,0.24);
}

.ai-output {
  display: grid;
  gap: 12px;
  padding: 16px;
  transition: opacity 180ms ease, filter 180ms ease;
}

.ai-output.is-loading {
  opacity: 0.58;
  filter: blur(1px);
}

.ai-kv,
.ai-list {
  display: grid;
  gap: 6px;
  font-family: var(--mono);
}

.ai-kv span,
.ai-list span {
  color: var(--muted);
  font-size: 0.68rem;
  letter-spacing: 0.16em;
}

.ai-kv strong {
  color: var(--white);
  line-height: 1.4;
}

.ai-list p {
  margin: 0;
  color: var(--silver);
  font-size: 0.78rem;
  line-height: 1.45;
}

.command-button {
  justify-self: start;
  margin: 0 16px 16px;
  min-height: 38px;
  padding: 0 14px;
  border: 1px solid rgba(255,255,255,0.26);
  border-radius: 4px;
  background: rgba(255,255,255,0.06);
  color: var(--white);
  font-family: var(--mono);
  font-size: 0.72rem;
  letter-spacing: 0.14em;
  cursor: pointer;
  transition: border-color 160ms ease, box-shadow 160ms ease, background 160ms ease;
}

.small-command-button {
  min-height: 32px;
  padding: 0 10px;
  border: 1px solid rgba(255,255,255,0.24);
  border-radius: 4px;
  background: rgba(255,255,255,0.055);
  color: var(--white);
  font-family: var(--mono);
  font-size: 0.66rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  cursor: pointer;
}

.small-command-button:hover {
  border-color: rgba(255,255,255,0.52);
  background: rgba(255,255,255,0.10);
}

.small-command-button:disabled {
  cursor: progress;
  color: var(--muted);
}

.small-command-button.subtle {
  color: var(--muted);
}

.command-button:hover {
  border-color: rgba(255,255,255,0.58);
  background: rgba(255,255,255,0.10);
  box-shadow: 0 0 24px rgba(255,255,255,0.10);
}

.command-button:disabled {
  cursor: progress;
  color: var(--muted);
}

.openrouter-stream {
  min-height: 92px;
  max-height: 160px;
  overflow: auto;
  padding: 12px 16px 16px;
  border-top: 1px solid var(--line-soft);
  color: var(--ai);
  font-size: 0.74rem;
  line-height: 1.55;
}

.connector-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--line-soft);
}

.connector-card,
.candidate-card,
.playbook-card,
.pipeline-stage {
  position: relative;
  min-width: 0;
  border: 1px solid var(--line-soft);
  border-radius: 5px;
  background: rgba(255,255,255,0.028);
  font-family: var(--mono);
}

.connector-card {
  min-height: 156px;
  padding: 12px;
}

.connector-card::after {
  content: "";
  position: absolute;
  right: 12px;
  top: 14px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--healthy);
  box-shadow: 0 0 16px rgba(173,249,255,0.72);
}

.connector-card[data-status="lagging"]::after {
  background: var(--warning);
  box-shadow: 0 0 16px rgba(230,211,166,0.62);
}

.connector-card[data-status="offline"]::after {
  background: var(--critical);
  box-shadow: 0 0 16px rgba(255,54,72,0.72);
}

.connector-card span,
.pipeline-stage span,
.candidate-card span,
.playbook-card span,
.cause-verdict span,
.next-checks span {
  color: var(--muted);
  font-size: 0.66rem;
  letter-spacing: 0.13em;
  text-transform: uppercase;
}

.connector-card strong,
.candidate-card strong,
.playbook-card strong {
  display: block;
  margin-top: 6px;
  padding-right: 16px;
  color: var(--white);
  font-size: 0.86rem;
  line-height: 1.35;
  text-transform: uppercase;
}

.connector-card em {
  display: block;
  margin-top: 12px;
  color: var(--healthy);
  font-size: 0.68rem;
  font-style: normal;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.connector-card[data-status="lagging"] em {
  color: var(--warning);
}

.connector-card p,
.pipeline-stage p,
.candidate-card p,
.playbook-card p {
  margin: 10px 0 0;
  color: var(--silver);
  font-size: 0.72rem;
  line-height: 1.45;
}

.connector-card footer {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}

.connector-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-top: 12px;
}

.connector-form {
  display: grid;
  gap: 9px;
  margin-top: 12px;
  border-top: 1px solid var(--line-soft);
  padding-top: 12px;
}

.connector-form[hidden] {
  display: none;
}

.connector-form label {
  display: grid;
  gap: 5px;
  color: var(--muted);
  font-size: 0.66rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.connector-form input,
.connector-form select {
  min-width: 0;
  min-height: 34px;
  border: 1px solid var(--line-soft);
  border-radius: 4px;
  padding: 0 9px;
  background: rgba(0,0,0,0.36);
  color: var(--white);
  font-family: var(--mono);
  font-size: 0.74rem;
}

.connector-status {
  min-height: 34px;
  padding: 0 16px 14px;
  color: var(--warning);
  font-family: var(--mono);
  font-size: 0.72rem;
  line-height: 1.45;
}

.empty-state {
  grid-column: 1 / -1;
  padding: 16px;
  color: var(--muted);
  font-family: var(--mono);
  font-size: 0.76rem;
  line-height: 1.45;
}

.connector-card footer span {
  border: 1px solid var(--line-soft);
  border-radius: 4px;
  padding: 5px 6px;
  background: rgba(0,0,0,0.26);
  letter-spacing: 0.08em;
}

.agent-pipeline {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--line-soft);
}

.pipeline-stage {
  min-height: 112px;
  padding: 12px;
}

.pipeline-stage strong {
  display: inline-block;
  margin-top: 8px;
  border: 1px solid rgba(173,249,255,0.28);
  border-radius: 4px;
  padding: 4px 6px;
  color: var(--healthy);
  font-size: 0.66rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.pipeline-stage[data-state="ready"] strong {
  border-color: rgba(230,211,166,0.34);
  color: var(--warning);
}

.signal-ledger {
  display: grid;
  padding: 8px 0;
  background:
    linear-gradient(180deg, rgba(0,0,0,0.22), transparent),
    repeating-linear-gradient(to bottom, transparent, transparent 35px, rgba(255,255,255,0.03) 36px);
}

.signal-row {
  display: grid;
  grid-template-columns: 82px 92px 150px 1fr;
  gap: 10px;
  align-items: center;
  min-height: 36px;
  padding: 0 14px;
  color: var(--silver);
  font-family: var(--mono);
  font-size: 0.72rem;
}

.signal-row strong {
  color: var(--white);
}

.signal-row em {
  color: var(--muted);
  font-style: normal;
}

.signal-row p {
  margin: 0;
  line-height: 1.35;
}

.signal-row.severity-critical {
  background: linear-gradient(90deg, rgba(255,54,72,0.12), transparent 70%);
}

.cause-verdict {
  display: grid;
  gap: 9px;
  padding: 16px;
  border-bottom: 1px solid var(--line-soft);
  font-family: var(--mono);
}

.cause-verdict strong {
  color: var(--white);
  font-size: 1.08rem;
  line-height: 1.35;
  text-transform: uppercase;
}

.cause-verdict em {
  justify-self: start;
  border: 1px solid rgba(255,54,72,0.35);
  border-radius: 4px;
  padding: 5px 8px;
  color: var(--critical);
  font-size: 0.7rem;
  font-style: normal;
  letter-spacing: 0.12em;
}

.candidate-list,
.playbook-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--line-soft);
}

.candidate-card,
.playbook-card {
  min-height: 146px;
  padding: 12px;
}

.candidate-card::before {
  content: "";
  position: absolute;
  inset: 0 auto 0 0;
  width: 3px;
  background: var(--critical);
  opacity: 0.78;
}

.candidate-card em {
  display: block;
  margin-top: 10px;
  color: var(--healthy);
  font-size: 0.68rem;
  font-style: normal;
  line-height: 1.35;
}

.playbook-card code {
  display: block;
  margin-top: 9px;
  overflow-wrap: anywhere;
  border: 1px solid var(--line-soft);
  border-radius: 4px;
  padding: 8px;
  background: rgba(0,0,0,0.36);
  color: var(--ai);
  font-size: 0.7rem;
  line-height: 1.35;
}

.next-checks {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px 16px 16px;
}

.next-checks span {
  max-width: 100%;
  border: 1px solid var(--line-soft);
  border-radius: 4px;
  padding: 6px 8px;
  background: rgba(255,255,255,0.035);
  line-height: 1.35;
}

.terminal-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 36px;
  padding: 0 14px;
  border-bottom: 1px solid var(--line-soft);
  background: rgba(255,255,255,0.035);
}

.terminal-bar span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: rgba(255,255,255,0.34);
}

.terminal-bar span:first-child {
  background: var(--critical);
  box-shadow: 0 0 12px rgba(255,54,72,0.52);
}

.terminal-bar strong {
  margin-left: auto;
  color: var(--muted);
  font-family: var(--mono);
  font-size: 0.64rem;
  letter-spacing: 0.14em;
}

.log-stream {
  height: 432px;
  overflow: hidden;
  padding: 8px 0;
  background:
    linear-gradient(180deg, rgba(0,0,0,0.22), transparent),
    repeating-linear-gradient(to bottom, transparent, transparent 31px, rgba(255,255,255,0.035) 32px);
}

.log-line {
  display: grid;
  grid-template-columns: 82px 150px 82px 1fr;
  gap: 12px;
  align-items: center;
  min-height: 32px;
  padding: 0 14px;
  color: var(--silver);
  font-family: var(--mono);
  font-size: 0.74rem;
  transition: transform 280ms ease, opacity 280ms ease, background 280ms ease;
}

.log-line.entering {
  transform: translateY(10px);
  opacity: 0;
}

.log-line strong {
  color: var(--white);
}

.log-line.severity-critical {
  background: linear-gradient(90deg, rgba(255,54,72,0.16), transparent 62%);
  color: var(--white);
  text-shadow: 0 0 14px rgba(255,54,72,0.30);
}

.metrics-panel {
  min-height: 522px;
}

.metric-strip {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  border-top: 0;
}

#metricsCanvas {
  display: block;
  width: 100%;
  height: 360px;
}

.legend-row,
.blast-meta,
.summary-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 12px 16px 14px;
  border-top: 1px solid var(--line-soft);
}

.legend-row span,
.blast-meta span,
.summary-actions span {
  border: 1px solid var(--line-soft);
  border-radius: 4px;
  padding: 6px 8px;
  background: rgba(255,255,255,0.035);
}

.blast-panel {
  min-height: 520px;
}

#blastCanvas {
  display: block;
  width: 100%;
  height: 424px;
}

.timeline {
  display: grid;
  padding: 10px 16px 16px;
}

.timeline-event {
  display: grid;
  grid-template-columns: 62px 18px 1fr;
  gap: 12px;
  align-items: start;
  min-height: 44px;
  color: var(--silver);
  font-family: var(--mono);
  font-size: 0.76rem;
}

.timeline-event time {
  padding-top: 2px;
}

.timeline-event span {
  position: relative;
  width: 9px;
  height: 9px;
  margin-top: 4px;
  border-radius: 50%;
  background: rgba(255,255,255,0.42);
  box-shadow: 0 0 14px rgba(255,255,255,0.26);
}

.timeline-event span::after {
  content: "";
  position: absolute;
  left: 4px;
  top: 10px;
  width: 1px;
  height: 34px;
  background: var(--line);
}

.timeline-event:last-child span::after {
  display: none;
}

.timeline-event p {
  margin: 0;
  line-height: 1.45;
}

.timeline-event.severity-critical span {
  background: var(--critical);
  box-shadow: 0 0 18px rgba(255,54,72,0.65);
}

.timeline-event.severity-warning span {
  background: var(--warning);
}

.timeline-event.severity-ai span {
  background: var(--ai);
}

.summary-panel p {
  margin: 0;
  padding: 18px 16px 20px;
  color: var(--silver);
  font-family: var(--mono);
  font-size: 0.82rem;
  line-height: 1.7;
}

.service-matrix {
  padding-bottom: 14px;
}

.service-grid {
  display: grid;
  grid-template-columns: repeat(8, minmax(0, 1fr));
  gap: 10px;
  padding: 14px 16px 0;
}

.service-cell {
  position: relative;
  overflow: hidden;
  min-height: 92px;
  padding: 12px;
  border: 1px solid var(--line-soft);
  border-radius: 5px;
  background: rgba(255,255,255,0.028);
  font-family: var(--mono);
}

.service-cell::before {
  content: "";
  position: absolute;
  inset: auto 0 0;
  height: var(--load);
  max-height: 100%;
  background: linear-gradient(180deg, transparent, rgba(255,255,255,0.08));
  transition: height 420ms ease;
}

.service-cell[data-state="critical"] {
  border-color: rgba(255,54,72,0.38);
  box-shadow: inset 0 0 28px rgba(255,54,72,0.08);
}

.service-cell[data-state="warning"] {
  border-color: rgba(230,211,166,0.30);
}

.service-cell span,
.service-cell strong,
.service-cell i {
  position: relative;
  z-index: 1;
}

.service-cell span {
  display: block;
  min-height: 34px;
  color: var(--silver);
  font-size: 0.7rem;
  line-height: 1.25;
  text-transform: uppercase;
}

.service-cell strong {
  display: block;
  margin-top: 8px;
  color: var(--white);
  font-size: 1.3rem;
}

.service-cell i {
  display: block;
  width: 100%;
  height: 2px;
  margin-top: 10px;
  background: rgba(255,255,255,0.18);
}

.service-cell[data-state="critical"] i {
  background: var(--critical);
  box-shadow: 0 0 18px rgba(255,54,72,0.76);
}

.service-cell[data-state="warning"] i {
  background: var(--warning);
}

@keyframes neural-shimmer {
  0%, 54% { transform: translateX(-110%); }
  72%, 100% { transform: translateX(110%); }
}

@keyframes pulse-critical {
  0%, 100% { opacity: 0.55; transform: scale(0.92); }
  50% { opacity: 1; transform: scale(1.12); }
}

@keyframes orbit {
  from { transform: rotate(0deg) scale(1); }
  50% { transform: rotate(180deg) scale(1.08); }
  to { transform: rotate(360deg) scale(1); }
}

@media (max-width: 1180px) {
  .command-grid,
  .systems-grid,
  .lower-grid {
    grid-template-columns: 1fr;
  }

  .service-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .connector-grid,
  .agent-pipeline {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .top-command {
    grid-template-columns: auto 1fr;
  }

  .top-command__right {
    grid-column: 1 / -1;
    justify-content: flex-start;
  }

  .incident-hero {
    grid-template-columns: 1fr;
  }

  .severity-orbit {
    width: 116px;
  }

  .incident-hero strong {
    font-size: 1.25rem;
  }

  .kpi-grid,
  .metric-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .ops-alert,
  .log-line {
    grid-template-columns: 70px 1fr;
    gap: 6px 10px;
  }

  .ops-alert em,
  .log-line em {
    justify-self: start;
  }

  .ops-alert p,
  .log-line span:last-child {
    grid-column: 1 / -1;
  }

  .service-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .connector-grid,
  .agent-pipeline,
  .candidate-list,
  .playbook-list {
    grid-template-columns: 1fr;
  }

  .signal-row {
    grid-template-columns: 70px 1fr;
    gap: 6px 10px;
  }

  .signal-row em,
  .signal-row p {
    grid-column: 1 / -1;
  }
}
"""
