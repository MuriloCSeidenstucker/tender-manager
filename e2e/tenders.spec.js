import { test, expect } from '@playwright/test';

test.describe('Tender Manager - Tenders', () => {

  test('should_redirect_to_login_when_not_authenticated', async ({ page }) => {
    await page.goto('/tenders.html');
    await page.waitForURL('**/index.html');
  });

  test.describe('Authenticated User Flow', () => {
    let userId = null;
    let accessToken = null;
    let companyId = null;

    test.beforeEach(async ({ request, page }) => {
      // Arrange: Create user, login and create one company
      const uniqueId = Date.now();
      const username = `tender_user_${uniqueId}`;
      const email = `tender_user_${uniqueId}@test.com`;
      const password = 'password123';

      const userResp = await request.post('/api/users/', { data: { username, email, password } });
      const userData = await userResp.json();
      userId = userData.id;

      const tokenResp = await request.post('/api/auth/token', { form: { username: email, password } });
      const tokenData = await tokenResp.json();
      accessToken = tokenData.access_token;

      const companyResp = await request.post('/api/companies/', {
        data: { name: 'Tender Co Ltd', trade_name: 'Tender Co', cnpj: `11111222${uniqueId.toString().slice(-6)}` },
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      const companyData = await companyResp.json();
      companyId = companyData.id;

      // Set token and navigate
      await page.goto('/');
      await page.evaluate((token) => {
        localStorage.setItem('access_token', token);
      }, accessToken);
      await page.goto('/tenders.html');
    });

    test.afterEach(async ({ request }) => {
      if (userId && accessToken) {
        await request.delete(`/api/users/${userId}`, {
          headers: { 'Authorization': `Bearer ${accessToken}` }
        }).catch(() => {});
      }
    });

    test('should_populate_company_selector_and_handle_selection', async ({ page }) => {
      const selector = page.locator('#company-select');
      await expect(selector).toContainText('Tender Co Ltd');

      // Act: Select company
      await selector.selectOption(String(companyId));

      // Assert
      await expect(page.locator('#btn-new-tender')).toBeEnabled();
      await expect(page.locator('.empty-state h3')).toHaveText('Nenhuma licitação encontrada');
      expect(page.url()).toContain(`company=${companyId}`);
    });

    test('should_preselect_company_from_url_param', async ({ page }) => {
        // Navigate directly with param
        await page.goto(`/tenders.html?company=${companyId}`);
        
        // Assert
        await expect(page.locator('#company-select')).toHaveValue(String(companyId));
        await expect(page.locator('#btn-new-tender')).toBeEnabled();
        await expect(page.locator('.empty-state h3')).toHaveText('Nenhuma licitação encontrada');
    });

    test('should_create_tender_successfully', async ({ page }) => {
      // Arrange
      await page.locator('#company-select').selectOption(String(companyId));

      // Act
      await page.locator('#btn-new-tender').click();
      await expect(page.locator('#modal-overlay')).toBeVisible();

      await page.locator('#tender-number').fill('101');
      await page.locator('#tender-year').fill('2026');
      await page.locator('#tender-body').fill('Prefeitura Municipal');
      await page.locator('#tender-desc').fill('Objeto da licitação de teste');
      await page.locator('#tender-modality').selectOption('trading_session');
      await page.locator('#tender-format').selectOption('electronic');
      await page.locator('#tender-session-date').fill('2026-05-20T14:00');
      await page.locator('#tender-status').selectOption('analysis');
      await page.locator('#tender-result').selectOption('pending');
      
      await page.locator('#btn-save').click();

      // Assert
      await expect(page.locator('#modal-overlay')).toBeHidden();
      const row = page.locator('tr', { hasText: '101/2026' });
      await expect(row).toBeVisible();
      await expect(row).toContainText('Prefeitura Municipal');
      await expect(row).toContainText('Pregão');
      await expect(row.locator('.badge')).toHaveText('Análise');
    });

    test('should_show_error_for_invalid_business_rules', async ({ page }) => {
        // Rule: Result LOST but AWARDED VALUE > 0
        await page.locator('#company-select').selectOption(String(companyId));
        await page.locator('#btn-new-tender').click();
        
        await page.locator('#tender-number').fill('202');
        await page.locator('#tender-year').fill('2026');
        await page.locator('#tender-body').fill('Órgão de Teste');
        await page.locator('#tender-desc').fill('Descrição');
        await page.locator('#tender-result').selectOption('lost');
        await page.locator('#tender-awarded').fill('100.00'); // Forbidden for LOST
        await page.locator('#btn-save').click();

        // Assert
        const errorMsg = page.locator('#form-error');
        await expect(errorMsg).toBeVisible();
        await expect(errorMsg).toHaveText('O valor adjudicado deve ser zero quando o resultado for Perdeu.');
    });

    test('should_update_tender_successfully', async ({ request, page }) => {
      // Arrange: Create via API
      await request.post(`/api/companies/${companyId}/tenders/`, {
        data: {
          tender_number: 303,
          tender_year: 2026,
          public_body_name: 'Orgão Original',
          object_description: 'Desc',
          modality: 'public_tender',
          format: 'in_person',
          status: 'monitoring'
        },
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      await page.reload();
      await page.locator('#company-select').selectOption(String(companyId));

      // Act
      const row = page.locator('tr', { hasText: '303/2026' });
      await row.locator('.btn-edit').click();
      
      await page.locator('#tender-status').selectOption('finished');
      await page.locator('#tender-result').selectOption('won');
      await page.locator('#tender-awarded').fill('150000.50');
      await page.locator('#btn-save').click();

      // Assert
      await expect(page.locator('#modal-overlay')).toBeHidden();
      await expect(row.locator('.badge')).toHaveText('Finalizado');
      await expect(row).toContainText('Ganhou ✅');
      await expect(row).toContainText('R$ 150.000,50');
    });

    test('should_delete_tender_successfully', async ({ request, page }) => {
      // Arrange: Create via API
      const label = '404/2026';
      await request.post(`/api/companies/${companyId}/tenders/`, {
        data: {
          tender_number: 404,
          tender_year: 2026,
          public_body_name: 'Deletar este',
          object_description: 'Desc',
          modality: 'auction',
          format: 'electronic',
          status: 'canceled'
        },
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      await page.reload();
      await page.locator('#company-select').selectOption(String(companyId));

      // Act
      const row = page.locator('tr', { hasText: label });
      await row.locator('.btn-delete').click();
      
      await expect(page.locator('#delete-overlay')).toBeVisible();
      await expect(page.locator('#delete-tender-label')).toHaveText(label);
      
      await page.locator('#btn-confirm-delete').click();

      // Assert
      await expect(page.locator('#delete-overlay')).toBeHidden();
      await expect(page.locator('tr', { hasText: label })).toBeHidden();
    });

  });

});
