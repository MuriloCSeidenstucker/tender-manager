import { test, expect } from '@playwright/test';

test.describe('Tender Manager - Dashboard', () => {

  test('should_redirect_to_login_when_not_authenticated', async ({ page }) => {
    // Act
    await page.goto('/dashboard.html');

    // Assert
    await page.waitForURL('**/index.html');
    await expect(page).toHaveTitle(/Tender Manager — Acesso/);
  });

  test.describe('Authenticated User', () => {
    let username = '';
    let email = '';
    let password = 'password123';
    let userId = null;
    let accessToken = null;

    test.beforeEach(async ({ request, page }) => {
      // Arrange: Create a user and login
      const uniqueId = Date.now();
      username = `dash_user_${uniqueId}`;
      email = `dash_user_${uniqueId}@test.com`;

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

      // Set token in localStorage and navigate
      await page.goto('/');
      await page.evaluate((token) => {
        localStorage.setItem('access_token', token);
      }, accessToken);
      await page.goto('/dashboard.html');
    });

    test.afterEach(async ({ request }) => {
      // Teardown: Delete user
      if (userId && accessToken) {
        await request.delete(`/api/users/${userId}`, {
          headers: { 'Authorization': `Bearer ${accessToken}` }
        });
      }
    });

    test('should_display_username_and_initial_when_authenticated', async ({ page }) => {
      // Assert
      const usernameDisplay = page.locator('#username-display');
      const userInitial = page.locator('#user-initial');

      await expect(usernameDisplay).toHaveText(email);
      await expect(userInitial).toHaveText(email[0].toUpperCase());
    });

    test('should_display_empty_state_when_no_companies_exist', async ({ page }) => {
      // Assert
      const emptyState = page.locator('.empty-state');
      await expect(emptyState).toBeVisible();
      await expect(emptyState.locator('h3')).toHaveText('Nenhuma empresa cadastrada');
    });

    test('should_logout_successfully_when_logout_button_is_clicked', async ({ page }) => {
      // Act
      await page.locator('#logout-btn').click();

      // Assert
      await page.waitForURL('**/index.html');
      const tokenInStorage = await page.evaluate(() => localStorage.getItem('access_token'));
      expect(tokenInStorage).toBeNull();
    });

    test('should_populate_year_selector_with_last_5_years', async ({ page }) => {
      // Assert
      const yearSelect = page.locator('#year-select');
      const options = yearSelect.locator('option');
      await expect(options).toHaveCount(5);

      const currentYear = new Date().getFullYear();
      await expect(options.first()).toHaveAttribute('value', currentYear.toString());
      await expect(options.last()).toHaveAttribute('value', (currentYear - 4).toString());
    });

    test('should_display_metrics_for_current_year_by_default', async ({ request, page }) => {
      // Arrange
      const companyName = 'Test Company Metrics';
      const companyResponse = await request.post('/api/companies/', {
        data: {
          name: companyName,
          trade_name: 'Test Trade Name',
          cnpj: '12345678901234'
        },
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      expect(companyResponse.ok()).toBeTruthy();
      const companyData = await companyResponse.json();
      const companyId = companyData.id;

      const currentYear = new Date().getFullYear();

      // Tender 1: Won
      await request.post(`/api/companies/${companyId}/tenders/`, {
        data: {
          tender_number: 101,
          tender_year: currentYear,
          object_description: 'Won Tender Description',
          public_body_name: 'Public Body A',
          modality: 'trading_session',
          format: 'electronic',
          status: 'finished',
          participation_result: 'won',
          awarded_value: 50000.50,
          session_date: new Date().toISOString()
        },
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });

      // Tender 2: Lost (Should count in total, but not in wins or value if value is only for wins)
      // Actually dashboard.js shows total_awarded_value, lets check if it sums all or only won.
      // Usually it sums awarded value.
      await request.post(`/api/companies/${companyId}/tenders/`, {
        data: {
          tender_number: 102,
          tender_year: currentYear,
          object_description: 'Lost Tender Description',
          public_body_name: 'Public Body B',
          modality: 'trading_session',
          format: 'electronic',
          status: 'finished',
          participation_result: 'lost',
          awarded_value: 0,
          session_date: new Date().toISOString()
        },
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });

      // Act
      await page.reload(); // Reload to fetch new metrics

      // Assert
      const companyCard = page.locator('.company-card').filter({ hasText: companyName });
      await expect(companyCard).toBeVisible();

      // Total Tenders: 2
      await expect(companyCard.locator('.metric-box >> text=Licitações').locator('xpath=following-sibling::*')).toHaveText('2');
      // Wins: 1
      await expect(companyCard.locator('.metric-box.success >> text=Vitórias').locator('xpath=following-sibling::*')).toHaveText('1');
      // Total Awarded: R$ 50.000,50
      await expect(companyCard.locator('.metric-box.warning.wide >> text=Total Adjudicado').locator('xpath=following-sibling::*')).toHaveText(/50\.000,50/);
    });

    test('should_update_metrics_when_year_is_changed', async ({ request, page }) => {
      // Arrange
      const companyName = 'Year Change Company';
      const companyResponse = await request.post('/api/companies/', {
        data: {
          name: companyName,
          trade_name: 'Year Trade',
          cnpj: '98765432109876'
        },
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      const companyData = await companyResponse.json();
      const companyId = companyData.id;

      const currentYear = new Date().getFullYear();
      const lastYear = currentYear - 1;

      // Tender in last year
      await request.post(`/api/companies/${companyId}/tenders/`, {
        data: {
          tender_number: 201,
          tender_year: lastYear,
          object_description: 'Last Year Tender',
          public_body_name: 'Old Body',
          modality: 'trading_session',
          format: 'electronic',
          status: 'finished',
          participation_result: 'won',
          awarded_value: 1000,
          session_date: new Date(lastYear, 0, 1).toISOString()
        },
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });

      // Act
      await page.reload();
      // By default current year (no tenders)
      const companyCardDefault = page.locator('.company-card').filter({ hasText: companyName });
      await expect(companyCardDefault.locator('.metric-box >> text=Licitações').locator('xpath=following-sibling::*')).toHaveText('0');

      // Change year to last year
      await page.locator('#year-select').selectOption(lastYear.toString());

      // Assert updated metrics
      await expect(companyCardDefault.locator('.metric-box >> text=Licitações').locator('xpath=following-sibling::*')).toHaveText('1');
      await expect(companyCardDefault.locator('.metric-box.success >> text=Vitórias').locator('xpath=following-sibling::*')).toHaveText('1');
    });

  });

});
