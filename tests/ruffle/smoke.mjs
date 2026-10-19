/**
 * Automated runtime smoke test of the compiled SWF.
 * - Serves Ruffle assets and SWF from localhost
 * - Launches Chromium headlessly via Playwright
 * - Captures ActionScript trace() through Ruffle traceObserver
 * - Stores screenshot and machine-readable report even on failure.
 *
 * Run: cd tests/ruffle && npm install && npx playwright install chromium
 *      npm run smoke
 */
import { chromium } from "playwright";
import { spawn } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const base = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const out = path.join(base, "dist", "ruffle-smoke");
await mkdir(out, { recursive: true });

const host = "http://127.0.0.1:18765";
let browser;
let page;
let server;
let report = { result: "not-started", traces: [], errors: [], console: [],
               url: host + "/tests/ruffle/index.html" };

try {
  server = spawn("python3", ["-m","http.server","18765","--bind","127.0.0.1",
                              "--directory", base], { stdio: ["ignore","pipe","pipe"]});
  server.on("error", e => report.errors.push("server: " + e.message));

  let ready = false;
  for (let i = 0; i < 100; i++) {
    try {
      const r = await fetch(host + "/tests/ruffle/index.html");
      if (r.ok) { ready = true; break; }
    } catch (_) {}
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  if (!ready) throw new Error("Local HTTP server did not start");

  browser = await chromium.launch({
    headless: true,
    args: [
      "--enable-webgl",
      "--use-gl=angle",
      "--use-angle=swiftshader",
      "--enable-unsafe-swiftshader"
    ]
  });
  page = await browser.newPage({ viewport: {width:1100, height:720} });
  page.on("console", msg => report.console.push(msg.type() + ": " + msg.text()));
  page.on("pageerror", error => report.errors.push("pageerror: " + String(error)));
  page.on("response", response => {
    if (response.status() >= 400)
      report.errors.push("HTTP " + response.status() + " " + response.url());
  });
  await page.goto(report.url, { waitUntil: "domcontentloaded", timeout: 30000 });
  await page.waitForFunction(
    () => window.__swDone === true || Boolean(window.__swError),
    null, {timeout:60000}
  );
  report.traces = await page.evaluate(() => window.__swTrace || []);
  report.loadError = await page.evaluate(() => window.__swError);
  report.loaded = await page.evaluate(() => Boolean(window.__swLoaded));
  report.summary = report.traces.find(t => t.startsWith("SWTEST:SUMMARY ")) || null;
  report.passTests = report.traces.filter(t => /SWTEST:[^:]+:PASS$/.test(t));
  report.failTests = report.traces.filter(t => /SWTEST:[^:]+:FAIL(?:\s|$)/.test(t));
  const m = report.summary?.match(/^SWTEST:SUMMARY pass=(\d+) fail=(\d+)$/);
  if (!m) throw new Error("No ActionScript test summary observed");
  report.passed = Number(m[1]);
  report.failed = Number(m[2]);
  if (report.passed !== report.passTests.length ||
      report.failed !== report.failTests.length) {
    throw new Error("Trace counts are inconsistent");
  }
  if (report.failed > 0 || report.passed < 8) {
    throw new Error("ActionScript smoke tests failed or did not all run");
  }
  report.result = "passed";
} catch (e) {
  report.result = "failed";
  report.errors.push(String(e && e.stack || e));
} finally {
  if (page) {
    try { await page.screenshot({ path: path.join(out, "screenshot.png"),
                                   fullPage:true,timeout:5000 }); }
    catch (e) { report.errors.push("screenshot: " + e.message); }
  }
  if (browser) await browser.close();
  if (server) server.kill();
  await writeFile(path.join(out,"report.json"),
                  JSON.stringify(report,null,2) + "\n","utf8");
  console.log("SW-RUFFLE-REPORT", JSON.stringify({
    result:report.result,loaded:report.loaded,summary:report.summary,
    errors:report.errors, traces:report.traces
  }));
}
if (report.result !== "passed") process.exitCode = 1;
