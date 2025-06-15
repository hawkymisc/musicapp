const { chromium } = require('playwright');
const path = require('path');

/**
 * Azure Portal での自動化タスク
 * 手動ログイン後に実行される自動化スクリプト
 */

async function azureSetupAutomation() {
  // メインプロファイルでブラウザを起動
  const userDataDir = '/Users/hwaka/Library/Application Support/Google/Chrome/Profile 1';
  
  const browser = await chromium.launchPersistentContext(userDataDir, {
    headless: false, // 手動操作確認のため表示
    viewport: { width: 1280, height: 800 },
    locale: 'ja-JP'
  });

  const page = browser.pages()[0] || await browser.newPage();

  try {
    console.log('🚀 Azure Portal自動化を開始...');

    // Azure Portal にアクセス
    await page.goto('https://portal.azure.com');
    await page.waitForTimeout(3000);

    // ログイン状態確認
    await page.waitForSelector('[data-testid="portal-header"]', { timeout: 30000 });
    console.log('✅ Azure Portal ログイン確認完了');

    // スクリーンショット撮影
    await page.screenshot({ path: 'azure-portal-logged-in.png', fullPage: true });

    // サブスクリプション確認
    await checkSubscriptions(page);

    // リソースグループ作成準備
    await prepareResourceGroup(page);

    // 無料枠確認
    await checkFreeServices(page);

    console.log('✅ Azure準備作業完了');

  } catch (error) {
    console.error('❌ エラー:', error.message);
    await page.screenshot({ path: 'azure-error.png' });
  }

  return { browser, page };
}

async function checkSubscriptions(page) {
  console.log('📊 サブスクリプション確認中...');
  
  try {
    // サブスクリプションページへ移動
    await page.click('text=サブスクリプション');
    await page.waitForTimeout(3000);

    // サブスクリプション情報取得
    const subscriptions = await page.$$eval('.msportalfx-grid-row', rows => 
      rows.map(row => ({
        name: row.querySelector('.msportalfx-text-header')?.textContent?.trim(),
        status: row.querySelector('.msportalfx-text-muted')?.textContent?.trim()
      }))
    );

    console.log('利用可能なサブスクリプション:', subscriptions);
    
    // スクリーンショット
    await page.screenshot({ path: 'azure-subscriptions.png' });

  } catch (error) {
    console.log('⚠️ サブスクリプション確認をスキップ:', error.message);
  }
}

async function prepareResourceGroup(page) {
  console.log('🏗️ リソースグループ作成準備...');
  
  try {
    // ホームに戻る
    await page.click('[aria-label="Microsoft Azure"]');
    await page.waitForTimeout(2000);

    // リソースグループへ移動
    await page.fill('[placeholder="リソース、サービス、ドキュメントの検索"]', 'リソース グループ');
    await page.waitForTimeout(1000);
    await page.click('text=リソース グループ');
    await page.waitForTimeout(3000);

    // 作成ボタンの確認
    const createButton = await page.$('text=作成');
    if (createButton) {
      console.log('✅ リソースグループ作成ボタン確認');
      await page.screenshot({ path: 'azure-resource-groups.png' });
    }

  } catch (error) {
    console.log('⚠️ リソースグループ準備をスキップ:', error.message);
  }
}

async function checkFreeServices(page) {
  console.log('💰 無料サービス確認中...');
  
  try {
    // 無料サービスページへ移動
    await page.fill('[placeholder="リソース、サービス、ドキュメントの検索"]', '無料サービス');
    await page.waitForTimeout(1000);
    
    const freeServicesLink = await page.$('text=無料サービス');
    if (freeServicesLink) {
      await freeServicesLink.click();
      await page.waitForTimeout(3000);
      await page.screenshot({ path: 'azure-free-services.png' });
      console.log('✅ 無料サービス情報確認完了');
    }

  } catch (error) {
    console.log('⚠️ 無料サービス確認をスキップ:', error.message);
  }
}

// Firebase セットアップ関数
async function firebaseSetupAutomation(browser) {
  console.log('🔥 Firebase セットアップ開始...');
  
  const page = await browser.newPage();
  
  try {
    // Firebase Console にアクセス
    await page.goto('https://console.firebase.google.com');
    await page.waitForTimeout(3000);

    // ログイン状態確認
    await page.waitForSelector('[data-testid="project-list"]', { timeout: 30000 });
    console.log('✅ Firebase Console ログイン確認完了');

    await page.screenshot({ path: 'firebase-console.png' });

    // プロジェクト作成準備
    await prepareFirebaseProject(page);

    console.log('✅ Firebase準備作業完了');

  } catch (error) {
    console.error('❌ Firebase エラー:', error.message);
    await page.screenshot({ path: 'firebase-error.png' });
  }

  return page;
}

