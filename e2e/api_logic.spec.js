import { test, expect } from '@playwright/test';

test.describe('Tender Manager - API Logic (api.js)', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to a page where api.js can be imported as a module
    await page.goto('/');
  });

  test.describe('Authentication Utilities', () => {
    
    test('should_return_correct_status_for_isAuthenticated', async ({ page }) => {
      // Act & Assert (False)
      const isAuthFalse = await page.evaluate(async () => {
        const { isAuthenticated } = await import('./js/api.js');
        localStorage.removeItem('access_token');
        return isAuthenticated();
      });
      expect(isAuthFalse).toBe(false);

      // Act & Assert (True)
      const isAuthTrue = await page.evaluate(async () => {
        const { isAuthenticated } = await import('./js/api.js');
        localStorage.setItem('access_token', 'fake-token');
        return isAuthenticated();
      });
      expect(isAuthTrue).toBe(true);
    });

    test('should_clear_storage_and_redirect_on_logout', async ({ page }) => {
      // Arrange
      await page.evaluate(() => {
        localStorage.setItem('access_token', 'token-to-be-removed');
      });

      // Act
      await page.evaluate(async () => {
        const { logout } = await import('./js/api.js');
        logout();
      });

      // Assert
      await page.waitForURL('**/index.html');
      const token = await page.evaluate(() => localStorage.getItem('access_token'));
      expect(token).toBeNull();
    });
  });

  test.describe('apiFetch Wrapper', () => {

    test('should_include_auth_header_when_token_exists', async ({ page }) => {
      // Arrange
      const token = 'test-jwt-token';
      await page.evaluate((t) => localStorage.setItem('access_token', t), token);

      // Intercept fetch
      let requestHeaders = {};
      await page.route('**/api/test-path', async (route) => {
        requestHeaders = route.request().headers();
        await route.fulfill({ status: 200, contentType: 'application/json', body: '{}' });
      });

      // Act
      await page.evaluate(async () => {
        const { apiFetch } = await import('./js/api.js');
        await apiFetch('/test-path');
      });

      // Assert
      expect(requestHeaders['authorization']).toBe(`Bearer ${token}`);
    });

    test('should_redirect_and_clear_token_on_401', async ({ page }) => {
      // Arrange
      await page.evaluate(() => localStorage.setItem('access_token', 'invalid-token'));
      
      await page.route('**/api/unauthorized', async (route) => {
        await route.fulfill({ status: 401 });
      });

      // Act
      await page.evaluate(async () => {
        const { apiFetch } = await import('./js/api.js');
        await apiFetch('/unauthorized');
      });

      // Assert
      await page.waitForURL('**/index.html');
      const token = await page.evaluate(() => localStorage.getItem('access_token'));
      expect(token).toBeNull();
    });
  });

  test.describe('parseErrorResponse', () => {

    test('should_map_known_errors_correctly', async ({ page }) => {
      const message = await page.evaluate(async () => {
        const { parseErrorResponse } = await import('./js/api.js');
        const mockResp = {
          json: async () => ({ detail: 'Incorrect email or password' })
        };
        return await parseErrorResponse(mockResp);
      });
      expect(message).toBe('E-mail ou senha incorretos.');
    });

    test('should_handle_fastapi_validation_errors_422', async ({ page }) => {
      const message = await page.evaluate(async () => {
        const { parseErrorResponse } = await import('./js/api.js');
        const mockResp = {
          status: 422,
          json: async () => ({
            detail: [
              { loc: ['body', 'email'], msg: 'value is not a valid email', type: 'value_error.email' },
              { loc: ['body', 'password'], msg: 'field required', type: 'value_error.missing' }
            ]
          })
        };
        return await parseErrorResponse(mockResp);
      });
      
      expect(message).toContain('O campo "E-mail" deve ser um e-mail válido.');
      expect(message).toContain('O campo "Senha" é obrigatório.');
    });

    test('should_handle_dynamic_business_rule_errors', async ({ page }) => {
      const message = await page.evaluate(async () => {
        const { parseErrorResponse } = await import('./js/api.js');
        const mockResp = {
          json: async () => ({ detail: 'Value cannot be greater than zero for status: finished' })
        };
        return await parseErrorResponse(mockResp);
      });
      expect(message).toBe('O valor adjudicado não pode ser maior que zero para o status selecionado: Finalizado.');
    });

    test('should_return_fallback_on_unexpected_error', async ({ page }) => {
      const message = await page.evaluate(async () => {
        const { parseErrorResponse } = await import('./js/api.js');
        const mockResp = {
          status: 500,
          statusText: 'Internal Server Error',
          json: async () => { throw new Error('Not JSON'); }
        };
        return await parseErrorResponse(mockResp);
      });
      expect(message).toContain('Erro inesperado (500)');
    });

    test('should_return_connection_error_on_null_resp', async ({ page }) => {
      const message = await page.evaluate(async () => {
        const { parseErrorResponse } = await import('./js/api.js');
        return await parseErrorResponse(null);
      });
      expect(message).toBe('Erro de conexão com o servidor.');
    });
  });

});
