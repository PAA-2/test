import { test, expect } from '@playwright/test';
import { login } from './utils';

test('actions list filters and creation', async ({ page }) => {
  await login(page);
  await page.goto('/actions');
  await expect(page.locator('table')).toBeVisible();
  await page.selectOption('select[name="plan"]', { label: 'CODIR' });
  await page.selectOption('select[name="priorite"]', 'High');
  await page.fill('input[name="q"]', 'Action');
  await expect(page).toHaveURL(/plan=/);
  await page.click('text=Nouvelle action');
  await expect(page.getByText('Titre')).toBeVisible();
});
