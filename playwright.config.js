const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "tests/playwright",
  timeout: 30 * 1000,
  expect: {
    timeout: 5 * 1000,
  },
  use: {
    headless: true,
  },
  projects: [
    {
      name: "chromium",
      use: { browserName: "chromium" },
    },
  ],
});
