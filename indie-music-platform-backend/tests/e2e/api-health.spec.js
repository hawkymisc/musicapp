const { test, expect } = require('@playwright/test');

test.describe('API Health and Basic Functionality', () => {
  test('health endpoint should return healthy status', async ({ request }) => {
    const response = await request.get('/health');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
    expect(data.database).toBe('healthy');
    expect(data.timestamp).toBeDefined();
  });

  test('root endpoint should return app info', async ({ request }) => {
    const response = await request.get('/');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.name).toContain('インディーズミュージック');
    expect(data.version).toBe('0.1.0');
    expect(data.status).toBe('running');
  });

  test('should handle rate limiting gracefully', async ({ request }) => {
    // Make multiple rapid requests to test rate limiting
    const requests = [];
    for (let i = 0; i < 50; i++) {
      requests.push(request.get('/direct-test'));
    }
    
    const responses = await Promise.all(requests);
    const rateLimitedResponses = responses.filter(r => r.status() === 429);
    
    // Should have at least some rate-limited responses
    expect(rateLimitedResponses.length).toBeGreaterThan(0);
  });

  test('structured logging should include request IDs', async ({ request }) => {
    const response = await request.get('/health');
    expect(response.status()).toBe(200);
    
    // Check that response includes request ID header
    const requestId = response.headers()['x-request-id'];
    expect(requestId).toBeDefined();
    expect(requestId.length).toBeGreaterThan(0);
  });

  test('CORS headers should be present', async ({ request }) => {
    const response = await request.get('/', {
      headers: {
        'Origin': 'http://localhost:3000'
      }
    });
    
    expect(response.status()).toBe(200);
    // CORS headers should be present for allowed origins
    const corsHeader = response.headers()['access-control-allow-origin'];
    expect(corsHeader).toBeDefined();
  });
});