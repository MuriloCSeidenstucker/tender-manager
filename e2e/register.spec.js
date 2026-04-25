import { test, expect } from '@playwright/test';

test.describe('Tender Manager - Registration', () => {

  test('should_create_account_and_show_success_message_when_valid_data_is_provided', async ({ page, request }) => {
    // Arrange
    await page.goto('/');
    await page.locator('#tab-register').click();
    
    // Generate unique data to avoid conflicts in subsequent test runs
    const uniqueId = Date.now();
    const username = `user_${uniqueId}`;
    const email = `user_${uniqueId}@test.com`;
    const password = 'password123';

    let createdUserId = null;
    let accessToken = null;

    // Set up request listeners to capture the user ID and token for cleanup
    const userResponsePromise = page.waitForResponse(response => 
      response.url().includes('/api/users/') && response.request().method() === 'POST'
    );
    const tokenResponsePromise = page.waitForResponse(response => 
      response.url().includes('/api/auth/token') && response.request().method() === 'POST'
    );

    try {
      // Act
      await page.locator('#reg-username').fill(username);
      await page.locator('#reg-email').fill(email);
      await page.locator('#reg-password').fill(password);
      await page.locator('#register-submit-btn').click();

      // Capture API responses
      const userResponse = await userResponsePromise;
      const tokenResponse = await tokenResponsePromise;
      
      const userData = await userResponse.json();
      const tokenData = await tokenResponse.json();
      
      createdUserId = userData.id;
      accessToken = tokenData.access_token;

      // Assert
      const successMessage = page.locator('#register-success');
      await expect(successMessage).toBeVisible();
      await expect(successMessage).toHaveText('Conta criada! Fazendo login...');
    } finally {
      // Teardown: Clean up the generated user to prevent data pollution
      if (createdUserId && accessToken) {
        await request.delete(`/api/users/${createdUserId}`, {
          headers: {
            'Authorization': `Bearer ${accessToken}`
          }
        });
      }
    }
  });

  test('should_show_error_when_email_is_already_registered', async ({ page, request }) => {
    // Arrange: Create user via API
    const uniqueId = Date.now();
    const username = `user_dup_${uniqueId}`;
    const email = `user_dup_${uniqueId}@test.com`;
    const password = 'password123';
    let createdUserId = null;
    let accessToken = null;

    try {
      const createResponse = await request.post('/api/users/', {
        data: { username, email, password }
      });
      expect(createResponse.ok()).toBeTruthy();
      const userData = await createResponse.json();
      createdUserId = userData.id;

      const tokenResponse = await request.post('/api/auth/token', {
        form: { username: email, password }
      });
      const tokenData = await tokenResponse.json();
      accessToken = tokenData.access_token;

      // Act: Try to register again via UI
      await page.goto('/');
      await page.locator('#tab-register').click();
      
      await page.locator('#reg-username').fill(username);
      await page.locator('#reg-email').fill(email);
      await page.locator('#reg-password').fill(password);
      await page.locator('#register-submit-btn').click();

      // Assert
      const errorMessage = page.locator('#register-error');
      await expect(errorMessage).toBeVisible();
    } finally {
      if (createdUserId && accessToken) {
        await request.delete(`/api/users/${createdUserId}`, {
          headers: { 'Authorization': `Bearer ${accessToken}` }
        });
      }
    }
  });

  test('should_show_error_when_username_is_too_short', async ({ page }) => {
    await page.goto('/');
    await page.locator('#tab-register').click();
    
    // Act
    await page.locator('#reg-username').fill('ab'); // 2 chars (invalid)
    await page.locator('#reg-email').fill(`user_${Date.now()}@test.com`);
    await page.locator('#reg-password').fill('password123');
    await page.locator('#register-submit-btn').click();

    // Assert: Backend validation error shown
    const errorMessage = page.locator('#register-error');
    await expect(errorMessage).toBeVisible();
  });

  test('should_show_error_when_password_is_too_short', async ({ page }) => {
    await page.goto('/');
    await page.locator('#tab-register').click();
    
    // Act
    await page.locator('#reg-username').fill(`user_${Date.now()}`); 
    await page.locator('#reg-email').fill(`user_${Date.now()}@test.com`);
    await page.locator('#reg-password').fill('12345'); // 5 chars (invalid)
    await page.locator('#register-submit-btn').click();

    // Assert: Backend validation error shown
    const errorMessage = page.locator('#register-error');
    await expect(errorMessage).toBeVisible();
  });

});
