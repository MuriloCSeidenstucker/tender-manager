import { test, expect } from '@playwright/test';

test.describe('Tender Manager - Companies', () => {

  test('should_redirect_to_login_when_not_authenticated', async ({ page }) => {
    await page.goto('/companies.html');
    await page.waitForURL('**/index.html');
  });

  test.describe('Authenticated User Flow', () => {
    let userId = null;
    let accessToken = null;

    test.beforeEach(async ({ request, page }) => {
      // Arrange: Create a user and login
      const uniqueId = Date.now();
      const username = `company_user_${uniqueId}`;
      const email = `company_user_${uniqueId}@test.com`;
      const password = 'password123';

      const createResponse = await request.post('/api/users/', {
        data: { username, email, password }
      });
      const userData = await createResponse.json();
      userId = userData.id;

      const tokenResponse = await request.post('/api/auth/token', {
        form: { username: email, password }
      });
      const tokenData = await tokenResponse.json();
      accessToken = tokenData.access_token;

      // Set token and navigate
      await page.goto('/');
      await page.evaluate((token) => {
        localStorage.setItem('access_token', token);
      }, accessToken);
      await page.goto('/companies.html');
    });

    test.afterEach(async ({ request }) => {
      // Cleanup: Delete user
      if (userId && accessToken) {
        await request.delete(`/api/users/${userId}`, {
          headers: { 'Authorization': `Bearer ${accessToken}` }
        }).catch(() => {});
      }
    });

    test('should_display_empty_state_when_no_companies', async ({ page }) => {
      await expect(page.locator('.empty-state')).toBeVisible();
      await expect(page.locator('.empty-state h3')).toHaveText('Nenhuma empresa cadastrada');
    });

    test('should_create_company_successfully', async ({ page }) => {
      // Act
      await page.locator('#btn-new-company').click();
      await expect(page.locator('#modal-overlay')).toBeVisible();
      await expect(page.locator('#modal-title')).toHaveText('Nova Empresa');

      await page.locator('#company-name').fill('Test Company Success');
      await page.locator('#company-trade-name').fill('Test Success');
      await page.locator('#company-cnpj').fill('12345678000199');
      await page.locator('#btn-save').click();

      // Assert
      await expect(page.locator('#modal-overlay')).toBeHidden();
      const companyRow = page.locator('tr', { hasText: 'Test Company Success' });
      await expect(companyRow).toBeVisible();
      await expect(companyRow.locator('.cnpj-code')).toHaveText('12345678000199');
    });

    test('should_show_error_for_invalid_cnpj', async ({ page }) => {
      // Act
      await page.locator('#btn-new-company').click();
      await page.locator('#company-name').fill('Invalid CNPJ Co');
      await page.locator('#company-trade-name').fill('Invalid');
      await page.locator('#company-cnpj').fill('123'); // Too short
      await page.locator('#btn-save').click();

      // Assert
      const errorMsg = page.locator('#form-error');
      await expect(errorMsg).toBeVisible();
      await expect(errorMsg).toHaveText('O CNPJ deve conter exatamente 14 dígitos numéricos.');
    });

    test('should_show_error_on_duplicate_cnpj', async ({ request, page }) => {
      // Arrange: Create a company via API first
      const duplicateCnpj = '11222333000100';
      await request.post('/api/companies/', {
        data: { name: 'Existing Co', trade_name: 'Existing', cnpj: duplicateCnpj },
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });

      // Act
      await page.reload(); // Refresh to see the new company (not strictly necessary but good practice)
      await page.locator('#btn-new-company').click();
      await page.locator('#company-name').fill('New Co with Dup CNPJ');
      await page.locator('#company-trade-name').fill('New Dup');
      await page.locator('#company-cnpj').fill(duplicateCnpj);
      await page.locator('#btn-save').click();

      // Assert
      const errorMsg = page.locator('#form-error');
      await expect(errorMsg).toBeVisible();
      // Using part of the message to be robust against minor phrasing changes
      await expect(errorMsg).toHaveText(/já existe uma empresa com este nome ou CNPJ/i);
    });

    test('should_update_company_successfully', async ({ request, page }) => {
      // Arrange: Create via API
      await request.post('/api/companies/', {
        data: { name: 'Company to Edit', trade_name: 'To Edit', cnpj: '99999999000199' },
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      await page.reload();

      // Act
      const row = page.locator('tr', { hasText: 'Company to Edit' });
      await row.locator('.btn-edit').click();
      
      await expect(page.locator('#modal-title')).toHaveText('Editar Empresa');
      await page.locator('#company-name').fill('Edited Company Name');
      await page.locator('#btn-save').click();

      // Assert
      await expect(page.locator('#modal-overlay')).toBeHidden();
      await expect(page.locator('tr', { hasText: 'Edited Company Name' })).toBeVisible();
      await expect(page.locator('tr', { hasText: 'Company to Edit' })).toBeHidden();
    });

    test('should_delete_company_successfully', async ({ request, page }) => {
      // Arrange: Create via API
      const name = 'Company to Delete';
      await request.post('/api/companies/', {
        data: { name, trade_name: 'To Delete', cnpj: '88888888000188' },
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      await page.reload();

      // Act
      const row = page.locator('tr', { hasText: name });
      await row.locator('.btn-delete').click();
      
      await expect(page.locator('#delete-overlay')).toBeVisible();
      await expect(page.locator('#delete-company-name')).toHaveText(name);
      
      await page.locator('#btn-confirm-delete').click();

      // Assert
      await expect(page.locator('#delete-overlay')).toBeHidden();
      await expect(page.locator('tr', { hasText: name })).toBeHidden();
      await expect(page.locator('.empty-state')).toBeVisible();
    });

    test('should_cancel_deletion', async ({ request, page }) => {
      // Arrange: Create via API
      const name = 'Company Saved';
      await request.post('/api/companies/', {
        data: { name, trade_name: 'Saved', cnpj: '77777777000177' },
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      await page.reload();

      // Act
      const row = page.locator('tr', { hasText: name });
      await row.locator('.btn-delete').click();
      await page.locator('#btn-cancel-delete').click();

      // Assert
      await expect(page.locator('#delete-overlay')).toBeHidden();
      await expect(page.locator('tr', { hasText: name })).toBeVisible();
    });

  });

});
