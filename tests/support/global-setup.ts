/**
 * Global setup for Playwright tests
 * Runs once before all tests to initialize the test environment
 */

import * as dotenv from "dotenv";

async function globalSetup() {
  // Load test environment variables
  dotenv.config({ path: ".env.test" });

  console.log("🧪 Running global test setup...");

  const baseURL = process.env.PLAYWRIGHT_BASE_URL || "http://localhost:5001";

  // Wait for server to be ready
  console.log(`⏳ Waiting for server at ${baseURL}...`);

  // Add any database seeding or cleanup here
  // Example: Clear test database, seed with sample data, etc.

  console.log("✅ Global setup complete");
}

export default globalSetup;
