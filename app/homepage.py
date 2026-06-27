HOME_PAGE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Autonomous Feature Pipeline</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Sans+3:wght@400;500;600&display=block" rel="stylesheet">
  <style>
    :root {
      --bg: #F9F8F4;
      --fg: #2D3A31;
      --sage: #8C9A84;
      --clay: #DCCFC2;
      --stone: #E6E2DA;
      --terracotta: #C27B66;
      --paper: rgba(255, 255, 255, 0.78);
      --shadow: 0 20px 40px -10px rgba(45, 58, 49, 0.10);
      --shadow-soft: 0 10px 15px -3px rgba(45, 58, 49, 0.06);
    }

    * { box-sizing: border-box; }
    [hidden] { display: none !important; }

    html {
      scroll-behavior: smooth;
    }

    body {
      margin: 0;
      min-height: 100vh;
      color: var(--fg);
      background:
        radial-gradient(circle at top left, rgba(140, 154, 132, 0.10), transparent 28%),
        radial-gradient(circle at bottom right, rgba(194, 123, 102, 0.10), transparent 26%),
        linear-gradient(180deg, rgba(249, 248, 244, 0.95), rgba(249, 248, 244, 1));
      font-family: "Source Sans 3", system-ui, sans-serif;
      font-weight: 400;
      line-height: 1.6;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      opacity: 0.015;
      z-index: 0;
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
      background-repeat: repeat;
    }

    a {
      color: inherit;
      text-decoration: none;
    }

    button,
    textarea,
    input {
      font: inherit;
    }

    .shell {
      position: relative;
      z-index: 1;
      width: min(1280px, calc(100% - 48px));
      margin: 0 auto;
      padding: 28px 0 64px;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      margin-bottom: 28px;
    }

    .logo {
      display: inline-flex;
      align-items: center;
      gap: 12px;
      padding: 14px 18px;
      border: 1px solid var(--stone);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.66);
      box-shadow: var(--shadow-soft);
      backdrop-filter: blur(8px);
      font-family: "Playfair Display", serif;
      font-size: 1.05rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      transition: transform 500ms ease-out, box-shadow 500ms ease-out;
    }

    .logo:hover {
      transform: translateY(-1px);
      box-shadow: var(--shadow);
    }

    .logo-mark {
      display: inline-grid;
      place-items: center;
      width: 34px;
      height: 34px;
      border-radius: 999px;
      background: var(--sage);
      color: white;
      font-family: "Source Sans 3", sans-serif;
      font-size: 0.8rem;
      font-weight: 600;
      letter-spacing: 0.18em;
    }

    .links {
      display: flex;
      flex-wrap: wrap;
      justify-content: flex-end;
      gap: 10px;
    }

    .links a {
      padding: 10px 16px;
      border: 1px solid var(--stone);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.7);
      box-shadow: var(--shadow-soft);
      font-size: 0.84rem;
      font-weight: 500;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      transition: transform 300ms ease-out, background 300ms ease-out, box-shadow 300ms ease-out, border-color 300ms ease-out;
    }

    .links a:hover {
      transform: translateY(-1px);
      border-color: rgba(140, 154, 132, 0.65);
      background: rgba(227, 220, 209, 0.82);
      box-shadow: var(--shadow);
    }

    .hero-grid {
      display: grid;
      grid-template-columns: minmax(0, 0.92fr) minmax(380px, 1.08fr);
      gap: 36px;
      align-items: start;
      margin-bottom: 34px;
    }

    .hero-copy {
      display: grid;
      gap: 18px;
      padding-top: 12px;
    }

    .eyebrow {
      width: max-content;
      padding: 10px 16px;
      border-radius: 999px;
      background: rgba(220, 207, 194, 0.58);
      border: 1px solid var(--stone);
      box-shadow: var(--shadow-soft);
      font-size: 0.8rem;
      font-weight: 600;
      letter-spacing: 0.22em;
      text-transform: uppercase;
    }

    h1 {
      margin: 0;
      color: var(--fg);
      font-family: "Playfair Display", serif;
      font-size: clamp(3.4rem, 6.5vw, 7rem);
      font-weight: 700;
      line-height: 0.95;
      letter-spacing: -0.03em;
    }

    h1 em {
      font-style: italic;
      color: var(--terracotta);
    }

    .hero-note {
      max-width: 620px;
      margin: 0;
      padding: 22px 24px;
      border: 1px solid var(--stone);
      border-radius: 40px 40px 16px 40px;
      background: rgba(255, 255, 255, 0.78);
      box-shadow: var(--shadow-soft);
      font-size: 1.08rem;
      line-height: 1.75;
      backdrop-filter: blur(6px);
    }

    .stats-strip {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 10px;
    }

    .stat {
      padding: 18px 18px 16px;
      border: 1px solid var(--stone);
      border-radius: 28px;
      background: rgba(255, 255, 255, 0.74);
      box-shadow: var(--shadow-soft);
      min-height: 104px;
      transition: transform 500ms ease-out, box-shadow 500ms ease-out;
    }

    .stat:nth-child(2) {
      transform: translateY(10px);
      background: rgba(220, 207, 194, 0.45);
    }

    .stat:nth-child(3) {
      transform: translateY(22px);
      background: rgba(140, 154, 132, 0.14);
    }

    .stat strong {
      display: block;
      color: var(--fg);
      font-family: "Playfair Display", serif;
      font-size: 2.2rem;
      font-weight: 700;
      line-height: 1;
    }

    .stat span {
      display: block;
      margin-top: 8px;
      color: rgba(45, 58, 49, 0.86);
      font-size: 0.78rem;
      font-weight: 600;
      letter-spacing: 0.18em;
      text-transform: uppercase;
    }

    .tool-stack {
      display: grid;
      gap: 22px;
      align-self: start;
    }

    .panel {
      position: relative;
      border-radius: 40px;
      border: 1px solid var(--stone);
      background: rgba(255, 255, 255, 0.80);
      box-shadow: var(--shadow);
      overflow: hidden;
      backdrop-filter: blur(8px);
    }

    .panel::before {
      content: "";
      position: absolute;
      inset: 0;
      pointer-events: none;
      background:
        radial-gradient(circle at 18% 14%, rgba(140, 154, 132, 0.14), transparent 18%),
        radial-gradient(circle at 85% 8%, rgba(194, 123, 102, 0.12), transparent 16%);
    }

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 20px 22px 16px;
      border-bottom: 1px solid var(--stone);
    }

    .panel-title {
      margin: 0;
      color: var(--fg);
      font-family: "Playfair Display", serif;
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: 0.04em;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 14px;
      border-radius: 999px;
      background: rgba(140, 154, 132, 0.16);
      color: var(--fg);
      border: 1px solid rgba(140, 154, 132, 0.35);
      font-size: 0.76rem;
      font-weight: 600;
      letter-spacing: 0.18em;
      text-transform: uppercase;
    }

    .panel-body {
      position: relative;
      padding: 22px;
    }

    .pipeline {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }

    .agent {
      display: grid;
      place-items: center;
      min-height: 54px;
      padding: 12px 10px;
      border-radius: 999px;
      border: 1px solid var(--stone);
      background: rgba(255, 255, 255, 0.82);
      color: var(--fg);
      box-shadow: var(--shadow-soft);
      text-align: center;
      font-size: 0.76rem;
      font-weight: 600;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      transition: transform 300ms ease-out, background 300ms ease-out, box-shadow 300ms ease-out, border-color 300ms ease-out;
    }

    .agent:nth-child(2) { background: rgba(220, 207, 194, 0.60); }
    .agent:nth-child(3) { background: rgba(140, 154, 132, 0.18); }
    .agent:nth-child(4) { background: rgba(255, 255, 255, 0.86); }

    .agent.active {
      border-color: rgba(194, 123, 102, 0.65);
      background: rgba(194, 123, 102, 0.18);
      transform: translateY(-2px);
      box-shadow: var(--shadow);
    }

    .field-label {
      display: block;
      margin: 0 0 10px;
      color: rgba(45, 58, 49, 0.88);
      font-size: 0.8rem;
      font-weight: 600;
      letter-spacing: 0.18em;
      text-transform: uppercase;
    }

    textarea {
      width: 100%;
      min-height: 240px;
      resize: vertical;
      border: 1px solid var(--stone);
      border-radius: 32px;
      background: rgba(255, 255, 255, 0.92);
      color: var(--fg);
      padding: 18px 20px;
      font: inherit;
      font-size: 1rem;
      line-height: 1.7;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7), var(--shadow-soft);
    }

    textarea::placeholder {
      color: rgba(45, 58, 49, 0.46);
    }

    textarea:focus {
      outline: none;
      border-color: rgba(140, 154, 132, 0.8);
      box-shadow: 0 0 0 3px rgba(140, 154, 132, 0.18), var(--shadow-soft);
    }

    a:focus-visible,
    button:focus-visible,
    textarea:focus-visible {
      outline: 2px solid var(--sage);
      outline-offset: 3px;
    }

    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 16px;
    }

    button {
      min-height: 48px;
      padding: 12px 20px;
      border: 1px solid transparent;
      border-radius: 999px;
      background: var(--fg);
      color: white;
      box-shadow: var(--shadow-soft);
      cursor: pointer;
      font-size: 0.8rem;
      font-weight: 600;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      transition: transform 300ms ease-out, background 300ms ease-out, box-shadow 300ms ease-out;
    }

    button.secondary {
      background: transparent;
      color: var(--sage);
      border-color: var(--sage);
    }

    button:hover {
      transform: translateY(-1px);
      box-shadow: var(--shadow);
    }

    button:active {
      transform: translateY(0);
      box-shadow: var(--shadow-soft);
    }

    button:disabled {
      opacity: 0.7;
      cursor: wait;
    }

    #status {
      margin: 16px 0 0;
      padding: 12px 16px;
      border-radius: 24px;
      border: 1px solid var(--stone);
      background: rgba(220, 207, 194, 0.48);
      color: var(--fg);
      font-size: 0.98rem;
      font-weight: 500;
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
      min-height: 44px;
      padding: 10px 16px;
      border-radius: 999px;
      border: 1px solid rgba(140, 154, 132, 0.45);
      background: rgba(255, 255, 255, 0.8);
      box-shadow: var(--shadow-soft);
      font-size: 0.78rem;
      font-weight: 600;
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }

    .error-sticker {
      background: rgba(194, 123, 102, 0.18);
      border-color: rgba(194, 123, 102, 0.3);
    }

    .output-grid {
      display: grid;
      grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
      gap: 18px;
      margin-top: 24px;
    }

    .section {
      border-radius: 32px;
      border: 1px solid var(--stone);
      background: rgba(255, 255, 255, 0.8);
      box-shadow: var(--shadow-soft);
      overflow: hidden;
    }

    .section h2 {
      margin: 0;
      padding: 14px 18px;
      border-bottom: 1px solid var(--stone);
      background: rgba(220, 207, 194, 0.35);
      color: var(--fg);
      font-family: "Playfair Display", serif;
      font-size: 1.1rem;
      font-weight: 700;
      letter-spacing: 0.03em;
    }

    pre {
      margin: 0;
      max-height: 420px;
      overflow: auto;
      padding: 18px;
      white-space: pre-wrap;
      color: var(--fg);
      font-family: "Source Sans 3", system-ui, sans-serif;
      font-size: 0.96rem;
      font-weight: 400;
      line-height: 1.75;
    }

    #activity-log {
      min-height: 180px;
      background: linear-gradient(180deg, rgba(45, 58, 49, 0.95), rgba(45, 58, 49, 0.92));
      color: rgba(255, 255, 255, 0.96);
    }

    .spacer {
      display: none;
    }

    @media (max-width: 1100px) {
      .hero-grid,
      .output-grid {
        grid-template-columns: 1fr;
      }

      .hero-copy {
        order: 1;
      }
    }

    @media (max-width: 720px) {
      .shell {
        width: min(100% - 24px, 1280px);
        padding-top: 20px;
      }

      .topbar {
        flex-direction: column;
        align-items: stretch;
      }

      .links {
        justify-content: stretch;
      }

      .links a {
        flex: 1 1 120px;
        justify-content: center;
      }

      h1 {
        font-size: clamp(2.8rem, 12vw, 4.1rem);
      }

      .stats-strip,
      .pipeline {
        grid-template-columns: 1fr;
      }

      .panel-body {
        padding: 18px;
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
        <div class="eyebrow">Autonomous Dev Loop</div>
        <h1 id="page-title">
          <span>Autonomous</span>
          <span>Feature</span>
          <span><em>Pipeline</em></span>
        </h1>
        <p class="hero-note">Paste a feature spec, run the agent loop, watch the QA round-trip, then open the generated API and UI.</p>
        <div class="stats-strip" aria-label="Pipeline stages">
          <div class="stat"><strong>04</strong><span>Agents</span></div>
          <div class="stat"><strong>08</strong><span>Max loops</span></div>
          <div class="stat"><strong>Live</strong><span>Deploy</span></div>
        </div>
      </section>

      <section class="tool-stack" aria-label="Feature generator">
        <div class="panel">
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

            <label class="field-label" for="feature">Feature Spec</label>
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
