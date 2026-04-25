import { test, expect } from '@playwright/test';

test.describe('Tender Manager - Login', () => {

  test('should_login_successfully_and_redirect_to_dashboard_when_valid_credentials_are_provided', async ({ page, request }) => {
    // Arrange
    const uniqueId = Date.now();
    const username = `user_login_${uniqueId}`;
    const email = `user_login_${uniqueId}@test.com`;
    const password = 'password123';
    let createdUserId = null;
    let accessToken = null;

    try {
      // Setup: Create a user directly via API for this test
      const createResponse = await request.post('/api/users/', {
        data: { username, email, password }
      });
      expect(createResponse.ok()).toBeTruthy();
      const userData = await createResponse.json();
      createdUserId = userData.id;

      // Act
      await page.goto('/');
      await page.locator('#login-email').fill(email);
      await page.locator('#login-password').fill(password);
      
      // Intercept the auth/token to get the token for cleanup
      const tokenResponsePromise = page.waitForResponse(response => 
        response.url().includes('/api/auth/token') && response.request().method() === 'POST'
      );
      
      await page.locator('#login-submit-btn').click();
      
      const tokenResponse = await tokenResponsePromise;
      const tokenData = await tokenResponse.json();
      accessToken = tokenData.access_token;

      // Assert
      await page.waitForURL('**/dashboard.html');
      
      // Verify token is in localStorage
      const tokenInStorage = await page.evaluate(() => localStorage.getItem('access_token'));
      expect(tokenInStorage).toBeTruthy();
    } finally {
      // Teardown
      if (createdUserId && accessToken) {
        await request.delete(`/api/users/${createdUserId}`, {
          headers: { 'Authorization': `Bearer ${accessToken}` }
        });
      }
    }
  });

  test('should_show_error_when_invalid_credentials_are_provided', async ({ page }) => {
    // Arrange
    await page.goto('/');

    // Act
    await page.locator('#login-email').fill('non_existent_user@test.com');
    await page.locator('#login-password').fill('password123');
    await page.locator('#login-submit-btn').click();

    // Assert
    const errorMessage = page.locator('#login-error');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toHaveText('E-mail ou senha incorretos.');
  });

});
