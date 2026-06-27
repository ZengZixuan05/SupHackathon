HOME_PAGE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Autonomous Feature Pipeline</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=block" rel="stylesheet">
  <style>
    :root {
      --canvas: #FFFDF5;
      --ink: #000000;
      --accent: #FF6B6B;
      --secondary: #FFD93D;
      --muted: #C4B5FD;
      --white: #FFFFFF;
      --shadow-sm: 4px 4px 0 0 var(--ink);
      --shadow-md: 8px 8px 0 0 var(--ink);
      --shadow-lg: 12px 12px 0 0 var(--ink);
    }

    * { box-sizing: border-box; }
    [hidden] { display: none !important; }

    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      font-family: "Space Grotesk", system-ui, sans-serif;
      font-weight: 700;
      background-color: var(--canvas);
      background-image:
        linear-gradient(to right, rgba(0, 0, 0, 0.12) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(0, 0, 0, 0.12) 1px, transparent 1px);
      background-size: 36px 36px;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      opacity: 0.08;
      background-image: radial-gradient(var(--ink) 1.5px, transparent 1.5px);
      background-size: 18px 18px;
      z-index: -1;
    }

    a { color: var(--ink); text-decoration: none; }

    .shell {
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
      padding: 28px 0 48px;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 28px;
    }

    .logo {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      border: 4px solid var(--ink);
      background: var(--secondary);
      box-shadow: var(--shadow-sm);
      padding: 10px 14px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 0.9rem;
      transform: rotate(-1deg);
    }

    .logo-mark {
      display: inline-grid;
      place-items: center;
      width: 28px;
      height: 28px;
      border: 3px solid var(--ink);
      background: var(--accent);
      font-weight: 700;
    }

    .links {
      display: flex;
      flex-wrap: wrap;
      justify-content: flex-end;
      gap: 10px;
      margin: 0;
    }

    .links a {
      display: inline-flex;
      align-items: center;
      min-height: 44px;
      border: 3px solid var(--ink);
      background: var(--white);
      box-shadow: var(--shadow-sm);
      padding: 8px 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 0.78rem;
      transition: transform 100ms linear, box-shadow 100ms linear, background 100ms linear;
    }

    .links a:hover {
      background: var(--muted);
      transform: translate(-1px, -1px);
      box-shadow: 6px 6px 0 0 var(--ink);
    }

    .links a:active {
      transform: translate(4px, 4px);
      box-shadow: none;
    }

    .hero-grid {
      display: grid;
      grid-template-columns: minmax(0, 0.82fr) minmax(520px, 1.18fr);
      gap: 48px;
      align-items: start;
    }

    .hero-copy {
      position: sticky;
      top: 24px;
      display: grid;
      gap: 20px;
    }

    .label {
      width: max-content;
      border: 4px solid var(--ink);
      background: var(--muted);
      box-shadow: var(--shadow-sm);
      padding: 8px 12px;
      text-transform: uppercase;
      letter-spacing: 0.18em;
      font-size: 0.78rem;
      transform: rotate(2deg);
    }

    h1 {
      margin: 0;
      max-width: 100%;
      overflow-wrap: anywhere;
      text-transform: uppercase;
      letter-spacing: -0.045em;
      line-height: 0.88;
      font-size: clamp(3.1rem, 5.4vw, 5.3rem);
      font-weight: 700;
    }

    .headline-solid,
    .headline-block,
    .headline-stroke {
      display: block;
    }

    .headline-block {
      width: fit-content;
      max-width: 100%;
      margin: 10px 0;
      border: 5px solid var(--ink);
      background: var(--accent);
      box-shadow: var(--shadow-md);
      padding: 4px 12px 10px;
      transform: rotate(-1deg);
    }

    .headline-stroke {
      color: transparent;
      -webkit-text-stroke: 2px var(--ink);
      text-shadow: none;
    }

    .hero-note {
      border: 4px solid var(--ink);
      background: var(--white);
      box-shadow: var(--shadow-md);
      padding: 18px;
      max-width: 560px;
      font-size: clamp(1rem, 2vw, 1.25rem);
      line-height: 1.35;
      transform: rotate(1deg);
    }

    .stats-strip {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }

    .stat {
      border: 4px solid var(--ink);
      background: var(--secondary);
      box-shadow: var(--shadow-sm);
      padding: 12px;
      min-height: 80px;
    }

    .stat:nth-child(2) { background: var(--accent); transform: rotate(-1deg); }
    .stat:nth-child(3) { background: var(--muted); transform: rotate(1deg); }

    .stat strong {
      display: block;
      font-size: 1.8rem;
      line-height: 1;
    }

    .stat span {
      display: block;
      margin-top: 6px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 0.72rem;
    }

    .tool-stack {
      display: grid;
      gap: 22px;
      min-width: 0;
      align-self: start;
    }

    .output-grid {
      display: grid;
      grid-template-columns: minmax(0, 0.92fr) minmax(0, 1.08fr);
      gap: 24px;
      margin-top: 34px;
    }

    .panel {
      position: relative;
      border: 4px solid var(--ink);
      background: var(--white);
      box-shadow: var(--shadow-lg);
      transition: transform 180ms ease-out, box-shadow 180ms ease-out;
    }

    .panel:hover {
      transform: translate(-2px, -2px);
      box-shadow: 16px 16px 0 0 var(--ink);
    }

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      border-bottom: 4px solid var(--ink);
      background: var(--secondary);
      padding: 14px 16px;
    }

    .panel-title {
      margin: 0;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 1rem;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 32px;
      border: 3px solid var(--ink);
      border-radius: 999px;
      background: var(--accent);
      padding: 4px 10px;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      font-size: 0.68rem;
      box-shadow: var(--shadow-sm);
      transform: rotate(3deg);
    }

    .panel-body {
      padding: 18px;
    }

    .pipeline {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin: 0 0 16px;
    }

    .agent {
      display: grid;
      place-items: center;
      min-height: 54px;
      border: 4px solid var(--ink);
      background: var(--white);
      box-shadow: var(--shadow-sm);
      padding: 8px;
      text-align: center;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-size: 0.78rem;
      transition: transform 120ms linear, background 120ms linear, box-shadow 120ms linear;
    }

    .agent:nth-child(2) { background: var(--muted); }
    .agent:nth-child(3) { background: var(--secondary); }
    .agent:nth-child(4) { background: var(--white); }

    .agent.active {
      background: var(--accent);
      transform: translate(-2px, -2px) rotate(-1deg);
      box-shadow: 8px 8px 0 0 var(--ink);
    }

    textarea {
      width: 100%;
      min-height: 230px;
      resize: vertical;
      border: 4px solid var(--ink);
      border-radius: 0;
      background: var(--canvas);
      color: var(--ink);
      padding: 16px;
      font: inherit;
      font-size: 1rem;
      line-height: 1.4;
      box-shadow: inset 4px 4px 0 0 var(--secondary);
    }

    textarea::placeholder { color: var(--ink); }

    textarea:focus {
      outline: none;
      background: var(--secondary);
      box-shadow: var(--shadow-sm);
    }

    a:focus-visible,
    button:focus-visible,
    textarea:focus-visible {
      outline: 4px solid var(--ink);
      outline-offset: 4px;
    }

    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 14px;
    }

    button {
      min-height: 54px;
      border: 4px solid var(--ink);
      border-radius: 0;
      background: var(--accent);
      color: var(--ink);
      box-shadow: var(--shadow-sm);
      cursor: pointer;
      font: inherit;
      font-size: 0.92rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: 10px 16px;
      transition: transform 100ms linear, box-shadow 100ms linear, background 100ms linear;
    }

    button.secondary { background: var(--muted); }

    button:hover {
      background: var(--secondary);
      transform: translate(-1px, -1px);
      box-shadow: 6px 6px 0 0 var(--ink);
    }

    button:active {
      transform: translate(4px, 4px);
      box-shadow: none;
    }

    button:disabled {
      cursor: wait;
      background: var(--white);
      box-shadow: none;
      transform: translate(4px, 4px);
    }

    #status {
      min-height: 52px;
      margin: 16px 0 0;
      border: 4px solid var(--ink);
      background: var(--secondary);
      box-shadow: var(--shadow-sm);
      padding: 12px 14px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }

    #deploy-links {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 14px;
    }

    #deploy-links a,
    .error-sticker {
      display: inline-flex;
      align-items: center;
      min-height: 46px;
      border: 4px solid var(--ink);
      background: var(--secondary);
      box-shadow: var(--shadow-sm);
      padding: 8px 12px;
      margin: 0;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }

    .error-sticker { background: var(--accent); }

    .section {
      border: 4px solid var(--ink);
      background: var(--white);
      box-shadow: var(--shadow-md);
      margin-top: 22px;
    }

    .section h2 {
      margin: 0;
      border-bottom: 4px solid var(--ink);
      background: var(--muted);
      padding: 12px 14px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 0.95rem;
    }

    pre {
      margin: 0;
      max-height: 420px;
      overflow: auto;
      border: 0;
      background: var(--white);
      color: var(--ink);
      padding: 16px;
      font-family: "Space Grotesk", ui-monospace, monospace;
      font-size: 0.9rem;
      font-weight: 700;
      line-height: 1.45;
      white-space: pre-wrap;
    }

    #activity-log {
      min-height: 180px;
      max-height: 280px;
      background: var(--ink);
      color: var(--white);
      text-shadow: 2px 2px 0 var(--accent);
    }

    .decor {
      position: absolute;
      width: 78px;
      height: 78px;
      border: 4px solid var(--ink);
      background: var(--accent);
      box-shadow: var(--shadow-sm);
      right: -18px;
      top: -22px;
      transform: rotate(10deg);
      pointer-events: none;
    }

    .decor::after {
      content: "";
      position: absolute;
      inset: 14px;
      border: 4px solid var(--ink);
      border-radius: 999px;
      background: var(--secondary);
    }

    @media (max-width: 1040px) {
      .hero-grid {
        grid-template-columns: 1fr;
      }

      .hero-copy {
        position: static;
      }

      .output-grid {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 640px) {
      .shell {
        width: min(100% - 20px, 1180px);
        padding-top: 16px;
      }

      .topbar {
        align-items: stretch;
        flex-direction: column;
      }

      .links {
        justify-content: stretch;
      }

      .links a {
        flex: 1 1 120px;
        justify-content: center;
      }

      .stats-strip,
      .pipeline {
        grid-template-columns: 1fr;
      }

      .actions button {
        width: 100%;
      }

      .panel-body {
        padding: 14px;
      }
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        transition: none !important;
        animation: none !important;
      }
    }
  </style>