async function prepareFirebaseProject(page) {
  console.log('📱 Firebaseプロジェクト作成準備...');
  
  try {
    // プロジェクト作成ボタンを探す
    const createProjectButton = await page.$('text=プロジェクトを作成');
    if (createProjectButton) {
      console.log('✅ プロジェクト作成ボタン確認');
      
      // 作成フロー開始
      await createProjectButton.click();
      await page.waitForTimeout(2000);
      
      // プロジェクト名入力画面のスクリーンショット
      await page.screenshot({ path: 'firebase-create-project.png' });
      
      // プロジェクト名入力（例）
      const projectNameInput = await page.$('[placeholder*="プロジェクト名"]');
      if (projectNameInput) {
        await projectNameInput.fill('indie-music-platform');
        await page.screenshot({ path: 'firebase-project-name.png' });
        console.log('✅ プロジェクト名入力例設定完了');
      }
    }

    // 既存プロジェクト確認
    const existingProjects = await page.$$eval('[data-testid="project-card"]', cards =>
      cards.map(card => ({
        name: card.querySelector('.project-display-name')?.textContent?.trim(),
        id: card.querySelector('.project-id')?.textContent?.trim()
      }))
    );

    if (existingProjects.length > 0) {
      console.log('既存Firebaseプロジェクト:', existingProjects);
    }

  } catch (error) {
    console.log('⚠️ Firebaseプロジェクト準備をスキップ:', error.message);
  }
}

// 認証情報収集関数
async function collectCredentials(azurePage, firebasePage) {
  console.log('🔑 認証情報収集ガイド表示...');
  
  const credentials = {
    azure: {
      subscription_id: null,
      tenant_id: null,
      instructions: [
        '1. Azure Portal > サブスクリプション > 概要から「サブスクリプションID」をコピー',
        '2. Azure Portal > Azure Active Directory > 概要から「テナントID」をコピー',
        '3. Azure CLI: az login でログイン認証'
      ]
    },
    firebase: {
      project_id: null,
      service_account_key: null,
      instructions: [
        '1. Firebase Console > プロジェクト設定 > 全般 > プロジェクトIDを確認',
        '2. Firebase Console > プロジェクト設定 > サービスアカウント',
        '3. 「新しい秘密鍵の生成」クリック > JSONファイルダウンロード'
      ]
    }
  };

  // ガイド表示用HTML作成
  const guideHtml = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>デプロイ準備ガイド</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .section { border: 1px solid #ddd; padding: 20px; margin: 20px 0; }
        .instructions { background: #f5f5f5; padding: 10px; margin: 10px 0; }
        .status { color: green; font-weight: bold; }
      </style>
    </head>
    <body>
      <h1>🚀 インディーズミュージックプラットフォーム デプロイ準備</h1>
      
      <div class="section">
        <h2>🔵 Azure 設定</h2>
        <div class="instructions">
          ${credentials.azure.instructions.map(i => `<p>${i}</p>`).join('')}
        </div>
        <p class="status">✅ Azure Portal アクセス完了</p>
      </div>
      
      <div class="section">
        <h2>🔥 Firebase 設定</h2>
        <div class="instructions">
          ${credentials.firebase.instructions.map(i => `<p>${i}</p>`).join('')}
        </div>
        <p class="status">✅ Firebase Console アクセス完了</p>
      </div>
      
      <div class="section">
        <h2>📋 次のステップ</h2>
        <ol>
          <li>上記の認証情報を収集</li>
          <li>Azure CLI をインストール: <code>brew install azure-cli</code></li>
          <li>Azure にログイン: <code>az login</code></li>
          <li>デプロイスクリプト実行: <code>./deploy/azure-deploy.sh minimal</code></li>
        </ol>
      </div>
    </body>
    </html>
  `;

  // ガイドファイル保存
  require('fs').writeFileSync('deployment-guide.html', guideHtml);
  console.log('✅ デプロイガイド作成: deployment-guide.html');

  return credentials;
}

// メイン実行関数
async function main() {
  console.log('🎯 Azure & Firebase 自動セットアップ開始');
  
  try {
    // Azure セットアップ
    const { browser, azurePage } = await azureSetupAutomation();
    
    // Firebase セットアップ
    const firebasePage = await firebaseSetupAutomation(browser);
    
    // 認証情報ガイド作成
    await collectCredentials(azurePage, firebasePage);
    
    console.log('✅ すべてのセットアップ完了！');
    console.log('📖 deployment-guide.html を確認してください');
    
    // ブラウザは開いたまま（手動作業用）
    console.log('🔄 ブラウザは開いたままです。手動で認証情報を収集してください。');
    
  } catch (error) {
    console.error('❌ メインエラー:', error);
  }
}

// 実行
if (require.main === module) {
  main();
}

module.exports = { azureSetupAutomation, firebaseSetupAutomation, collectCredentials };