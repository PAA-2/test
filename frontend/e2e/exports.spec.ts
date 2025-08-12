import { test, expect } from '@playwright/test';
import { login } from './utils';

test('exports excel and pdf', async ({ page }) => {
  await login(page);
  await page.goto('/actions');
  const [excel] = await Promise.all([
    page.waitForEvent('download'),
    page.click('text=Exporter Excel'),
  ]);
  expect(excel.suggestedFilename()).toContain('.xlsx');
  const [pdf] = await Promise.all([
    page.waitForEvent('download'),
    page.click('text=Exporter PDF'),
  ]);
  expect(pdf.suggestedFilename()).toContain('.pdf');
});