</head>
<body>
  <main class="shell">
    <nav class="topbar" aria-label="Primary">
      <a class="logo" href="/">
        <span class="logo-mark">AI</span>
        Feature Pipeline
      </a>
      <div class="links">
        <a href="/docs">API Docs</a>
        <a href="/deployments">Deployments</a>
        <a href="/health">Health</a>
      </div>
    </nav>

    <div class="hero-grid">
      <section class="hero-copy" aria-labelledby="page-title">
        <div class="label">Autonomous Dev Loop</div>
        <h1 id="page-title">
          <span class="headline-solid">Autonomous</span>
          <span class="headline-block">Feature</span>
          <span class="headline-stroke">Pipeline</span>
        </h1>
        <p class="hero-note">Paste a feature spec, run the agent loop, watch the QA fight, then open the generated API and UI.</p>
        <div class="stats-strip" aria-label="Pipeline stages">
          <div class="stat"><strong>04</strong><span>Agents</span></div>
          <div class="stat"><strong>08</strong><span>Max loops</span></div>
          <div class="stat"><strong>Live</strong><span>Deploy</span></div>
        </div>
      </section>

      <section class="tool-stack" aria-label="Feature generator">
        <div class="panel">
          <div class="decor" aria-hidden="true"></div>
          <div class="panel-header">
            <h2 class="panel-title">Run Board</h2>
            <span class="badge">Hot path</span>
          </div>
          <div class="panel-body">
            <div class="pipeline">
              <span class="agent" id="a-pm">1. PM</span>
              <span class="agent" id="a-coder">2. Coder</span>
              <span class="agent" id="a-qa">3. QA</span>
              <span class="agent" id="a-fe">4. Frontend</span>
            </div>

            <label class="panel-title" for="feature">Feature Spec</label>
            <textarea id="feature" placeholder="Describe a feature or paste markdown spec..."></textarea>
            <div class="actions">
              <button id="run">Run Pipeline</button>
              <button class="secondary" id="load-example">Load Example Spec</button>
            </div>
            <p id="status">Ready.</p>
            <div id="deploy-links"></div>
          </div>
        </div>
      </section>
    </div>

    <section class="output-grid" aria-label="Pipeline output">
        <div class="section" id="activity-section">
          <h2>Activity Log</h2>
          <pre id="activity-log" aria-live="polite">Ready.</pre>
        </div>

        <div class="section" id="blueprint-section" hidden>
          <h2>Technical Blueprint</h2>
          <pre id="blueprint"></pre>
        </div>

        <div class="section" id="logs-section" hidden>
          <h2>QA Failure Logs</h2>
          <pre id="logs"></pre>
        </div>

        <div class="section" id="output-section" hidden>
          <h2>Pipeline Result</h2>
          <pre id="output"></pre>
        </div>
    </section>
  </main>

  <script>
    const agents = { pm: "a-pm", coder: "a-coder", qa: "a-qa", frontend: "a-fe" };
    const logEl = document.getElementById("activity-log");
    let heartbeatId = null;

    function appendLog(message) {
      const line = "[" + new Date().toLocaleTimeString() + "] " + message;
      const current = logEl.textContent.trim();
      logEl.textContent = current && current !== "Ready." ? current + "\n" + line : line;
      logEl.scrollTop = logEl.scrollHeight;
      console.info("[pipeline]", message);
    }

    function resetLog() {
      logEl.textContent = "";
    }

    function startHeartbeat() {
      let seconds = 0;
      heartbeatId = window.setInterval(() => {
        seconds += 5;
        appendLog("Pipeline still running (" + seconds + "s elapsed)...");
      }, 5000);
    }

    function stopHeartbeat() {
      if (heartbeatId) {
        window.clearInterval(heartbeatId);
        heartbeatId = null;
      }
    }

    async function readJson(res) {
      const text = await res.text();
      if (!text) return {};
      try {
        return JSON.parse(text);
      } catch (e) {
        throw new Error("Response was not valid JSON.");
      }
    }

    function renderBackendEvents(events) {
      if (!Array.isArray(events) || events.length === 0) return;
      appendLog("Backend emitted " + events.length + " events.");
      events.forEach(message => appendLog("backend: " + message));
    }

    function renderAttempts(history) {
      if (!Array.isArray(history) || history.length === 0) return;
      history.forEach(attempt => {
        const exitCode = attempt.exit_code === null || attempt.exit_code === undefined
          ? "n/a"
          : attempt.exit_code;
        appendLog(
          "attempt " + attempt.iteration + ": " + attempt.status + " via " +
          (attempt.agent || "none") + " (exit " + exitCode + ")"
        );
      });
    }

    function setActiveAgent(name) {
      Object.values(agents).forEach(id => document.getElementById(id).classList.remove("active"));
      if (name && agents[name]) document.getElementById(agents[name]).classList.add("active");
    }

    document.getElementById("load-example").addEventListener("click", async () => {
      resetLog();
      appendLog("Loading example spec.");
      try {
        const res = await fetch("/specs/example");
        document.getElementById("feature").value = await res.text();
        appendLog("Example spec loaded.");
      } catch (e) {
        appendLog("Could not load example spec: " + (e.message || e));
      }
    });

    document.getElementById("run").addEventListener("click", async () => {
      const text = document.getElementById("feature").value.trim();
      if (text.length < 10) { alert("Please enter at least 10 characters."); return; }
      const btn = document.getElementById("run");
      btn.disabled = true;
      resetLog();
      appendLog("Starting pipeline request.");
      setActiveAgent("pm");
      document.getElementById("status").textContent = "PM Agent planning...";
      appendLog("PM Agent planning...");
      document.getElementById("deploy-links").innerHTML = "";
      document.getElementById("blueprint-section").hidden = true;
      document.getElementById("logs-section").hidden = true;
      document.getElementById("output-section").hidden = true;

      try {
        appendLog("Submitting request to /generate-feature.");
        startHeartbeat();
        const res = await fetch("/generate-feature", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ feature_request: text }),
        });
        stopHeartbeat();
        appendLog("Received HTTP " + res.status + " from /generate-feature.");
        const data = await readJson(res);
        if (!res.ok) {
          throw new Error(data.detail || "Request failed with HTTP " + res.status);
        }

        setActiveAgent(data.active_agent);
        document.getElementById("status").textContent =
          "Status: " + data.status + " | Correction rounds: " + data.iteration_count;
        appendLog("Pipeline response received for run " + data.run_id + ".");
        renderBackendEvents(data.event_log);
        renderAttempts(data.history);

        if (data.technical_blueprint) {
          document.getElementById("blueprint").textContent = data.technical_blueprint;
          document.getElementById("blueprint-section").hidden = false;
        }

        if (data.status === "success") {
          setActiveAgent("frontend");
          document.getElementById("deploy-links").innerHTML =
            '<a href="' + data.live_api_path + '/docs" target="_blank">Live Swagger UI</a>' +
            '<a href="' + data.live_ui_path + '" target="_blank">Generated UI</a>';
        } else if (data.status === "failed" && data.test_logs) {
          document.getElementById("deploy-links").innerHTML =
            '<p class="error-sticker">See QA failure logs below.</p>';
        }

        if (data.status === "failed" && data.test_logs) {
          document.getElementById("logs").textContent = data.test_logs;
          document.getElementById("logs-section").hidden = false;
        }

        document.getElementById("output").textContent = JSON.stringify(data, null, 2);
        document.getElementById("output-section").hidden = false;
      } catch (e) {
        stopHeartbeat();
        setActiveAgent(null);
        document.getElementById("status").textContent = "Request failed.";
        appendLog("Request failed: " + (e.message || e));
        console.error(e);
      } finally {
        stopHeartbeat();
        btn.disabled = false;
      }
    });
  </script>
</body>
</html>"""
