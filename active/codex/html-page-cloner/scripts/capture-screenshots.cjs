#!/usr/bin/env node
const fs = require("fs");
const http = require("http");
const net = require("net");
const path = require("path");
const { spawn } = require("child_process");
const { pathToFileURL } = require("url");

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith("--")) continue;
    const key = token.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith("--")) args[key] = "true";
    else {
      args[key] = next;
      i += 1;
    }
  }
  return args;
}

function boolArg(value, defaultValue) {
  if (value === undefined) return defaultValue;
  return !/^(false|0|no)$/i.test(String(value));
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function removeDirRetry(dirPath, attempts = 8) {
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      fs.rmSync(dirPath, { recursive: true, force: true });
      return;
    } catch (err) {
      if (attempt === attempts) throw err;
      await delay(250 * attempt);
    }
  }
}

async function waitForExit(child, timeoutMs = 5000) {
  if (child.exitCode !== null || child.signalCode !== null) return;
  await Promise.race([
    new Promise((resolve) => child.once("exit", resolve)),
    delay(timeoutMs),
  ]);
}

function parseViewport(value, fallback) {
  if (!value) return fallback;
  const match = String(value).match(/^(\d+)x(\d+)$/i);
  if (!match) throw new Error(`Invalid viewport "${value}", expected WIDTHxHEIGHT`);
  return { width: Number(match[1]), height: Number(match[2]) };
}

function httpJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = "";
      res.on("data", (chunk) => { data += chunk; });
      res.on("end", () => {
        try { resolve(JSON.parse(data)); }
        catch (err) { reject(err); }
      });
    }).on("error", reject);
  });
}

async function waitForJson(url, timeoutMs = 10000) {
  const start = Date.now();
  let lastError;
  while (Date.now() - start < timeoutMs) {
    try { return await httpJson(url); }
    catch (err) {
      lastError = err;
      await delay(250);
    }
  }
  throw lastError || new Error(`Timed out waiting for ${url}`);
}

function freePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.listen(0, "127.0.0.1", () => {
      const { port } = server.address();
      server.close(() => resolve(port));
    });
    server.on("error", reject);
  });
}

class CdpClient {
  constructor(wsUrl) {
    if (typeof WebSocket === "undefined") {
      throw new Error("This script requires a Node runtime with built-in WebSocket.");
    }
    this.ws = new WebSocket(wsUrl);
    this.nextId = 1;
    this.pending = new Map();
    this.events = [];
    this.ws.addEventListener("message", (event) => {
      const msg = JSON.parse(event.data);
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) reject(new Error(JSON.stringify(msg.error)));
        else resolve(msg.result || {});
      } else if (msg.method) {
        this.events.push(msg);
      }
    });
  }

  async open() {
    await new Promise((resolve, reject) => {
      this.ws.addEventListener("open", resolve, { once: true });
      this.ws.addEventListener("error", reject, { once: true });
    });
  }

  send(method, params = {}) {
    const id = this.nextId;
    this.nextId += 1;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
    });
  }

  drainEvents() {
    const events = this.events;
    this.events = [];
    return events;
  }

  close() {
    this.ws.close();
  }
}

function collectCdpErrors(events) {
  const out = [];
  for (const event of events) {
    if (event.method === "Runtime.exceptionThrown") {
      out.push(event.params?.exceptionDetails?.text || "Runtime exception");
    }
    if (event.method === "Log.entryAdded" && ["error", "warning"].includes(event.params?.entry?.level)) {
      out.push(event.params.entry.text);
    }
    if (event.method === "Runtime.consoleAPICalled" && event.params?.type === "error") {
      const text = (event.params.args || []).map((arg) => arg.value || arg.description || "").join(" ");
      out.push(text || "console.error");
    }
  }
  return out.filter(Boolean);
}

async function setupClient(client) {
  await client.send("Page.enable");
  await client.send("Runtime.enable");
  await client.send("Log.enable");
  await client.send("Runtime.addBinding", { name: "__cloneReportError" }).catch(() => {});
  await client.send("Page.addScriptToEvaluateOnNewDocument", {
    source: `
      window.__cloneConsoleErrors = [];
      window.addEventListener("error", (event) => window.__cloneConsoleErrors.push(event.message || "error"));
      window.addEventListener("unhandledrejection", (event) => window.__cloneConsoleErrors.push(String(event.reason || "unhandled rejection")));
    `,
  });
}

