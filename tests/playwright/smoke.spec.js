const { test, expect } = require("@playwright/test");
const fs = require("fs");
const os = require("os");
const path = require("path");

// This smoke test intentionally avoids network or project-specific runtime
// dependencies. It verifies that Playwright is wired up and can execute
// JavaScript in a real browser context in CI.
test("opens local HTML and evaluates client-side JS", async ({ page }) => {
  const html = [
    "<!doctype html>",
    "<html>",
    "<head><meta charset='utf-8'><title>argviz smoke</title></head>",
    "<body>",
    "  <h1 id='status'>ready</h1>",
    "  <script>",
    "    document.getElementById('status').textContent = 'playwright-ok';",
    "  </script>",
    "</body>",
    "</html>",
  ].join("\n");

  const htmlPath = path.join(os.tmpdir(), `argviz-playwright-${Date.now()}.html`);
  fs.writeFileSync(htmlPath, html, "utf8");

  await page.goto(`file://${htmlPath}`);
  await expect(page.locator("#status")).toHaveText("playwright-ok");
});
