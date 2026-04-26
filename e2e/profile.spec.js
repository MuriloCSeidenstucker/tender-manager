import { test, expect } from '@playwright/test';

test.describe('Tender Manager - Profile', () => {

  test('should_redirect_to_login_when_not_authenticated', async ({ page }) => {
    await page.goto('/profile.html');
    await page.waitForURL('**/index.html');
  });

  test.describe('Authenticated User Flow', () => {
    let username = '';
    let email = '';
    let password = 'password123';
    let userId = null;
    let accessToken = null;

    test.beforeEach(async ({ request, page }) => {
      // Arrange: Create a user and login
      const uniqueId = Date.now();
      username = `profile_user_${uniqueId}`;
      email = `profile_user_${uniqueId}@test.com`;

      const createResponse = await request.post('/api/users/', {
        data: { username, email, password }
      });
      expect(createResponse.ok()).toBeTruthy();
      const userData = await createResponse.json();
      userId = userData.id;

      const tokenResponse = await request.post('/api/auth/token', {
        form: { username: email, password }
      });
      expect(tokenResponse.ok()).toBeTruthy();
      const tokenData = await tokenResponse.json();
      accessToken = tokenData.access_token;

      // Set token and navigate
      await page.goto('/');
      await page.evaluate((token) => {
        localStorage.setItem('access_token', token);
      }, accessToken);
      await page.goto('/profile.html');
    });

    test.afterEach(async ({ request }) => {
      // Cleanup: Delete user if still exists
      if (userId && accessToken) {
        await request.delete(`/api/users/${userId}`, {
          headers: { 'Authorization': `Bearer ${accessToken}` }
        }).catch(() => {}); // Ignore error if user already deleted
      }
    });

    test('should_prefill_profile_fields_correctly', async ({ page }) => {
      // Assert
      await expect(page.locator('#profile-username')).toHaveValue(username);
      await expect(page.locator('#profile-email')).toHaveValue(email);
      await expect(page.locator('#username-display')).toHaveText(username);
    });

    test('should_update_profile_successfully', async ({ page }) => {
      // Act
      const newUsername = `${username}_new`;
      await page.locator('#profile-username').fill(newUsername);
      await page.locator('#btn-save-profile').click();

      // Assert
      const successMsg = page.locator('#profile-success');
      await expect(successMsg).toBeVisible();
      await expect(successMsg).toHaveText('Dados atualizados com sucesso!');
      await expect(page.locator('#username-display')).toHaveText(newUsername);
      
      // Initial also updates
      await expect(page.locator('#user-initial')).toHaveText(newUsername[0].toUpperCase());
    });

    test('should_show_error_on_invalid_email', async ({ page, request }) => {
        // Arrange: Create another user first to have a conflicting email
        const otherEmail = `conflict_${Date.now()}@test.com`;
        await request.post('/api/users/', {
            data: { username: `other_${Date.now()}`, email: otherEmail, password: 'password123' }
        });

        // Act
        await page.locator('#profile-email').fill(otherEmail);
        await page.locator('#btn-save-profile').click();

        // Assert
        const errorMsg = page.locator('#profile-error');
        await expect(errorMsg).toBeVisible();
        await expect(errorMsg).toHaveText('Usuário ou e-mail já cadastrado.');
    });

    test.describe('Password Changes', () => {

        test('should_change_password_successfully', async ({ page }) => {
            // Act
            await page.locator('#current-password').fill(password);
            await page.locator('#new-password').fill('newpassword123');
            await page.locator('#confirm-password').fill('newpassword123');
            await page.locator('#btn-save-password').click();

            // Assert
            const successMsg = page.locator('#password-success');
            await expect(successMsg).toBeVisible();
            await expect(successMsg).toHaveText('Senha alterada com sucesso!');
            
            // Inputs should be reset
            await expect(page.locator('#current-password')).toHaveValue('');
        });

        test('should_show_error_when_passwords_do_not_match', async ({ page }) => {
            // Act
            await page.locator('#current-password').fill(password);
            await page.locator('#new-password').fill('newpassword123');
            await page.locator('#confirm-password').fill('mismatch');
            await page.locator('#btn-save-password').click();

            // Assert
            const errorMsg = page.locator('#password-error');
            await expect(errorMsg).toBeVisible();
            await expect(errorMsg).toHaveText('A nova senha e a confirmação não coincidem.');
        });

        test('should_show_error_for_short_password', async ({ page }) => {
            // Act
            await page.locator('#current-password').fill(password);
            await page.locator('#new-password').fill('123');
            await page.locator('#confirm-password').fill('123');
            await page.locator('#btn-save-password').click();

            // Assert
            const errorMsg = page.locator('#password-error');
            await expect(errorMsg).toBeVisible();
            await expect(errorMsg).toHaveText('A nova senha deve ter pelo menos 6 caracteres.');
        });

        test('should_show_api_error_for_incorrect_current_password', async ({ page }) => {
            // Act
            await page.locator('#current-password').fill('wrongpassword');
            await page.locator('#new-password').fill('newpassword123');
            await page.locator('#confirm-password').fill('newpassword123');
            await page.locator('#btn-save-password').click();

            // Assert
            const errorMsg = page.locator('#password-error');
            await expect(errorMsg).toBeVisible();
            await expect(errorMsg).toHaveText('A senha atual está incorreta.');
        });
    });

    test.describe('Account Deletion', () => {

        test('should_open_and_close_delete_modal', async ({ page }) => {
            // Open
            await page.locator('#btn-delete-account').click();
            const overlay = page.locator('#delete-overlay');
            await expect(overlay).toBeVisible();

            // Close via cancel button
            await page.locator('#btn-cancel-delete').click();
            await expect(overlay).toBeHidden();

            // Open again
            await page.locator('#btn-delete-account').click();
            await expect(overlay).toBeVisible();

            // Close via X button
            await page.locator('#delete-modal-close').click();
            await expect(overlay).toBeHidden();
        });

        test('should_delete_account_successfully', async ({ page }) => {
            // Act
            await page.locator('#btn-delete-account').click();
            await page.locator('#btn-confirm-delete').click();

            // Assert
            await page.waitForURL('**/index.html');
            const token = await page.evaluate(() => localStorage.getItem('access_token'));
            expect(token).toBeNull();
        });
    });

  });

});
