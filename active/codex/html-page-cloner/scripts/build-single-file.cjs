#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

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

function fail(message) {
  console.error(message);
  process.exit(1);
}

function ensureFile(filePath, label) {
  if (!filePath) fail(`Missing --${label}`);
  const resolved = path.resolve(filePath);
  if (!fs.existsSync(resolved) || !fs.statSync(resolved).isFile()) {
    fail(`${label} not found: ${resolved}`);
  }
  return resolved;
}

function ensureDir(dirPath, label) {
  if (!dirPath) fail(`Missing --${label}`);
  const resolved = path.resolve(dirPath);
  if (!fs.existsSync(resolved) || !fs.statSync(resolved).isDirectory()) {
    fail(`${label} not found: ${resolved}`);
  }
  return resolved;
}

function sanitizeName(value) {
  return value
    .toLowerCase()
    .replace(/\.[a-z0-9]+$/i, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80) || "page-clone";
}

function boolArg(value, defaultValue) {
  if (value === undefined) return defaultValue;
  return !/^(false|0|no)$/i.test(String(value));
}

function mimeType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === ".css" || path.basename(filePath) === "css") return "text/css";
  if (ext === ".js" || ext === ".mjs" || ext === ".download" || path.basename(filePath) === "js") return "application/javascript";
  if (ext === ".svg") return "image/svg+xml";
  if (ext === ".png") return "image/png";
  if (ext === ".jpg" || ext === ".jpeg") return "image/jpeg";
  if (ext === ".webp") return "image/webp";
  if (ext === ".gif") return "image/gif";
  if (ext === ".avif") return "image/avif";
  if (ext === ".ico") return "image/x-icon";
  if (ext === ".woff2") return "font/woff2";
  if (ext === ".woff") return "font/woff";
  if (ext === ".ttf") return "font/ttf";
  if (ext === ".otf") return "font/otf";
  if (ext === ".mp4") return "video/mp4";
  if (ext === ".webm") return "video/webm";
  return "application/octet-stream";
}

