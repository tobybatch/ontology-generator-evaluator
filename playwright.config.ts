import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',

  use: {
    baseURL: 'http://127.0.0.1:5000',
    headless: true,
  },

  webServer: {
    command: 'python app.py', // or your Flask startup command
    url: 'http://127.0.0.1:5000',
    reuseExistingServer: !process.env.CI,
  },
});
