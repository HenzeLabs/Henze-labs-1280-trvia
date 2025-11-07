import { defineConfig, devices } from "@playwright/test";
import * as dotenv from "dotenv";

// Load test environment variables
dotenv.config({ path: ".env.test" });

const baseURL = process.env.PLAYWRIGHT_BASE_URL || "http://localhost:5001";
const flaskPort = process.env.FLASK_PORT || "5001";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 2 : 1, // Parallel in CI, sequential locally
  reporter: "html",
  use: {
    baseURL: baseURL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    testIdAttribute: "data-testid", // Use data-testid for stable selectors
  },

  projects: [
    {
      name: "chromium-desktop",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "chromium-tablet",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 1180, height: 820 },
      },
    },
    {
      name: "chromium-low-end",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 1280, height: 720 },
        launchOptions: {
          args: ["--disable-dev-shm-usage"],
        },
      },
    },
    {
      name: "mobile-safari",
      use: { ...devices["iPhone 12"] },
    },
  ],

  webServer: {
    command: "bash -c 'source venv/bin/activate && python run_server.py'",
    url: baseURL,
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },

  // Global setup for test initialization
  globalSetup: require.resolve("./tests/support/global-setup"),
});
