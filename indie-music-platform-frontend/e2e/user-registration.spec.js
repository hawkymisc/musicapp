import { test, expect } from '@playwright/test';

test.describe('User Registration Flow', () => {
  test('should display registration form and handle submission', async ({ page }) => {
    // Navigate to registration page
    await page.goto('http://localhost:5173/register');
    
    // Verify page loads correctly
    await expect(page.getByRole('heading', { name: '新規登録' })).toBeVisible();
    
    // Fill out registration form
    await page.getByRole('textbox', { name: '表示名' }).fill('Test User');
    await page.getByRole('textbox', { name: 'メールアドレス' }).fill('test@example.com');
    await page.getByRole('textbox', { name: 'パスワード', exact: true }).fill('password123');
    await page.getByRole('textbox', { name: 'パスワード確認' }).fill('password123');
    
    // Verify user type selector is set to listener by default
    await expect(page.getByRole('combobox')).toHaveValue('listener');
    
    // Submit form
    await page.getByRole('button', { name: '登録' }).click();
    
    // Check for error message (expected due to 404)
    await expect(page.getByText('Request failed with status code 404')).toBeVisible();
  });
  
  test('should navigate to login page from registration', async ({ page }) => {
    await page.goto('http://localhost:5173/register');
    
    // Click login link
    await page.getByRole('link', { name: 'ログイン' }).click();
    
    // Verify navigation to login page
    await expect(page).toHaveURL('http://localhost:5173/login');
    await expect(page.getByRole('heading', { name: 'ログインページ' })).toBeVisible();
  });
});

test.describe('Search Functionality', () => {
  test('should perform music search', async ({ page }) => {
    // Navigate to search page
    await page.goto('http://localhost:5173/search');
    
    // Enter search term
    await page.getByRole('textbox', { name: '楽曲、アーティストを検索' }).fill('test');
    
    // Click search button
    await page.getByRole('button').click();
    
    // Verify URL contains search query
    await expect(page).toHaveURL('http://localhost:5173/search?q=test');
    
    // Verify search results (should be empty)
    await expect(page.getByRole('heading', { name: '検索結果 (0件)' })).toBeVisible();
    await expect(page.getByText('検索条件に一致する楽曲が見つかりませんでした。')).toBeVisible();
  });
});

test.describe('Navigation', () => {
  test('should navigate between pages', async ({ page }) => {
    // Start at home page
    await page.goto('http://localhost:5173/');
    
    // Verify home page elements
    await expect(page.getByText('INDIE MUSIC')).toBeVisible();
    await expect(page.getByRole('heading', { name: '新着楽曲' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'おすすめアーティスト' })).toBeVisible();
    
    // Navigate to search
    await page.getByRole('link', { name: '検索' }).click();
    await expect(page).toHaveURL('http://localhost:5173/search');
    
    // Navigate back to home
    await page.getByRole('link', { name: 'ホーム' }).click();
    await expect(page).toHaveURL('http://localhost:5173/');
    
    // Navigate to library
    await page.getByRole('link', { name: 'マイライブラリ' }).click();
    await expect(page).toHaveURL('http://localhost:5173/library');
  });
});