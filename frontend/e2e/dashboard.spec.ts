import { test, expect } from '@playwright/test';
import { login } from './utils';

test('dashboard shows kpis and charts', async ({ page }) => {
  await login(page);
  await page.goto('/');
  await expect(page.getByText('Total')).toBeVisible();
  await expect(page.locator('svg')).toBeVisible();
});
