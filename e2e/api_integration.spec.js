import { test, expect } from '@playwright/test';

test.describe('Tender Manager - API Integration', () => {

  test('should receive error from backend when attempting login with invalid credentials', async ({ page }) => {
    await page.goto('/');

    await page.locator('#login-email').fill('non_existent_user@test.com');
    await page.locator('#login-password').fill('password123');

    await page.locator('#login-submit-btn').click();

    const errorMessage = page.locator('#login-error');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toHaveText('E-mail ou senha incorretos.');
  });

});
