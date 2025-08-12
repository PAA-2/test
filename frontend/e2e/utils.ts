import { Page, expect } from '@playwright/test';

export async function login(page: Page, username = 'sa', password = 'Pa$$w0rd!') {
  await page.goto('/login');
  await page.fill('input[name="username"]', username);
  await page.fill('input[name="password"]', password);
  await Promise.all([
    page.waitForNavigation(),
    page.click('button[type="submit"]'),
  ]);
}

export async function waitForToast(page: Page) {
  await expect(page.locator('#toast')).toBeVisible();
}
