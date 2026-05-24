def build_client_runtime() -> str:
    return r"""
(function () {
  const initialState = window.NULLTRACE_STATE;
  let liveContext = JSON.parse(JSON.stringify(initialState.context));
  let liveAnalysis = JSON.parse(JSON.stringify(initialState.analysis));

  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const formatPercent = (value) => `${Math.round(value)}%`;
  const formatNumber = (value) => Number(value || 0).toLocaleString('en-US');
  const asArray = (value) => Array.isArray(value) ? value : [];
  const latest = (values) => asArray(values).length ? values[values.length - 1] : null;
  const metricText = (value, suffix, integer = false) => {
    if (value === null || value === undefined || Number.isNaN(Number(value))) return '--';
    return `${integer ? Math.round(Number(value)) : Number(value).toFixed(1)}${suffix}`;
  };
  const escapeHtml = (value) => String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');

  const runtime = {
    metrics: null,
    logs: null,
    services: null,
    graph: null,
    connectors: null,
    analysis: null
  };

  window.NULLTRACE_RUNTIME = {
    getContext: () => liveContext,
    getAnalysis: () => liveAnalysis,
    ingestSnapshot: (snapshot, analysis) => {
      liveContext = snapshot;
      if (analysis) liveAnalysis = analysis;
      runtime.metrics && runtime.metrics(snapshot);
      runtime.logs && runtime.logs(snapshot);
      runtime.services && runtime.services(snapshot);
      runtime.graph && runtime.graph(snapshot);
      runtime.connectors && runtime.connectors(snapshot);
      runtime.analysis && runtime.analysis(liveAnalysis);
    }
  };

  function bootClock() {
    const target = document.querySelector('[data-clock]');
    const tick = () => {
      const now = new Date();
      target.textContent = now.toISOString().replace('T', ' ').slice(0, 19) + ' UTC';
    };
    tick();
    setInterval(tick, 1000);
  }

  function bootAtmosphere() {
    const canvas = document.getElementById('atmosphere');
    const ctx = canvas.getContext('2d');
    const particles = [];
    const resize = () => {
      canvas.width = window.innerWidth * devicePixelRatio;
      canvas.height = window.innerHeight * devicePixelRatio;
      canvas.style.width = window.innerWidth + 'px';
      canvas.style.height = window.innerHeight + 'px';
    };
    resize();
    window.addEventListener('resize', resize);

    for (let i = 0; i < 92; i += 1) {
      particles.push({
        x: Math.random(),
        y: Math.random(),
        r: Math.random() * 1.3 + 0.2,
        vx: (Math.random() - 0.5) * 0.00016,
        vy: (Math.random() - 0.5) * 0.00012,
        a: Math.random() * 0.26 + 0.06
      });
    }

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.save();
      ctx.scale(devicePixelRatio, devicePixelRatio);
      const width = window.innerWidth;
      const height = window.innerHeight;

      particles.forEach((p, index) => {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < -0.02) p.x = 1.02;
        if (p.x > 1.02) p.x = -0.02;
        if (p.y < -0.02) p.y = 1.02;
        if (p.y > 1.02) p.y = -0.02;

        ctx.beginPath();
        ctx.fillStyle = `rgba(255,255,255,${p.a})`;
        ctx.shadowColor = 'rgba(255,255,255,0.22)';
        ctx.shadowBlur = 8;
        ctx.arc(p.x * width, p.y * height, p.r, 0, Math.PI * 2);
        ctx.fill();

        const nearby = particles[(index + 11) % particles.length];
        const x1 = p.x * width;
        const y1 = p.y * height;
        const x2 = nearby.x * width;
        const y2 = nearby.y * height;
        const dist = Math.hypot(x1 - x2, y1 - y2);
        if (dist < 160) {
          ctx.strokeStyle = `rgba(214,214,214,${(160 - dist) / 2800})`;
          ctx.lineWidth = 0.7;
          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.lineTo(x2, y2);
          ctx.stroke();
        }
      });
      ctx.restore();
      requestAnimationFrame(render);
    };
    render();
  }

  function bootMetrics() {
    const canvas = document.getElementById('metricsCanvas');
    const ctx = canvas.getContext('2d');
    const series = {
      latency: liveContext.metrics.latencyMs.slice(),
      errors: liveContext.metrics.errorRate.slice(),
      cpu: liveContext.metrics.cpu.slice(),
      saturation: liveContext.metrics.dbConnections.slice()
    };

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * devicePixelRatio;
      canvas.height = rect.height * devicePixelRatio;
    };
    resize();
    window.addEventListener('resize', resize);

    function drawLine(values, color, max, offset) {
      const width = canvas.width / devicePixelRatio;
      const height = canvas.height / devicePixelRatio;
      const left = 14;
      const right = width - 14;
      const top = 22 + offset;
      const bottom = height - 22;
      const step = (right - left) / Math.max(values.length - 1, 1);

      ctx.beginPath();
      values.forEach((value, index) => {
        const x = left + index * step;
        const normalized = clamp(value / max, 0, 1);
        const y = bottom - normalized * (bottom - top);
        if (index === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.7;
      ctx.shadowColor = color;
      ctx.shadowBlur = 14;
      ctx.stroke();
      ctx.shadowBlur = 0;
    }

    function render() {
      const width = canvas.width / devicePixelRatio;
      const height = canvas.height / devicePixelRatio;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.save();
      ctx.scale(devicePixelRatio, devicePixelRatio);
      ctx.fillStyle = 'rgba(0,0,0,0.52)';
      ctx.fillRect(0, 0, width, height);
      ctx.strokeStyle = 'rgba(255,255,255,0.055)';
      ctx.lineWidth = 1;
      for (let y = 24; y < height; y += 34) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }
      drawLine(series.latency, 'rgba(255,255,255,0.85)', 900, 0);
      drawLine(series.errors, 'rgba(255,54,72,0.88)', 25, 24);
      drawLine(series.cpu, 'rgba(173,249,255,0.38)', 100, 8);
      drawLine(series.saturation, 'rgba(230,211,166,0.36)', 1200, 0);
      ctx.restore();
      requestAnimationFrame(render);
    }

    runtime.metrics = (snapshot) => {
      series.latency = asArray(snapshot.metrics.latencyMs).slice();
      series.errors = asArray(snapshot.metrics.errorRate).slice();
      series.cpu = asArray(snapshot.metrics.cpu).slice();
      series.saturation = asArray(snapshot.metrics.dbConnections).slice();
      document.querySelector('[data-metric="latency"]').textContent = metricText(latest(series.latency), 'ms', true);
      document.querySelector('[data-metric="errors"]').textContent = metricText(latest(series.errors), '%');
      document.querySelector('[data-metric="cpu"]').textContent = metricText(latest(series.cpu), '%', true);
    };

    render();
  }

  function bootLogs() {
    const stream = document.querySelector('[data-log-stream]');
    const seen = new Set();

    function keyFor(item) {
      return `${item.seq || 'seed'}-${item.time}-${item.service}-${item.message}`;
    }

    function appendLog(item) {
      const empty = stream.querySelector('.empty-state');
      if (empty) empty.remove();
      const key = keyFor(item);
      if (seen.has(key)) return;
      seen.add(key);

      const row = document.createElement('div');
      row.className = 'log-line entering severity-' + String(item.severity).toLowerCase();
      const fields = [
        item.time,
        item.service,
        item.severity,
        item.message
      ];
      row.innerHTML = `<span>${escapeHtml(fields[0])}</span><strong>${escapeHtml(fields[1])}</strong><em>${escapeHtml(fields[2])}</em><span>${escapeHtml(fields[3])}</span>`;
      stream.appendChild(row);
      while (stream.children.length > 18) {
        stream.removeChild(stream.firstElementChild);
      }
      stream.scrollTop = stream.scrollHeight;
      requestAnimationFrame(() => row.classList.remove('entering'));
    }

    runtime.logs = (snapshot) => {
      snapshot.logs.slice(-10).forEach(appendLog);
    };
    liveContext.logs.slice(-10).forEach(appendLog);
  }

  function bootThinking() {
    const target = document.querySelector('[data-thinking-stream]');
    target.textContent = '> idle: no analysis is running\n> connect a provider and sync real telemetry';
  }

  function bootBlastRadius() {
    const canvas = document.getElementById('blastCanvas');
    const ctx = canvas.getContext('2d');
    let nodes = liveContext.infrastructureGraph.nodes.map((node) => ({ ...node }));
    let edges = liveContext.infrastructureGraph.edges.map((edge) => ({ ...edge }));
    let pulse = 0;

    runtime.graph = (snapshot) => {
      nodes = snapshot.infrastructureGraph.nodes.map((node) => ({ ...node }));
      edges = snapshot.infrastructureGraph.edges.map((edge) => ({ ...edge }));
    };

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * devicePixelRatio;
      canvas.height = rect.height * devicePixelRatio;
    };
    resize();
    window.addEventListener('resize', resize);

    function render() {
      const width = canvas.width / devicePixelRatio;
      const height = canvas.height / devicePixelRatio;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.save();
      ctx.scale(devicePixelRatio, devicePixelRatio);
      ctx.fillStyle = 'rgba(0,0,0,0.56)';
      ctx.fillRect(0, 0, width, height);

      const projected = new Map(nodes.map((node) => [
        node.id,
        { ...node, x: width * node.x, y: height * node.y }
      ]));

      edges.forEach((edge, index) => {
        const from = projected.get(edge.from);
        const to = projected.get(edge.to);
        if (!from || !to) return;
        const phase = (pulse + index * 0.14) % 1;
        const px = from.x + (to.x - from.x) * phase;
        const py = from.y + (to.y - from.y) * phase;
        const danger = edge.state === 'critical';
        ctx.strokeStyle = danger ? 'rgba(255,54,72,0.42)' : 'rgba(214,214,214,0.16)';
        ctx.lineWidth = danger ? 1.5 : 1;
        ctx.shadowColor = danger ? 'rgba(255,54,72,0.42)' : 'rgba(255,255,255,0.14)';
        ctx.shadowBlur = danger ? 16 : 8;
        ctx.beginPath();
        ctx.moveTo(from.x, from.y);
        ctx.lineTo(to.x, to.y);
        ctx.stroke();
        ctx.fillStyle = danger ? 'rgba(255,54,72,0.78)' : 'rgba(214,214,214,0.42)';
        ctx.beginPath();
        ctx.arc(px, py, danger ? 3.4 : 2.4, 0, Math.PI * 2);
        ctx.fill();
      });

      projected.forEach((node) => {
        const critical = node.state === 'critical';
        const warning = node.state === 'warning';
        const radius = critical ? 17 : warning ? 14 : 11;
        const flicker = critical ? 1 + Math.sin(performance.now() / 210) * 0.08 : 1;
        ctx.shadowColor = critical ? 'rgba(255,54,72,0.62)' : warning ? 'rgba(230,211,166,0.32)' : 'rgba(173,249,255,0.22)';
        ctx.shadowBlur = critical ? 26 : 14;
        ctx.strokeStyle = critical ? 'rgba(255,54,72,0.88)' : warning ? 'rgba(230,211,166,0.58)' : 'rgba(214,214,214,0.46)';
        ctx.fillStyle = 'rgba(5,5,5,0.88)';
        ctx.lineWidth = critical ? 2 : 1.2;
        ctx.beginPath();
        ctx.arc(node.x, node.y, radius * flicker, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        ctx.shadowBlur = 0;
        ctx.fillStyle = critical ? 'rgba(255,255,255,0.96)' : 'rgba(214,214,214,0.82)';
        ctx.font = '11px "JetBrains Mono", "IBM Plex Mono", monospace';
        ctx.textAlign = 'center';
        ctx.fillText(node.label, node.x, node.y + radius + 16);
      });

      ctx.restore();
      pulse += 0.006;
      requestAnimationFrame(render);
    }
    render();
  }

  function connectorMarkup(connector) {
    const status = String(connector.status || 'unknown').toLowerCase();
    const provider = connector.id || '';
    const latency = connector.ingestLatencyMs === null || connector.ingestLatencyMs === undefined ? '--' : `${connector.ingestLatencyMs}ms`;
    return `
      <div class="connector-card" data-connector-id="${escapeHtml(provider)}" data-status="${escapeHtml(status)}">
        <div>
          <span>${escapeHtml(connector.name || 'Connector')}</span>
          <strong>${escapeHtml(connector.kind || 'telemetry')}</strong>
        </div>
        <em>${escapeHtml(status)} / ${escapeHtml(connector.mode || 'live')}</em>
        <p>${escapeHtml(connector.lastSignal || 'waiting for signal')}</p>
        <footer>
          <span>${escapeHtml(latency)}</span>
          <span>${formatNumber(connector.signalCount)} signals</span>
          <span>${escapeHtml(connector.lastSync || '--')}</span>
        </footer>
        <div class="connector-actions">
          <button class="small-command-button" type="button" data-connect-toggle="${escapeHtml(provider)}">Connect</button>
          <button class="small-command-button" type="button" data-sync-connector="${escapeHtml(provider)}">Sync</button>
          <button class="small-command-button subtle" type="button" data-disconnect-connector="${escapeHtml(provider)}">Disconnect</button>
        </div>
        ${connectorFormMarkup(connector)}
      </div>
    `;
  }

  function connectorFormMarkup(connector) {
    const provider = connector.id || '';
    const defaults = connector.defaults || {};
    if (provider === 'datadog') {
      return `
        <form class="connector-form" data-connector-form="${escapeHtml(provider)}" hidden>
          <label>Site<input name="site" value="${escapeHtml(defaults.site || 'datadoghq.com')}" autocomplete="off"></label>
          <label>API Key<input name="apiKey" type="password" autocomplete="off"></label>
          <label>Application Key<input name="appKey" type="password" autocomplete="off"></label>
          <button class="small-command-button" type="submit">Validate</button>
        </form>
      `;
    }
    if (provider === 'grafana') {
      return `
        <form class="connector-form" data-connector-form="${escapeHtml(provider)}" hidden>
          <label>Base URL<input name="baseUrl" value="${escapeHtml(defaults.baseUrl || '')}" autocomplete="off"></label>
          <label>Service Account Token<input name="token" type="password" autocomplete="off"></label>
          <button class="small-command-button" type="submit">Validate</button>
        </form>
      `;
    }
    if (provider === 'newrelic') {
      return `
        <form class="connector-form" data-connector-form="${escapeHtml(provider)}" hidden>
          <label>Region<select name="region"><option value="us">US</option><option value="eu">EU</option></select></label>
          <label>Account ID<input name="accountId" autocomplete="off"></label>
          <label>API Key<input name="apiKey" type="password" autocomplete="off"></label>
          <button class="small-command-button" type="submit">Validate</button>
        </form>
      `;
    }
    return '';
  }

  function signalMarkup(signal) {
    const severity = String(signal.severity || 'info').toLowerCase();
    return `
      <div class="signal-row severity-${escapeHtml(severity)}">
        <span>${escapeHtml(signal.time || '--')}</span>
        <strong>${escapeHtml(signal.source || 'unknown')}</strong>
        <em>${escapeHtml(signal.kind || 'signal')}</em>
        <p>${escapeHtml(signal.message || '')}</p>
      </div>
    `;
  }

  function pipelineMarkup(stage) {
    const state = String(stage.state || 'waiting').toLowerCase();
    return `
      <div class="pipeline-stage" data-state="${escapeHtml(state)}">
        <span>${escapeHtml(stage.stage || 'Stage')}</span>
        <strong>${escapeHtml(state)}</strong>
        <p>${escapeHtml(stage.detail || '')}</p>
      </div>
    `;
  }

  function candidateMarkup(candidate) {
    const sources = asArray(candidate.sourceAgreement).join(', ') || 'local telemetry';
    return `
      <div class="candidate-card" data-score="${escapeHtml(candidate.score || 0)}">
        <span>${escapeHtml(candidate.score || 0)}% / ${escapeHtml(candidate.confidence || 'medium').toUpperCase()}</span>
        <strong>${escapeHtml(candidate.title || 'candidate')}</strong>
        <p>${escapeHtml(candidate.why || '')}</p>
        <em>${escapeHtml(sources)}</em>
      </div>
    `;
  }

  function playbookMarkup(playbook) {
    return `
      <div class="playbook-card">
        <span>${escapeHtml(playbook.owner || 'sre')} / ${escapeHtml(playbook.risk || 'low')} risk</span>
        <strong>${escapeHtml(playbook.name || 'Fix action')}</strong>
        <code>${escapeHtml(playbook.command || '')}</code>
        <p>${escapeHtml(playbook.impact || '')}</p>
      </div>
    `;
  }

  function bootConnectors() {
    const connectorGrid = document.querySelector('[data-connector-grid]');
    const signalLedger = document.querySelector('[data-signal-ledger]');
    const agentPipeline = document.querySelector('[data-agent-pipeline]');

    runtime.connectors = (snapshot) => {
      if (connectorGrid) {
        connectorGrid.innerHTML = asArray(snapshot.connectors).map(connectorMarkup).join('');
      }
      if (agentPipeline) {
        agentPipeline.innerHTML = asArray(snapshot.agentPipeline).map(pipelineMarkup).join('');
      }
      if (signalLedger) {
        const signals = asArray(snapshot.signalLedger).slice(-6);
        signalLedger.innerHTML = signals.length ? signals.map(signalMarkup).join('') : '<div class="empty-state">No real signals imported.</div>';
      }
    };

    runtime.connectors(liveContext);

    document.addEventListener('click', async (event) => {
      const toggle = event.target.closest('[data-connect-toggle]');
      const sync = event.target.closest('[data-sync-connector]');
      const disconnect = event.target.closest('[data-disconnect-connector]');
      if (toggle) {
        const form = document.querySelector(`[data-connector-form="${CSS.escape(toggle.dataset.connectToggle)}"]`);
        if (form) form.hidden = !form.hidden;
      }
      if (sync) {
        await connectorRequest('/api/connectors/sync', { provider: sync.dataset.syncConnector }, sync);
      }
      if (disconnect) {
        await connectorRequest('/api/connectors/disconnect', { provider: disconnect.dataset.disconnectConnector }, disconnect);
      }
    });

    document.addEventListener('submit', async (event) => {
      const form = event.target.closest('[data-connector-form]');
      if (!form) return;
      event.preventDefault();
      const credentials = {};
      new FormData(form).forEach((value, key) => { credentials[key] = value; });
      await connectorRequest('/api/connectors/connect', {
        provider: form.dataset.connectorForm,
        credentials
      }, form.querySelector('button[type="submit"]'));
    });
  }

  async function connectorRequest(url, payload, control) {
    const status = document.querySelector('[data-connector-status]');
    const previous = control ? control.textContent : '';
    if (control) {
      control.disabled = true;
      control.textContent = 'Working';
    }
    if (status) status.textContent = '';
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      if (!response.ok || data.error) throw new Error(data.error || 'Connector request failed');
      if (data.context) window.NULLTRACE_RUNTIME.ingestSnapshot(data.context, data.analysis);
      if (status) status.textContent = data.state ? data.state.lastSignal || '' : '';
    } catch (error) {
      if (status) status.textContent = error.message;
    } finally {
      if (control) {
        control.disabled = false;
        control.textContent = previous;
      }
    }
  }

  function bootRootCauseAgent() {
    const title = document.querySelector('[data-cause-title]');
    const confidence = document.querySelector('[data-cause-confidence]');
    const integrationSummary = document.querySelector('[data-integration-summary]');
    const candidateList = document.querySelector('[data-candidate-list]');
    const playbookList = document.querySelector('[data-playbook-list]');
    const nextChecks = document.querySelector('[data-next-checks]');
    const summaryText = document.querySelector('[data-summary-text]');

    runtime.analysis = (analysis) => {
      if (!analysis) return;
      if (title) title.textContent = analysis.rootCause || 'root cause pending';
      if (confidence) confidence.textContent = `${analysis.confidence || 0}% CONFIDENCE`;
      if (integrationSummary) integrationSummary.textContent = analysis.integrationSummary || 'connector summary pending';
      if (candidateList) {
        const candidates = asArray(analysis.candidates).slice(0, 4);
        candidateList.innerHTML = candidates.length ? candidates.map(candidateMarkup).join('') : '<div class="empty-state">No candidates until real telemetry is imported.</div>';
      }
      if (playbookList) {
        const playbooks = asArray(analysis.playbooks).slice(0, 4);
        playbookList.innerHTML = playbooks.length ? playbooks.map(playbookMarkup).join('') : '<div class="empty-state">No playbooks generated without evidence.</div>';
      }
      if (nextChecks) {
        nextChecks.innerHTML = asArray(analysis.nextChecks)
          .slice(0, 4)
          .map((check) => `<span>${escapeHtml(check)}</span>`)
          .join('');
      }
      if (summaryText && analysis.summary) summaryText.textContent = analysis.summary;
    };

    runtime.analysis(liveAnalysis);
  }

  function bootAnalyzeAction() {
    const button = document.querySelector('[data-run-analysis]');
    const output = document.querySelector('[data-ai-output]');
    const streaming = document.querySelector('[data-openrouter-stream]');
    const sourceLabel = document.querySelector('[data-ai-source]');

    function renderAnalysis(next, meta) {
      const source = meta ? `${meta.source || 'unknown'} :: ${meta.status || 'unknown'} :: ${meta.model || ''}` : 'unknown';
      const evidence = asArray(next.evidence);
      const remediation = asArray(next.remediation);
      sourceLabel.textContent = 'AI CHANNEL :: ' + source;
      output.innerHTML = `
        <div class="ai-kv"><span>ROOT CAUSE</span><strong>${escapeHtml(next.rootCause)}</strong></div>
        <div class="ai-kv"><span>CONFIDENCE</span><strong>${escapeHtml(next.confidence)}%</strong></div>
        <div class="ai-list"><span>EVIDENCE</span>${evidence.map((item) => `<p>${escapeHtml(item)}</p>`).join('')}</div>
        <div class="ai-list"><span>SUGGESTED ACTIONS</span>${remediation.map((item) => `<p>${escapeHtml(item)}</p>`).join('')}</div>
      `;
      liveAnalysis = next;
      runtime.analysis && runtime.analysis(liveAnalysis);
    }

    button.addEventListener('click', async () => {
      button.disabled = true;
      button.textContent = 'ANALYZING';
      streaming.textContent = '';
      output.classList.add('is-loading');
      try {
        const response = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ context: liveContext, forceOpenRouter: true })
        });
        const payload = await response.json();
        if (payload.error) streaming.textContent = payload.error + '\n';
        renderAnalysis(payload.analysis, payload);
      } catch (error) {
        output.innerHTML = `<div class="ai-kv"><span>CHANNEL DEGRADED</span><strong>${escapeHtml(error.message)}</strong></div>`;
      } finally {
        output.classList.remove('is-loading');
        button.disabled = false;
        button.textContent = 'ANALYZE REAL TELEMETRY';
      }
    });

    fetch('/api/openrouter/status')
      .then((response) => response.json())
      .then((status) => {
        sourceLabel.textContent = `AI CHANNEL :: OPENROUTER ${status.configured ? 'CONFIGURED' : 'NOT CONFIGURED'} :: ${status.model}`;
      })
      .catch(() => {
        sourceLabel.textContent = 'AI CHANNEL :: STATUS UNAVAILABLE';
      });

    streaming.textContent = 'No AI request is running.';
  }

  function bootServiceMatrix() {
    const cells = new Map(
      Array.from(document.querySelectorAll('[data-service-cell]')).map((cell) => [
        cell.querySelector('span').textContent,
        cell
      ])
    );

    runtime.services = (snapshot) => {
      Object.entries(snapshot.serviceHealth).forEach(([service, health]) => {
        const cell = cells.get(service);
        if (!cell) return;
        cell.dataset.load = health.load;
        cell.dataset.state = health.state;
        cell.querySelector('strong').textContent = formatPercent(health.load);
        cell.style.setProperty('--load', `${health.load}%`);
      });
    };
  }

  function bootTelemetryStream() {
    const label = document.querySelector('[data-telemetry-source]');
    if (!window.EventSource) {
      label.textContent = 'TELEMETRY :: EVENTSOURCE UNSUPPORTED';
      return;
    }

    const source = new EventSource('/api/telemetry/stream');
    source.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if (payload.type === 'connected') {
        label.textContent = `TELEMETRY :: ${payload.source}`;
      }
      if (payload.type === 'snapshot') {
        window.NULLTRACE_RUNTIME.ingestSnapshot(payload.context, payload.analysis);
        const runtime = payload.context.runtime || {};
        label.textContent = `TELEMETRY :: STATUS SEQ ${runtime.sequence || 0}`;
      }
    };
    source.onerror = () => {
      label.textContent = 'TELEMETRY :: STREAM RECONNECTING';
    };
  }

  bootClock();
  bootAtmosphere();
  bootMetrics();
  bootLogs();
  bootThinking();
  bootBlastRadius();
  bootConnectors();
  bootRootCauseAgent();
  bootAnalyzeAction();
  bootServiceMatrix();
  bootTelemetryStream();
})();
"""