function dataUriFromBuffer(buf, mime) {
  if (mime === "image/svg+xml") {
    const svg = buf.toString("utf8")
      .replace(/\r?\n/g, " ")
      .replace(/>\s+</g, "><")
      .replace(/"/g, "'");
    return `data:${mime},${encodeURIComponent(svg)}`;
  }
  return `data:${mime};base64,${buf.toString("base64")}`;
}

function dataUri(filePath) {
  return dataUriFromBuffer(fs.readFileSync(filePath), mimeType(filePath));
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function htmlEscape(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function decodeSafe(value) {
  try { return decodeURIComponent(value); }
  catch (_) { return value; }
}

function encodePathSegments(value) {
  return value.split("/").map((part) => encodeURIComponent(part)).join("/");
}

function walkFiles(rootDir) {
  const out = [];
  for (const item of fs.readdirSync(rootDir, { withFileTypes: true })) {
    const full = path.join(rootDir, item.name);
    if (item.isDirectory()) out.push(...walkFiles(full));
    else if (item.isFile()) out.push(full);
  }
  return out;
}

function buildAssetRefs(assetsDir) {
  const assetBase = path.basename(assetsDir);
  const encodedBase = encodePathSegments(assetBase);
  const files = walkFiles(assetsDir).sort((a, b) => b.length - a.length);
  return files.map((filePath) => {
    const rel = path.relative(assetsDir, filePath).split(path.sep).join("/");
    const encodedRel = encodePathSegments(rel);
    const refs = [
      `./${assetBase}/${rel}`,
      `${assetBase}/${rel}`,
      `./${encodedBase}/${encodedRel}`,
      `${encodedBase}/${encodedRel}`,
      `./${assetBase}/${encodedRel}`,
      `${assetBase}/${encodedRel}`,
    ];
    return { filePath, rel, refs: [...new Set(refs)].sort((a, b) => b.length - a.length) };
  });
}

function replaceLiteralAll(text, needle, replacement) {
  return text.split(needle).join(replacement);
}

function stripRuntimeScripts(html) {
  return html
    .replace(/<script\b(?![^>]*type=["']application\/ld\+json["'])[\s\S]*?<\/script>/gi, "")
    .replace(/<link[^>]+rel=["']preconnect["'][^>]*>/gi, "")
    .replace(/<link[^>]+rel=["']preload["'][^>]*>/gi, "")
    .replace(/<link[^>]+rel=["']prefetch["'][^>]*>/gi, "")
    .replace(/<link[^>]+rel=["']alternate["'][^>]*>/gi, "")
    .replace(/<link[^>]+href=["']https:\/\/www\.google-analytics\.com\/?["'][^>]*>/gi, "")
    .replace(/<link[^>]+href=["']https:\/\/www\.googletagmanager\.com[^"']*["'][^>]*>/gi, "");
}

function normalizeStaticHtml(html) {
  return html
    .replace(/\sloading=["']lazy["']/gi, ' loading="eager"')
    .replace(/\sfetchpriority=["']auto["']/gi, ' fetchpriority="high"')
    .replace(/<img\b(?![^>]*\bdecoding=)/gi, '<img decoding="async"');
}

function assetPathFromRef(ref, assetsDir) {
  if (!ref || /^(data:|blob:|https?:|mailto:|tel:|#)/i.test(ref)) return null;
  let clean = ref.replace(/&amp;/g, "&").replace(/\\/g, "/").trim();
  clean = clean.replace(/[?#].*$/, "");
  clean = clean.replace(/^["']|["']$/g, "");
  if (clean.startsWith("file:")) {
    try {
      const url = new URL(clean);
      const localPath = decodeSafe(url.pathname).replace(/^\/([A-Za-z]:\/)/, "$1");
      const resolved = path.resolve(localPath);
      return resolved.startsWith(path.resolve(assetsDir)) && fs.existsSync(resolved) ? resolved : null;
    } catch (_) {
      return null;
    }
  }
  clean = decodeSafe(clean).replace(/^\.\//, "").replace(/^\/+/, "");
  const assetBase = path.basename(assetsDir);
  if (clean.startsWith(`${assetBase}/`)) clean = clean.slice(assetBase.length + 1);
  const candidate = path.join(assetsDir, clean);
  if (fs.existsSync(candidate) && fs.statSync(candidate).isFile()) return candidate;
  return null;
}

function extractAttr(tag, name) {
  const re = new RegExp(`\\b${name}\\s*=\\s*(["'])(.*?)\\1`, "i");
  const match = tag.match(re);
  return match ? match[2] : "";
}

function inlineStylesheets(html, assetsDir, assetRefs) {
  return html.replace(/<link\b[^>]*>/gi, (tag) => {
    const rel = extractAttr(tag, "rel").toLowerCase();
    const href = extractAttr(tag, "href");
    if (!rel.includes("stylesheet")) return tag;
    const filePath = assetPathFromRef(href, assetsDir);
    if (!filePath) return tag;
    let css = fs.readFileSync(filePath, "utf8");
    css = inlineLocalRefs(css, assetRefs);
    return `<style data-inlined-from="${htmlEscape(path.basename(filePath))}">\n${css}\n</style>`;
  });
}

function inlineLocalRefs(text, assetRefs) {
  let out = text;
  for (const item of assetRefs) {
    const uri = dataUri(item.filePath);
    for (const ref of item.refs) {
      out = replaceLiteralAll(out, ref, uri);
      out = replaceLiteralAll(out, ref.replace(/&/g, "&amp;"), uri);
    }
  }
  return out;
}

function rewriteMirrorRefs(html, assetsDir, mirrorAssetsName) {
  const assetBase = path.basename(assetsDir);
  const encodedBase = encodePathSegments(assetBase);
  const fromPrefixes = [`./${assetBase}/`, `${assetBase}/`, `./${encodedBase}/`, `${encodedBase}/`];
  let out = html;
  for (const prefix of fromPrefixes) out = replaceLiteralAll(out, prefix, `./${mirrorAssetsName}/`);
  return out;
}

function isRemoteVideoAsset(url, embedMp4) {
  let parsed;
  try { parsed = new URL(url.replace(/&amp;/g, "&")); }
  catch (_) { return false; }
  if (/\.(mp4|webm|mov)($|\?)/i.test(parsed.pathname)) return !embedMp4;
  return false;
}

function isRemoteEmbeddableAsset(url, embedMp4) {
  let parsed;
  try { parsed = new URL(url.replace(/&amp;/g, "&")); }
  catch (_) { return false; }
  const host = parsed.hostname.toLowerCase();
  const pathname = parsed.pathname.toLowerCase();
  if (/\.(mp4|webm|mov)($|\?)/i.test(pathname)) return !!embedMp4;
  if (/\.(png|jpe?g|webp|gif|avif|svg|ico|woff2?|ttf|otf)($|\?)/i.test(pathname)) return true;
  if (host === "lh3.googleusercontent.com") return true;
  if (host === "fonts.gstatic.com") return true;
  if (host.endsWith(".gstatic.com") && /\/s\//.test(pathname)) return true;
  if (host === "storage.googleapis.com" && !/\.(html?|json|js)($|\?)/i.test(pathname)) return true;
  if (host === "one.google.com" && /\/(favicon-|public\/)/.test(pathname)) return true;
  return false;
}

function extensionFromMime(mime) {
  if (!mime) return ".bin";
  if (mime.includes("image/png")) return ".png";
  if (mime.includes("image/jpeg")) return ".jpg";
  if (mime.includes("image/svg+xml")) return ".svg";
  if (mime.includes("image/webp")) return ".webp";
  if (mime.includes("image/gif")) return ".gif";
  if (mime.includes("image/avif")) return ".avif";
  if (mime.includes("font/woff2")) return ".woff2";
  if (mime.includes("font/woff")) return ".woff";
  if (mime.includes("font/ttf")) return ".ttf";
  if (mime.includes("font/otf")) return ".otf";
  if (mime.includes("video/mp4")) return ".mp4";
  return ".bin";
}

async function fetchRemoteAsset(url, remoteCache) {
  fs.mkdirSync(remoteCache, { recursive: true });
  const cleanUrl = url.replace(/&amp;/g, "&");
  const hash = crypto.createHash("sha1").update(cleanUrl).digest("hex");
  const metaPath = path.join(remoteCache, `${hash}.json`);
  if (fs.existsSync(metaPath)) {
    const meta = JSON.parse(fs.readFileSync(metaPath, "utf8"));
    if (meta.file && fs.existsSync(meta.file)) {
      const buf = fs.readFileSync(meta.file);
      return { uri: dataUriFromBuffer(buf, meta.mime), bytes: buf.length, cached: true };
    }
  }
  const res = await fetch(cleanUrl, {
    headers: {
      "User-Agent": "Mozilla/5.0 local page clone",
      "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,font/*,*/*;q=0.8",
    },
  });
  if (!res.ok) throw new Error(`Fetch failed ${res.status} ${cleanUrl}`);
  const mime = (res.headers.get("content-type") || "application/octet-stream").split(";")[0].trim();
  const buf = Buffer.from(await res.arrayBuffer());
  const file = path.join(remoteCache, `${hash}${extensionFromMime(mime)}`);
  fs.writeFileSync(file, buf);
  fs.writeFileSync(metaPath, JSON.stringify({ url: cleanUrl, mime, file }, null, 2));
  return { uri: dataUriFromBuffer(buf, mime), bytes: buf.length, cached: false };
}

async function inlineRemoteAssets(html, remoteCache, embedRemote, embedMp4) {
  if (!embedRemote) return { html, stats: [] };
  const urls = [...new Set([...html.matchAll(/https?:\/\/[^"'()<>\s]+/g)].map((m) => m[0]))]
    .filter((url) => isRemoteEmbeddableAsset(url, embedMp4));
  const stats = [];
  let out = html;
  for (const url of urls) {
    try {
      const asset = await fetchRemoteAsset(url, remoteCache);
      out = out.replace(new RegExp(escapeRegExp(url), "g"), asset.uri);
      out = out.replace(new RegExp(escapeRegExp(url.replace(/&/g, "&amp;")), "g"), asset.uri);
      stats.push({ url, bytes: asset.bytes, cached: asset.cached, status: "inlined" });
    } catch (err) {
      stats.push({ url, status: "failed", error: err.message });
    }
  }
  return { html: out, stats };
}

function injectCloneEnhancements(html) {
  const style = `
<style id="clone-local-enhancements">
  html { scroll-behavior: smooth; }
  bds-drawer { display: none; }
  .planCard_nvuF7.is-open bds-drawer { display: block; }
  .planCard_nvuF7 .planFeaturesCollapseLabel_zp93c { display: none; }
  .planCard_nvuF7.is-open .planFeaturesExpandLabel_NGti3 { display: none; }
  .planCard_nvuF7.is-open .planFeaturesCollapseLabel_zp93c { display: inline-flex; }
  mws-accordion-item .accordionItemContentWrap_9CuCo { display: none; }
  mws-accordion-item.is-open .accordionItemContentWrap_9CuCo { display: block; }
  mws-accordion-item.is-open .accordionItemContent_vbHYu { display: block; }
  .expandAllButton_pKRBZ[data-state="collapse-all"] .expandAllLabelExpand_ib0ak { display: none; }
  .expandAllButton_pKRBZ[data-state="expand-all"] .expandAllLabelCollapse_2rYlP { display: none; }
  .expandButton_-ludx[aria-expanded="true"] { transform: rotate(45deg); }
  .sticky\\:active, .sticky\\:past-last { position: sticky; top: 56px; z-index: 20; }
  .clone-script-disabled .glue-cookie-notification-bar { display: none !important; }
</style>`;

  const script = `
<script id="clone-local-interactions">
(() => {
  window.__cloneConsoleErrors = window.__cloneConsoleErrors || [];
  window.addEventListener("error", (event) => {
    window.__cloneConsoleErrors.push(event.message || String(event.error || "error"));
  });
  window.addEventListener("unhandledrejection", (event) => {
    window.__cloneConsoleErrors.push(String(event.reason || "unhandled rejection"));
  });
  document.documentElement.classList.add("clone-script-disabled");

  const toggleExpanded = (button, expanded) => {
    button.setAttribute("aria-expanded", String(expanded));
    button.setAttribute("aria-pressed", String(expanded));
  };

  document.querySelectorAll("[data-slot='features-expand-button']").forEach((button) => {
    const card = button.closest(".planCard_nvuF7") || button.parentElement;
    toggleExpanded(button, false);
    button.addEventListener("click", () => {
      const open = !card.classList.contains("is-open");
      card.classList.toggle("is-open", open);
      toggleExpanded(button, open);
    });
  });

  document.querySelectorAll("[data-slot='accordion-item-trigger']").forEach((button) => {
    const item = button.closest("mws-accordion-item");
    const content = item && item.querySelector("[data-slot='accordion-item-content']");
    if (content) content.setAttribute("inert", "");
    button.addEventListener("click", () => {
      const open = !item.classList.contains("is-open");
      item.classList.toggle("is-open", open);
      button.setAttribute("aria-expanded", String(open));
      if (content) {
        if (open) content.removeAttribute("inert");
        else content.setAttribute("inert", "");
      }
    });
  });

  document.querySelectorAll("[data-slot='accordion-expand-all-button']").forEach((button) => {
    button.addEventListener("click", () => {
      const accordion = button.closest("mws-accordion");
      if (!accordion) return;
      const expand = button.getAttribute("data-state") !== "collapse-all";
      button.setAttribute("data-state", expand ? "collapse-all" : "expand-all");
      accordion.querySelectorAll("mws-accordion-item").forEach((item) => {
        item.classList.toggle("is-open", expand);
        const trigger = item.querySelector("[data-slot='accordion-item-trigger']");
        const content = item.querySelector("[data-slot='accordion-item-content']");
        if (trigger) trigger.setAttribute("aria-expanded", String(expand));
        if (content) {
          if (expand) content.removeAttribute("inert");
          else content.setAttribute("inert", "");
        }
      });
    });
  });

  document.querySelectorAll("[role='tab'][data-index]").forEach((button) => {
    button.addEventListener("click", () => {
      const tabs = button.closest("[role='tablist']");
      if (!tabs) return;
      tabs.querySelectorAll("[role='tab']").forEach((tab) => {
        tab.setAttribute("aria-selected", String(tab === button));
        tab.classList.toggle("dot:autoplay", tab === button);
      });
      const index = Number(button.getAttribute("data-index") || "0");
      const carousel = tabs.closest("g1-scrollable") || tabs.parentElement;
      const content = carousel && carousel.querySelector("[data-slot='content']");
      if (content) {
        const slides = Array.from(content.children).filter((el) => el.matches(".slide_Ya5Qe, figure, [data-slot='slide']"));
        slides.forEach((slide, i) => {
          slide.style.display = i === index || slides.length === 1 ? "" : "none";
        });
      }
    });
  });

  document.querySelectorAll(".muteUnmuteButton_9M_66").forEach((button) => {
    button.addEventListener("click", () => {
      const video = button.closest("g1-video")?.querySelector("video");
      if (!video) return;
      video.muted = !video.muted;
      button.setAttribute("aria-pressed", String(!video.muted));
    });
  });

  document.querySelectorAll(".playPauseButton_Fnb17").forEach((button) => {
    button.addEventListener("click", () => {
      const video = button.closest("g1-video")?.querySelector("video");
      if (!video) return;
      if (video.paused) video.play().catch(() => {});
      else video.pause();
      button.setAttribute("aria-pressed", String(!video.paused));
    });
  });

  document.querySelectorAll("video").forEach((video) => {
    const source = video.querySelector("source[data-src]");
    if (!video.getAttribute("src") && source?.dataset?.src) video.setAttribute("src", source.dataset.src);
    video.muted = true;
    video.playsInline = true;
    video.setAttribute("playsinline", "");
    video.setAttribute("autoplay", "");
    video.setAttribute("loop", "");
    try {
      video.load();
      video.play().catch(() => {});
    } catch (_) {}
  });

  document.querySelectorAll("a[href*='#']").forEach((link) => {
    const raw = link.getAttribute("href");
    if (!raw || raw.startsWith("#")) return;
    try {
      const url = new URL(raw, location.href);
      if (url.hash && /^https?:/i.test(raw)) link.setAttribute("href", url.hash);
    } catch (_) {}
  });
})();
</script>`;

  let out = html.includes("</head>") ? html.replace("</head>", `${style}\n</head>`) : `${style}\n${html}`;
  out = out.includes("</body>") ? out.replace("</body>", `${script}\n</body>`) : `${out}\n${script}`;
  return out;
}

function safeRemove(target, allowedRoot) {
  const resolved = path.resolve(target);
  const root = path.resolve(allowedRoot);
  if (!resolved.startsWith(root)) throw new Error(`Refusing to remove outside output dir: ${resolved}`);
  fs.rmSync(resolved, { recursive: true, force: true });
}

function buildMirror(rawHtml, config, assetRefs) {
  fs.mkdirSync(config.outDir, { recursive: true });
  safeRemove(config.mirrorAssets, config.outDir);
  fs.cpSync(config.assetsDir, config.mirrorAssets, { recursive: true });
  let html = normalizeStaticHtml(stripRuntimeScripts(rawHtml));
  html = rewriteMirrorRefs(html, config.assetsDir, config.mirrorAssetsName);
  html = injectCloneEnhancements(html);
  html = html.replace(/<!-- saved from url=\([^)]+\)[^>]*-->/, "<!-- local mirror generated from saved source -->");
  fs.writeFileSync(config.mirrorOut, html, "utf8");
  return html;
}

async function buildSingle(rawHtml, config, assetRefs) {
  let html = normalizeStaticHtml(stripRuntimeScripts(rawHtml));
  html = inlineStylesheets(html, config.assetsDir, assetRefs);
  html = inlineLocalRefs(html, assetRefs);
  const remote = await inlineRemoteAssets(html, config.remoteCache, config.embedRemote, config.embedMp4);
  html = remote.html;
  html = injectCloneEnhancements(html);
  html = html
    .replace(/<!-- saved from url=\([^)]+\)[^>]*-->/, "<!-- single-file local prototype generated from saved source -->")
    .replace(/<link[^>]+rel=["']shortcut icon["'][^>]*>/gi, "");
  fs.writeFileSync(config.singleOut, html, "utf8");
  return { html, remoteStats: remote.stats };
}

function count(pattern, text) {
  return (text.match(pattern) || []).length;
}

function unresolvedLocalRefs(text, assetsDir) {
  const assetBase = path.basename(assetsDir);
  const encodedBase = encodePathSegments(assetBase);
  const patterns = [assetBase, encodedBase].map(escapeRegExp).join("|");
  const matches = text.match(new RegExp(`(?:\\./)?(?:${patterns})\\/[^"'()<>\\s]+`, "g")) || [];
  return [...new Set(matches)].sort();
}

function remainingRemoteAssets(text, embedMp4) {
  return [...new Set([...text.matchAll(/https?:\/\/[^"'()<>\s]+/g)].map((m) => m[0]))]
    .filter((url) => isRemoteEmbeddableAsset(url, embedMp4))
    .sort();
}

function remoteVideoExceptions(text, embedMp4) {
  return [...new Set([...text.matchAll(/https?:\/\/[^"'()<>\s]+/g)].map((m) => m[0]))]
    .filter((url) => isRemoteVideoAsset(url, embedMp4))
    .sort();
}

function textCheck(text, needle) {
  return needle ? text.includes(needle) : null;
}

function makeReport(rawHtml, mirrorHtml, singleHtml, remoteStats, config) {
  const unresolved = unresolvedLocalRefs(singleHtml, config.assetsDir);
  const remainingRemote = remainingRemoteAssets(singleHtml, config.embedMp4);
  const remoteVideos = remoteVideoExceptions(singleHtml, config.embedMp4);
  return {
    generatedAt: new Date().toISOString(),
    source: {
      html: config.sourceHtml,
      assets: config.assetsDir,
      chars: rawHtml.length,
      localAssetFiles: walkFiles(config.assetsDir).length,
    },
    outputs: {
      mirror: config.mirrorOut,
      mirrorChars: mirrorHtml.length,
      mirrorAssetFolder: config.mirrorAssets,
      mirrorAssetFiles: walkFiles(config.mirrorAssets).length,
      singleFile: config.singleOut,
      singleFileChars: singleHtml.length,
      singleFileBytes: fs.statSync(config.singleOut).size,
      validationJson: config.validationOut,
      validationMarkdown: config.validationMdOut,
    },
    options: {
      embedRemote: config.embedRemote,
      embedMp4: config.embedMp4,
      remoteCache: config.remoteCache,
    },
    checks: {
      sourceScripts: count(/<script\b/gi, rawHtml),
      mirrorScripts: count(/<script\b/gi, mirrorHtml),
      singleScripts: count(/<script\b/gi, singleHtml),
      singleStyleTags: count(/<style\b/gi, singleHtml),
      singleImageTags: count(/<img\b/gi, singleHtml),
      singleVideoTags: count(/<video\b/gi, singleHtml),
      unresolvedLocalRefsInSingle: unresolved,
      remainingRemoteEmbeddableAssets: remainingRemote,
      remoteAssets: {
        attempted: remoteStats.length,
        inlined: remoteStats.filter((item) => item.status === "inlined").length,
        failed: remoteStats.filter((item) => item.status === "failed"),
        bytes: remoteStats.reduce((sum, item) => sum + (item.bytes || 0), 0),
      },
      remoteVideoExceptions: remoteVideos,
      hasHero: textCheck(singleHtml, config.heroText),
      hasCompareTable: textCheck(singleHtml, config.compareText),
      hasFaq: textCheck(singleHtml, config.faqText),
    },
  };
}

function writeMarkdownReport(report, outPath) {
  const failedRemote = report.checks.remoteAssets.failed.length;
  const lines = [
    "# HTML Clone Build Report",
    "",
    `Generated: ${report.generatedAt}`,
    "",
    "| Check | Result |",
    "| --- | --- |",
    `| Unresolved local refs | ${report.checks.unresolvedLocalRefsInSingle.length} |`,
    `| Remaining remote image/font refs | ${report.checks.remainingRemoteEmbeddableAssets.length} |`,
    `| Remote asset fetch failures | ${failedRemote} |`,
    `| Remote video exceptions | ${report.checks.remoteVideoExceptions.length} |`,
    `| Single-file bytes | ${report.outputs.singleFileBytes} |`,
    `| Hero text | ${report.checks.hasHero === null ? "not checked" : report.checks.hasHero} |`,
    `| Compare text | ${report.checks.hasCompareTable === null ? "not checked" : report.checks.hasCompareTable} |`,
    `| FAQ text | ${report.checks.hasFaq === null ? "not checked" : report.checks.hasFaq} |`,
    "",
    "## Outputs",
    "",
    `- Mirror: ${report.outputs.mirror}`,
    `- Single file: ${report.outputs.singleFile}`,
    `- JSON report: ${report.outputs.validationJson}`,
    "",
    "## Known Gaps",
    "",
    report.checks.remoteVideoExceptions.length
      ? "- MP4/video URLs remain remote by default. Embed only on explicit request."
      : "- No remote video exceptions detected.",
  ];
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, `${lines.join("\n")}\n`, "utf8");
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const sourceHtml = ensureFile(args["source-html"], "source-html");
  const assetsDir = ensureDir(args["assets-dir"], "assets-dir");
  const outDir = path.resolve(args["out-dir"] || path.dirname(sourceHtml));
  const name = sanitizeName(args.name || path.basename(sourceHtml));
  const mirrorAssetsName = args["mirror-assets-name"] || `${name}-mirror_files`;
  const config = {
    sourceHtml,
    assetsDir,
    outDir,
    name,
    mirrorAssetsName,
    mirrorAssets: path.join(outDir, mirrorAssetsName),
    mirrorOut: path.resolve(args.mirror || path.join(outDir, `${name}-mirror.html`)),
    singleOut: path.resolve(args.single || path.join(outDir, `${name}-single-file.html`)),
    validationOut: path.resolve(args.report || path.join(outDir, "validation", "build-report.json")),
    validationMdOut: path.resolve(args["md-report"] || path.join(outDir, "validation", "build-report.md")),
    remoteCache: path.resolve(args["remote-cache"] || path.join(outDir, `${name}-remote-cache`)),
    embedRemote: boolArg(args["embed-remote"], true),
    embedMp4: boolArg(args["embed-mp4"], false),
    strict: boolArg(args.strict, true),
    heroText: args["hero-text"] || "",
    compareText: args["compare-text"] || "",
    faqText: args["faq-text"] || "",
  };

  const raw = fs.readFileSync(config.sourceHtml, "utf8");
  const assetRefs = buildAssetRefs(config.assetsDir);
  const mirror = buildMirror(raw, config, assetRefs);
  const single = await buildSingle(raw, config, assetRefs);
  const report = makeReport(raw, mirror, single.html, single.remoteStats, config);

  fs.mkdirSync(path.dirname(config.validationOut), { recursive: true });
  fs.writeFileSync(config.validationOut, JSON.stringify(report, null, 2), "utf8");
  writeMarkdownReport(report, config.validationMdOut);
  console.log(JSON.stringify(report, null, 2));

  const hasHardFailures =
    report.checks.unresolvedLocalRefsInSingle.length > 0 ||
    report.checks.remainingRemoteEmbeddableAssets.length > 0 ||
    report.checks.remoteAssets.failed.length > 0;
  if (config.strict && hasHardFailures) process.exitCode = 2;
}

main().catch((err) => {
  console.error(err.stack || err.message || err);
  process.exit(1);
});
