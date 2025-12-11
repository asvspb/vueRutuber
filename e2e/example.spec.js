// @ts-check
import { test, expect } from '@playwright/test';

// Tests use baseURL from playwright.config.js (PW_BASE_URL or default http://localhost:5173)

test('has title', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/Vue/);
});

test('has main heading', async ({ page }) => {
  await page.goto('/');
  const heading = page.locator('h1');
  await expect(heading).toBeVisible();
  await expect(heading).toContainText('Добро пожаловать');
});
