import { test, expect } from '@playwright/test';

test.describe('Tender Manager - Smoke Tests', () => {

  test('should load login page successfully', async ({ page }) => {
    await page.goto('/');

    await expect(page).toHaveTitle(/Tender Manager — Acesso/);

    const emailInput = page.locator('#login-email');
    const passwordInput = page.locator('#login-password');
    const loginButton = page.locator('#login-submit-btn');

    await expect(emailInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
    await expect(loginButton).toBeVisible();
  });

  test('should allow switching to register tab', async ({ page }) => {
    await page.goto('/');

    const registerTab = page.locator('#tab-register');
    const registerPanel = page.locator('#panel-register');

    await registerTab.click();
    await expect(registerPanel).toBeVisible();
    await expect(page.locator('#reg-username')).toBeVisible();
  });

});