async function loadAndCapture(client, targetUrl, name, metrics, outDir, waitMs, checks) {
  client.drainEvents();
  await client.send("Emulation.setDeviceMetricsOverride", metrics);
  await client.send("Page.navigate", { url: targetUrl });
  await delay(waitMs);

  const expression = `(() => {
    const width = Math.max(document.documentElement.scrollWidth, document.body ? document.body.scrollWidth : 0);
    const height = Math.max(document.documentElement.scrollHeight, document.body ? document.body.scrollHeight : 0);
    const bodyText = document.body ? document.body.innerText : "";
    return {
      title: document.title,
      url: location.href,
      width,
      height,
      viewportWidth: window.innerWidth,
      viewportHeight: window.innerHeight,
      hasHero: ${JSON.stringify(checks.heroText)} ? bodyText.includes(${JSON.stringify(checks.heroText)}) : null,
      hasFaq: ${JSON.stringify(checks.faqText)} ? bodyText.includes(${JSON.stringify(checks.faqText)}) : null,
      horizontalOverflow: width > window.innerWidth + 2,
      consoleErrors: window.__cloneConsoleErrors || []
    };
  })()`;
  const layout = await client.send("Runtime.evaluate", { returnByValue: true, expression });
  const value = layout.result.value;
  const width = Math.max(1, Math.min(Math.ceil(value.width), metrics.width));
  const height = Math.max(1, Math.ceil(value.height));
  const screenshot = await client.send("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport: true,
    clip: { x: 0, y: 0, width, height, scale: 1 },
  });
  fs.mkdirSync(outDir, { recursive: true });
  const outPath = path.join(outDir, `${name}.png`);
  fs.writeFileSync(outPath, Buffer.from(screenshot.data, "base64"));
  const cdpErrors = collectCdpErrors(client.drainEvents());
  const consoleErrors = [...new Set([...(value.consoleErrors || []), ...cdpErrors])];
  return {
    name,
    output: outPath,
    bytes: fs.statSync(outPath).size,
    viewport: { width: metrics.width, height: metrics.height, mobile: !!metrics.mobile },
    page: { ...value, consoleErrors },
  };
}

function writeMarkdownReport(report, outPath) {
  const lines = [
    "# Screenshot Validation Report",
    "",
    `Generated: ${report.generatedAt}`,
    "",
    "| View | Bytes | Width | Height | Overflow | Console errors |",
    "| --- | ---: | ---: | ---: | --- | ---: |",
  ];
  for (const result of report.results) {
    lines.push(`| ${result.name} | ${result.bytes} | ${result.page.width} | ${result.page.height} | ${result.page.horizontalOverflow} | ${result.page.consoleErrors.length} |`);
  }
  lines.push("", "## Outputs", "");
  for (const result of report.results) lines.push(`- ${result.output}`);
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, `${lines.join("\n")}\n`, "utf8");
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const htmlPath = args.html ? path.resolve(args.html) : "";
  const targetUrl = args.url || (htmlPath ? pathToFileURL(htmlPath).href : "");
  if (!targetUrl) throw new Error("Provide --html or --url");
  if (htmlPath && (!fs.existsSync(htmlPath) || !fs.statSync(htmlPath).isFile())) {
    throw new Error(`HTML file not found: ${htmlPath}`);
  }

  const chromePath = path.resolve(args.chrome || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe");
  if (!fs.existsSync(chromePath)) throw new Error(`Chrome not found: ${chromePath}`);

  const outDir = path.resolve(args["out-dir"] || path.join(path.dirname(htmlPath || process.cwd()), "screenshots"));
  const reportPath = path.resolve(args.report || path.join(outDir, "..", "validation", "screenshot-report.json"));
  const mdReportPath = path.resolve(args["md-report"] || reportPath.replace(/\.json$/i, ".md"));
  const waitMs = Number(args.wait || 9000);
  const strict = boolArg(args.strict, true);
  const prefix = args.prefix || (htmlPath ? path.basename(htmlPath, path.extname(htmlPath)) : "page");
  const desktop = parseViewport(args.desktop, { width: 1920, height: 1080 });
  const mobile = parseViewport(args.mobile, { width: 538, height: 844 });
  const port = args.port ? Number(args.port) : await freePort();
  const userDataDir = path.join(outDir, `.chrome-profile-${process.pid}`);
  const checks = {
    heroText: args["hero-text"] || "",
    faqText: args["faq-text"] || "",
  };

  fs.mkdirSync(outDir, { recursive: true });
  await removeDirRetry(userDataDir);

  const chrome = spawn(chromePath, [
    "--headless=new",
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${userDataDir}`,
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "about:blank",
  ], { stdio: "ignore" });

  const results = [];
  try {
    await waitForJson(`http://127.0.0.1:${port}/json/version`, 15000);
    const targets = await waitForJson(`http://127.0.0.1:${port}/json/list`, 15000);
    const page = targets.find((target) => target.type === "page");
    if (!page) throw new Error("No page target from Chrome");
    const client = new CdpClient(page.webSocketDebuggerUrl);
    await client.open();
    await setupClient(client);
    results.push(await loadAndCapture(client, targetUrl, `${prefix}-desktop-${desktop.width}`, {
      width: desktop.width,
      height: desktop.height,
      deviceScaleFactor: 1,
      mobile: false,
    }, outDir, waitMs, checks));
    results.push(await loadAndCapture(client, targetUrl, `${prefix}-mobile-${mobile.width}`, {
      width: mobile.width,
      height: mobile.height,
      deviceScaleFactor: 1,
      mobile: true,
    }, outDir, waitMs, checks));
    client.close();
  } finally {
    chrome.kill();
    await waitForExit(chrome);
    await removeDirRetry(userDataDir);
  }

  const report = {
    generatedAt: new Date().toISOString(),
    target: targetUrl,
    html: htmlPath || null,
    results,
  };
  fs.mkdirSync(path.dirname(reportPath), { recursive: true });
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2), "utf8");
  writeMarkdownReport(report, mdReportPath);
  console.log(JSON.stringify(report, null, 2));

  const hardFailure = results.some((item) =>
    item.bytes <= 0 ||
    item.page.horizontalOverflow ||
    (item.page.consoleErrors || []).length > 0
  );
  if (strict && hardFailure) process.exitCode = 2;
}

main().catch((err) => {
  console.error(err.stack || err.message || err);
  process.exit(1);
});
