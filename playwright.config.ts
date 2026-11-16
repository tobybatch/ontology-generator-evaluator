import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',

  use: {
    baseURL: 'http://127.0.0.1:5000',
    headless: true,
  },

  webServer: {
    command: 'uv run flask run',
    url: 'http://127.0.0.1:5000',
    reuseExistingServer: !process.env.CI,
  }
});
