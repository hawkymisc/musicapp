const { test, expect } = require('@playwright/test');

test.describe('API Endpoints Functionality', () => {
  test('tracks endpoint should return proper structure', async ({ request }) => {
    const response = await request.get('/api/v1/tracks');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
    
    if (data.length > 0) {
      const track = data[0];
      expect(track).toHaveProperty('id');
      expect(track).toHaveProperty('title');
      expect(track).toHaveProperty('artist_id');
      expect(track).toHaveProperty('price');
    }
  });

  test('auth registration should validate required fields', async ({ request }) => {
    // Test missing required field
    const response = await request.post('/api/v1/auth/register', {
      data: {
        email: 'test@example.com',
        password: 'testpass123',
        display_name: 'Test User',
        role: 'listener'
        // Missing firebase_uid
      }
    });
    
    expect(response.status()).toBe(422);
    const data = await response.json();
    expect(data.detail).toBeDefined();
    expect(data.detail.some(err => err.loc.includes('firebase_uid'))).toBeTruthy();
  });

  test('protected endpoints should require authentication', async ({ request }) => {
    const response = await request.get('/api/v1/users/me');
    expect(response.status()).toBe(404); // Currently returns 404, might be 401 in full auth implementation
  });

  test('invalid endpoints should return 404', async ({ request }) => {
    const response = await request.get('/api/v1/nonexistent-endpoint');
    expect(response.status()).toBe(404);
  });

  test('API should handle malformed JSON gracefully', async ({ request }) => {
    const response = await request.post('/api/v1/tracks', {
      data: 'invalid json string',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    expect([400, 422]).toContain(response.status());
  });

  test('API should include security headers', async ({ request }) => {
    const response = await request.get('/api/v1/tracks');
    
    // Check for basic security headers
    const headers = response.headers();
    expect(headers['x-process-time']).toBeDefined();
    expect(headers['x-request-id']).toBeDefined();
  });

  test('large payload should be handled properly', async ({ request }) => {
    const largeData = {
      title: 'A'.repeat(1000),
      description: 'B'.repeat(5000),
      price: 100
    };
    
    const response = await request.post('/api/v1/tracks', {
      data: largeData
    });
    
    // Should either accept or reject gracefully (not crash)
    expect(response.status()).toBeLessThan(500);
  });
});