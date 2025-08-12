import { test, expect } from '@playwright/test';
import { login } from './utils';

test('action detail buttons', async ({ page }) => {
  await login(page);
  await page.goto('/actions/ACT-0001');
  await expect(page.getByText('ACT-0001')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Valider' })).toBeVisible();
});
