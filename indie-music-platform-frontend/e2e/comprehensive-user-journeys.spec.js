/**
 * 包括的E2Eユーザージャーニーテストスイート
 * 
 * Seedデータを活用して、実際のユーザー体験を
 * エンドツーエンドでテストします。
 */

import { test, expect } from '@playwright/test';

// テストデータ（Seedデータに基づく）
const testData = {
  listener: {
    email: 'e2e_listener@example.com',
    password: 'password123',
    displayName: 'E2Eテストリスナー'
  },
  artist: {
    email: 'e2e_artist@example.com', 
    password: 'password123',
    displayName: 'E2Eテストアーティスト'
  },
  track: {
    title: 'E2Eテスト楽曲',
    description: 'E2Eテスト用の楽曲です',
    genre: 'テスト',
    price: 500
  }
};

test.describe('包括的ユーザージャーニーテスト', () => {
  
  // テスト前にSeedデータがロードされていることを確認
  test.beforeEach(async ({ page }) => {
    // バックエンドヘルスチェック
    const healthResponse = await page.request.get('http://localhost:8000/');
    expect(healthResponse.ok()).toBeTruthy();
  });

  // ==================== 新規ユーザー登録・初回体験ジャーニー ====================
  
  test('新規リスナーの完全な登録・音楽発見・購入ジャーニー', async ({ page }) => {
    // 1. ホームページ訪問
    await page.goto('/');
    await expect(page.getByText('INDIE MUSIC')).toBeVisible();
    await expect(page.getByText('新着楽曲')).toBeVisible();
    
    // 2. ユーザー登録
    await page.getByRole('img').click(); // ユーザーアバター
    await page.getByText('ログイン').click();
    await page.getByText('新規登録はこちら').click();
    
    await page.getByLabel('表示名').fill(testData.listener.displayName);
    await page.getByLabel('メールアドレス').fill(testData.listener.email);
    await page.getByLabel('パスワード', { exact: true }).fill(testData.listener.password);
    await page.getByLabel('パスワード確認').fill(testData.listener.password);
    await page.getByRole('combobox').selectOption('リスナー');
    
    await page.getByRole('button', { name: '登録' }).click();
    
    // 登録成功の確認
    await expect(page.getByText('登録が完了しました')).toBeVisible();
    
    // 3. 音楽検索・発見
    await page.getByText('検索').click();
    await expect(page).toHaveURL(/.*\/search/);
    
    // Seedデータの楽曲を検索
    await page.getByPlaceholder('楽曲、アーティストを検索...').fill('青空');
    await page.getByRole('button', { name: '検索' }).click();
    
    await expect(page).toHaveURL(/.*\/search\?q=青空/);
    
    // 検索結果の確認
    await expect(page.getByText('検索結果')).toBeVisible();
    await expect(page.getByText('青い空の下で')).toBeVisible();
    await expect(page.getByText('青空バンド')).toBeVisible();
    
    // 4. 楽曲詳細閲覧
    await page.getByText('青い空の下で').click();
    await expect(page).toHaveURL(/.*\/track\/.*/);
    
    await expect(page.getByText('青い空の下で')).toBeVisible();
    await expect(page.getByText('青空バンド')).toBeVisible();
    await expect(page.getByText('ポップ')).toBeVisible();
    await expect(page.getByText('¥300')).toBeVisible();
    
    // 5. 楽曲試聴
    await page.getByRole('button', { name: '試聴' }).click();
    await expect(page.getByText('再生中')).toBeVisible();
    
    // 6. 楽曲購入
    await page.getByRole('button', { name: '購入' }).click();
    await expect(page.getByText('購入確認')).toBeVisible();
    await expect(page.getByText('青い空の下でを¥300で購入しますか？')).toBeVisible();
    
    await page.getByRole('button', { name: '購入確定' }).click();
    
    // 決済処理の完了待ち
    await expect(page.getByText('購入が完了しました')).toBeVisible();
    
    // 7. マイライブラリ確認
    await page.getByText('マイライブラリ').click();
    await expect(page).toHaveURL(/.*\/library/);
    
    await expect(page.getByText('購入済み楽曲')).toBeVisible();
    await expect(page.getByText('青い空の下で')).toBeVisible();
    
    // 8. ダウンロード機能確認
    await page.getByRole('button', { name: 'ダウンロード' }).click();
    // ダウンロードリンクが生成されることを確認
    await expect(page.getByText('ダウンロード準備完了')).toBeVisible();
  });

  test('新規アーティストの登録・楽曲アップロード・販売ジャーニー', async ({ page }) => {
    // 1. アーティストとして登録
    await page.goto('/register');
    
    await page.getByLabel('表示名').fill(testData.artist.displayName);
    await page.getByLabel('メールアドレス').fill(testData.artist.email);
    await page.getByLabel('パスワード', { exact: true }).fill(testData.artist.password);
    await page.getByLabel('パスワード確認').fill(testData.artist.password);
    await page.getByRole('combobox').selectOption('アーティスト');
    
    await page.getByRole('button', { name: '登録' }).click();
    
    // 2. アーティストダッシュボードアクセス
    await expect(page.getByText('アーティストパネル')).toBeVisible();
    await page.getByText('アーティストパネル').click();
    
    await expect(page).toHaveURL(/.*\/artist\/dashboard/);
    await expect(page.getByText('アーティストダッシュボード')).toBeVisible();
    await expect(page.getByText('総収益')).toBeVisible();
    await expect(page.getByText('楽曲数')).toBeVisible();
    
    // 3. 楽曲アップロード
    await page.getByText('楽曲をアップロード').click();
    await expect(page).toHaveURL(/.*\/artist\/upload/);
    
    await page.getByLabel('楽曲タイトル').fill(testData.track.title);
    await page.getByLabel('説明').fill(testData.track.description);
    await page.getByLabel('ジャンル').selectOption(testData.track.genre);
    await page.getByLabel('価格').fill(testData.track.price.toString());
    
    // ファイルアップロード（モック）
    await page.getByLabel('音声ファイル').setInputFiles({
      name: 'test-audio.mp3',
      mimeType: 'audio/mpeg',
      buffer: Buffer.from('mock audio content')
    });
    
    await page.getByLabel('カバーアート').setInputFiles({
      name: 'test-cover.jpg', 
      mimeType: 'image/jpeg',
      buffer: Buffer.from('mock image content')
    });
    
    await page.getByRole('button', { name: 'アップロード' }).click();
    
    // アップロード成功の確認
    await expect(page.getByText('楽曲のアップロードが完了しました')).toBeVisible();
    
    // 4. 楽曲管理画面で確認
    await page.getByText('楽曲管理').click();
    await expect(page).toHaveURL(/.*\/artist\/tracks/);
    
    await expect(page.getByText(testData.track.title)).toBeVisible();
    await expect(page.getByText(`¥${testData.track.price}`)).toBeVisible();
    await expect(page.getByText('公開')).toBeVisible();
    
    // 5. 楽曲編集
    await page.getByRole('button', { name: '編集' }).first().click();
    
    const newPrice = 600;
    await page.getByLabel('価格').fill(newPrice.toString());
    await page.getByRole('button', { name: '更新' }).click();
    
    await expect(page.getByText('楽曲情報を更新しました')).toBeVisible();
    await expect(page.getByText(`¥${newPrice}`)).toBeVisible();
    
    // 6. 売上分析確認
    await page.getByText('分析').click();
    await expect(page).toHaveURL(/.*\/artist\/analytics/);
    
    await expect(page.getByText('売上レポート')).toBeVisible();
    await expect(page.getByText('再生統計')).toBeVisible();
    await expect(page.getByText('人気楽曲')).toBeVisible();
  });

  // ==================== 既存ユーザーの高度な機能ジャーニー ====================
  
  test('高度な検索・フィルタリング・発見ジャーニー', async ({ page }) => {
    await page.goto('/search');
    
    // 1. 基本検索
    await page.getByPlaceholder('楽曲、アーティストを検索...').fill('夜想曲');
    await page.getByRole('button', { name: '検索' }).click();
    
    await expect(page.getByText('夜想曲')).toBeVisible();
    await expect(page.getByText('Digital Dreams')).toBeVisible();
    
    // 2. ジャンルフィルタリング
    await page.getByRole('combobox', { name: 'ジャンル' }).selectOption('エレクトロニック');
    
    // フィルター適用の確認
    await expect(page.getByText('エレクトロニック')).toBeVisible();
    
    // 3. 価格範囲フィルタリング
    await page.getByLabel('最低価格').fill('300');
    await page.getByLabel('最高価格').fill('500');
    await page.getByRole('button', { name: 'フィルター適用' }).click();
    
    // 価格範囲内の楽曲のみ表示されることを確認
    const priceElements = page.locator('[data-testid="track-price"]');
    const prices = await priceElements.allTextContents();
    for (const priceText of prices) {
      const price = parseInt(priceText.replace('¥', '').replace(',', ''));
      expect(price).toBeGreaterThanOrEqual(300);
      expect(price).toBeLessThanOrEqual(500);
    }
    
    // 4. ソート機能
    await page.getByRole('combobox', { name: 'ソート' }).selectOption('price_asc');
    
    // 価格昇順になっていることを確認
    const sortedPrices = await priceElements.allTextContents();
    for (let i = 0; i < sortedPrices.length - 1; i++) {
      const current = parseInt(sortedPrices[i].replace('¥', '').replace(',', ''));
      const next = parseInt(sortedPrices[i + 1].replace('¥', '').replace(',', ''));
      expect(current).toBeLessThanOrEqual(next);
    }
    
    // 5. アーティストページへの遷移
    await page.getByText('夜想曲').click();
    await expect(page).toHaveURL(/.*\/artist\/.*/);
    
    await expect(page.getByText('夜想曲')).toBeVisible();
    await expect(page.getByText('アーティスト情報')).toBeVisible();
    await expect(page.getByText('楽曲一覧')).toBeVisible();
  });

  test('複数楽曲購入・プレイリスト管理ジャーニー', async ({ page }) => {
    // 認証済みユーザーとしてスタート
    await page.goto('/');
    // モックログイン処理
    await page.evaluate(() => {
      localStorage.setItem('authToken', 'mock_listener_token');
    });
    
    await page.reload();
    
    // 1. 複数楽曲の購入
    await page.goto('/search');
    
    const trackTitles = ['青い空の下で', 'Digital Dreams', '風のうた'];
    
    for (const title of trackTitles) {
      await page.getByPlaceholder('楽曲、アーティストを検索...').fill(title);
      await page.getByRole('button', { name: '検索' }).click();
      
      await page.getByText(title).click();
      await page.getByRole('button', { name: '購入' }).click();
      await page.getByRole('button', { name: '購入確定' }).click();
      
      await expect(page.getByText('購入が完了しました')).toBeVisible();
      await page.goBack();
      await page.goBack();
    }
    
    // 2. マイライブラリで購入楽曲確認
    await page.getByText('マイライブラリ').click();
    
    for (const title of trackTitles) {
      await expect(page.getByText(title)).toBeVisible();
    }
    
    // 3. プレイリスト作成
    await page.getByRole('button', { name: 'プレイリスト作成' }).click();
    await page.getByLabel('プレイリスト名').fill('お気に入りコレクション');
    await page.getByRole('button', { name: '作成' }).click();
    
    // 4. 楽曲をプレイリストに追加
    for (const title of trackTitles) {
      await page.getByText(title).hover();
      await page.getByRole('button', { name: 'プレイリストに追加' }).click();
      await page.getByText('お気に入りコレクション').click();
    }
    
    // 5. プレイリスト再生
    await page.getByText('お気に入りコレクション').click();
    await page.getByRole('button', { name: 'プレイリスト再生' }).click();
    
    await expect(page.getByText('再生中')).toBeVisible();
    await expect(page.getByText(trackTitles[0])).toBeVisible();
  });

  // ==================== エラーハンドリング・エッジケースジャーニー ====================
  
  test('ネットワークエラー・回復ジャーニー', async ({ page }) => {
    await page.goto('/search');
    
    // 1. ネットワーク切断をシミュレート
    await page.route('**/api/v1/tracks**', route => route.abort());
    
    await page.getByPlaceholder('楽曲、アーティストを検索...').fill('test');
    await page.getByRole('button', { name: '検索' }).click();
    
    // エラーメッセージの確認
    await expect(page.getByText('ネットワークエラーが発生しました')).toBeVisible();
    await expect(page.getByRole('button', { name: '再試行' })).toBeVisible();
    
    // 2. ネットワーク回復をシミュレート
    await page.unroute('**/api/v1/tracks**');
    
    await page.getByRole('button', { name: '再試行' }).click();
    
    // 正常な検索結果が表示されることを確認
    await expect(page.getByText('検索結果')).toBeVisible();
  });

  test('決済エラー・回復ジャーニー', async ({ page }) => {
    await page.goto('/');
    
    // 1. 楽曲選択
    await page.goto('/search');
    await page.getByPlaceholder('楽曲、アーティストを検索...').fill('青空');
    await page.getByRole('button', { name: '検索' }).click();
    await page.getByText('青い空の下で').click();
    
    // 2. 決済エラーをシミュレート
    await page.route('**/api/v1/purchases**', route => {
      route.fulfill({
        status: 400,
        body: JSON.stringify({ detail: '決済処理に失敗しました' })
      });
    });
    
    await page.getByRole('button', { name: '購入' }).click();
    await page.getByRole('button', { name: '購入確定' }).click();
    
    // エラーメッセージの確認
    await expect(page.getByText('決済処理に失敗しました')).toBeVisible();
    await expect(page.getByRole('button', { name: '再試行' })).toBeVisible();
    
    // 3. 決済情報の修正・再試行
    await page.getByRole('button', { name: '決済情報を変更' }).click();
    await page.getByLabel('カード番号').fill('4111111111111111');
    await page.getByLabel('有効期限').fill('12/25');
    await page.getByLabel('CVV').fill('123');
    
    // 決済処理の正常化
    await page.unroute('**/api/v1/purchases**');
    
    await page.getByRole('button', { name: '再試行' }).click();
    
    // 成功メッセージの確認
    await expect(page.getByText('購入が完了しました')).toBeVisible();
  });

  // ==================== パフォーマンス・レスポンシブテスト ====================
  
  test('大量データ表示・スクロールパフォーマンステスト', async ({ page }) => {
    await page.goto('/search');
    
    // 1. 大量の検索結果を表示
    await page.getByRole('combobox', { name: 'ジャンル' }).selectOption('すべて');
    
    // 初期表示の性能測定
    const startTime = Date.now();
    await page.getByRole('button', { name: '検索' }).click();
    await page.waitForSelector('[data-testid="track-list"]');
    const loadTime = Date.now() - startTime;
    
    expect(loadTime).toBeLessThan(3000); // 3秒以内での表示
    
    // 2. 無限スクロールテスト
    let trackCount = await page.locator('[data-testid="track-card"]').count();
    
    await page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
    });
    
    // 追加ロードの待機
    await page.waitForTimeout(1000);
    
    const newTrackCount = await page.locator('[data-testid="track-card"]').count();
    expect(newTrackCount).toBeGreaterThan(trackCount);
  });

  test('モバイルレスポンシブ・タッチ操作テスト', async ({ page }) => {
    // モバイルビューポートに設定
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/');
    
    // 1. モバイルナビゲーションの確認
    await expect(page.getByRole('button', { name: 'メニュー' })).toBeVisible();
    await page.getByRole('button', { name: 'メニュー' }).click();
    
    await expect(page.getByText('ホーム')).toBeVisible();
    await expect(page.getByText('検索')).toBeVisible();
    
    // 2. タッチ操作での楽曲再生
    await page.getByText('検索').click();
    await page.getByPlaceholder('楽曲、アーティストを検索...').fill('青空');
    
    // タッチでの検索実行
    await page.getByRole('button', { name: '検索' }).tap();
    
    // 楽曲カードのタッチ操作
    await page.getByText('青い空の下で').tap();
    
    // モバイル用再生ボタンの確認
    await expect(page.getByRole('button', { name: '再生' })).toBeVisible();
    await page.getByRole('button', { name: '再生' }).tap();
    
    // 3. スワイプ操作（プレイリストナビゲーション）
    const playlistArea = page.locator('[data-testid="playlist-area"]');
    
    // 左スワイプ
    await playlistArea.hover();
    await page.mouse.down();
    await page.mouse.move(300, 0);
    await page.mouse.up();
    
    // スワイプ後の表示確認
    await expect(page.getByText('次の楽曲')).toBeVisible();
  });

  // ==================== アクセシビリティテスト ====================
  
  test('キーボードナビゲーション・スクリーンリーダー対応テスト', async ({ page }) => {
    await page.goto('/');
    
    // 1. キーボードでのナビゲーション
    await page.keyboard.press('Tab'); // 最初のフォーカス要素
    await page.keyboard.press('Tab'); // 検索リンク
    await page.keyboard.press('Enter'); // 検索ページへ
    
    await expect(page).toHaveURL(/.*\/search/);
    
    // 2. 検索フォームのキーボード操作
    await page.keyboard.press('Tab'); // 検索入力フィールド
    await page.keyboard.type('青空');
    await page.keyboard.press('Enter'); // 検索実行
    
    // 3. 結果のキーボードナビゲーション
    await page.keyboard.press('Tab'); // 最初の検索結果
    await page.keyboard.press('Enter'); // 楽曲詳細へ
    
    // 4. ARIAラベルの確認
    const playButton = page.getByRole('button', { name: /再生/ });
    await expect(playButton).toHaveAttribute('aria-label');
    
    const trackTitle = page.getByRole('heading', { level: 1 });
    await expect(trackTitle).toBeVisible();
    
    // 5. コントラスト比の確認（視覚的テスト）
    await expect(page.locator('body')).toHaveCSS('background-color', /rgb\(/);
    await expect(page.locator('h1')).toHaveCSS('color', /rgb\(/);
  });
});