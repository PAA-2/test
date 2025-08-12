import { test, expect } from '@playwright/test';
import { login } from './utils';

test('login and redirect to dashboard', async ({ page }) => {
  await login(page);
  await expect(page.getByText('Total')).toBeVisible();
});
