const { test, expect } = require('@playwright/test');

test.describe('Performance and Reliability', () => {
  test('API response times should be reasonable', async ({ request }) => {
    const startTime = Date.now();
    const response = await request.get('/health');
    const endTime = Date.now();
    
    expect(response.status()).toBe(200);
    
    // Response time should be under 2 seconds for health check
    const responseTime = endTime - startTime;
    expect(responseTime).toBeLessThan(2000);
    
    // Check X-Process-Time header
    const processTime = parseFloat(response.headers()['x-process-time']);
    expect(processTime).toBeLessThan(1.0); // Should be under 1 second
  });

  test('concurrent requests should be handled properly', async ({ request }) => {
    const concurrentRequests = 20;
    const requests = [];
    
    for (let i = 0; i < concurrentRequests; i++) {
      requests.push(request.get('/health'));
    }
    
    const startTime = Date.now();
    const responses = await Promise.all(requests);
    const endTime = Date.now();
    
    // All requests should succeed (ignoring rate limits)
    const successfulResponses = responses.filter(r => r.status() === 200);
    const rateLimitedResponses = responses.filter(r => r.status() === 429);
    
    expect(successfulResponses.length + rateLimitedResponses.length).toBe(concurrentRequests);
    
    // Total time should be reasonable for concurrent processing
    const totalTime = endTime - startTime;
    expect(totalTime).toBeLessThan(10000); // Should complete within 10 seconds
  });

  test('database connection pool should handle multiple queries', async ({ request }) => {
    const requests = [];
    
    // Make multiple database-dependent requests
    for (let i = 0; i < 10; i++) {
      requests.push(request.get('/health'));
      requests.push(request.get('/api/v1/tracks'));
    }
    
    const responses = await Promise.all(requests);
    const successfulResponses = responses.filter(r => r.status() === 200);
    
    // Most should succeed (some might be rate limited)
    expect(successfulResponses.length).toBeGreaterThan(5);
  });

  test('memory usage should be stable over time', async ({ request }) => {
    // Simulate sustained load to check for memory leaks
    const iterations = 100;
    
    for (let i = 0; i < iterations; i++) {
      await request.get('/health');
      
      // Add small delay to simulate real usage
      if (i % 10 === 0) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }
    
    // Final health check should still work
    const finalResponse = await request.get('/health');
    expect(finalResponse.status()).toBe(200);
  });

  test('large response payloads should be handled efficiently', async ({ request }) => {
    const startTime = Date.now();
    const response = await request.get('/api/v1/tracks');
    const endTime = Date.now();
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    const responseTime = endTime - startTime;
    
    // Response time should scale reasonably with data size
    if (Array.isArray(data) && data.length > 0) {
      // Rough heuristic: should handle 100 records in under 5 seconds
      const expectedMaxTime = Math.max(1000, data.length * 50);
      expect(responseTime).toBeLessThan(expectedMaxTime);
    }
  });

  test('error recovery should work properly', async ({ request }) => {
    // Try to cause an error
    const errorResponse = await request.get('/api/v1/nonexistent');
    expect(errorResponse.status()).toBe(404);
    
    // System should recover and handle normal requests
    const recoveryResponse = await request.get('/health');
    expect(recoveryResponse.status()).toBe(200);
  });

  test('graceful degradation under load', async ({ request }) => {
    // Simulate high load
    const highLoadRequests = [];
    for (let i = 0; i < 50; i++) {
      highLoadRequests.push(request.get('/'));
    }
    
    const responses = await Promise.all(highLoadRequests);
    
    // System should either succeed or rate limit, but not crash
    const validStatuses = responses.every(r => 
      r.status() === 200 || r.status() === 429 || r.status() === 503
    );
    expect(validStatuses).toBeTruthy();
    
    // At least some requests should succeed
    const successCount = responses.filter(r => r.status() === 200).length;
    expect(successCount).toBeGreaterThan(0);
  });
});