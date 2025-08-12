import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 90000,
  retries: process.env.CI ? 1 : 0,
  reporter: [ ['list'], ['html'], ['junit', { outputFile: 'playwright-report/results.xml' }] ],
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:5173',
    trace: 'on-first-retry',
  },
});
