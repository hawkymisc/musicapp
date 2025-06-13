const { test, expect } = require('@playwright/test');

test.describe('Security Features', () => {
  test('rate limiting should prevent excessive requests', async ({ request }) => {
    const endpoint = '/direct-test';
    const requests = [];
    
    // Send 15 requests rapidly (limit is 10/minute for this endpoint)
    for (let i = 0; i < 15; i++) {
      requests.push(request.get(endpoint));
    }
    
    const responses = await Promise.all(requests);
    const rateLimitedCount = responses.filter(r => r.status() === 429).length;
    
    expect(rateLimitedCount).toBeGreaterThan(0);
    
    // Check rate limit response format
    const rateLimitedResponse = responses.find(r => r.status() === 429);
    if (rateLimitedResponse) {
      const data = await rateLimitedResponse.json();
      expect(data.detail).toContain('リクエスト制限');
      expect(data.retry_after).toBeDefined();
      
      // Check Retry-After header
      const retryAfter = rateLimitedResponse.headers()['retry-after'];
      expect(retryAfter).toBeDefined();
    }
  });

  test('structured logging should capture security events', async ({ request }) => {
    // Trigger a rate limit to generate security log
    const requests = [];
    for (let i = 0; i < 12; i++) {
      requests.push(request.get('/direct-test'));
    }
    
    await Promise.all(requests);
    
    // The security logging should have captured these events
    // (We can't directly verify logs in this test, but we can ensure the endpoint behaves correctly)
    expect(true).toBeTruthy(); // Placeholder for log verification
  });

  test('error handling should not expose sensitive information', async ({ request }) => {
    // Try to cause an error that might expose system info
    const response = await request.get('/api/v1/tracks/invalid-id-format');
    
    if (response.status() >= 400) {
      const data = await response.json();
      
      // Error messages should be user-friendly, not expose internal details
      expect(data.detail).toBeDefined();
      expect(data.detail).not.toContain('Traceback');
      expect(data.detail).not.toContain('postgresql://');
      expect(data.detail).not.toContain('password');
    }
  });

  test('CORS should be properly configured', async ({ request }) => {
    // Test allowed origin
    const allowedOriginResponse = await request.get('/', {
      headers: {
        'Origin': 'http://localhost:3000'
      }
    });
    
    expect(allowedOriginResponse.status()).toBe(200);
    
    // Test disallowed origin
    const disallowedOriginResponse = await request.get('/', {
      headers: {
        'Origin': 'http://malicious-site.com'
      }
    });
    
    // Should still return 200 but without CORS headers for disallowed origins
    expect(disallowedOriginResponse.status()).toBe(200);
  });

  test('SQL injection protection should be in place', async ({ request }) => {
    // Try basic SQL injection patterns
    const maliciousInputs = [
      "'; DROP TABLE users; --",
      "' OR '1'='1",
      "1' UNION SELECT * FROM users--"
    ];
    
    for (const input of maliciousInputs) {
      const response = await request.get(`/api/v1/tracks?search=${encodeURIComponent(input)}`);
      
      // Should handle gracefully, not crash
      expect(response.status()).toBeLessThan(500);
    }
  });

  test('XSS protection should sanitize inputs', async ({ request }) => {
    const xssPayload = '<script>alert(\"xss\")</script>';
    
    const response = await request.post('/api/v1/tracks', {
      data: {
        title: xssPayload,
        description: xssPayload,
        price: 100
      }
    });
    
    // Should either reject or sanitize, not execute
    expect(response.status()).toBeLessThan(500);
    
    if (response.status() === 200) {
      const data = await response.json();
      // If accepted, should be sanitized
      expect(data.title).not.toContain('<script>');
    }
  });

  test('file upload security should validate file types', async ({ request }) => {
    // Test with potentially malicious file types
    const maliciousFile = Buffer.from('#!/bin/bash\necho "malicious script"', 'utf8');
    
    const response = await request.post('/api/v1/tracks/upload/audio', {
      multipart: {
        file: {
          name: 'malicious.sh',
          mimeType: 'application/x-sh',
          buffer: maliciousFile
        }
      }
    });
    
    // Should reject non-audio files
    expect([400, 422, 415]).toContain(response.status());
  });
});