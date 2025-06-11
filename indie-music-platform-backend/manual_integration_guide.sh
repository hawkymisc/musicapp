#!/bin/bash
# フロントエンド・バックエンド統合テストガイド
# このスクリプトは手動実行手順をガイドします

echo "🚀 インディーズミュージックプラットフォーム 統合テスト"
echo "=========================================="
echo ""

echo "📋 手動実行手順:"
echo ""

echo "1️⃣ バックエンドサーバーの起動"
echo "新しいターミナルウィンドウで以下を実行："
echo "cd /Users/hwaka/Projects/musicapp/indie-music-platform-backend"
echo "./.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload"
echo ""

echo "2️⃣ フロントエンドサーバーの起動"
echo "別の新しいターミナルウィンドウで以下を実行："
echo "cd /Users/hwaka/Projects/musicapp/indie-music-platform-frontend"
echo "npm run dev"
echo ""

echo "3️⃣ 動作確認"
echo "ブラウザで以下のURLにアクセス："
echo "- フロントエンド: http://localhost:5173"
echo "- バックエンドAPI: http://localhost:8001"
echo "- API ドキュメント: http://localhost:8001/docs"
echo ""

echo "4️⃣ テスト項目"
echo "✅ フロントエンドページが正常に表示される"
echo "✅ ブラウザのネットワークタブでAPIリクエストが送信される"
echo "✅ バックエンドAPIが正常にレスポンスを返す"
echo "✅ CORS エラーが発生しない"
echo ""

echo "🔧 トラブルシューティング"
echo "- ポート競合エラー: lsof -i :8001 でプロセスを確認"
echo "- CORS エラー: バックエンドの設定でlocalhost:5173が許可されているか確認"
echo "- API エラー: /docs でAPIドキュメントを確認"
echo ""

echo "📊 APIエンドポイントテスト"
echo "サーバーが起動したら、以下のコマンドでAPIテストを実行："
echo "cd /Users/hwaka/Projects/musicapp/indie-music-platform-backend"
echo "./.venv/bin/python test_api_standalone.py"
echo ""

echo "=========================================="
echo "🎯 成功の指標:"
echo "✅ フロントエンドが localhost:5173 で表示される"
echo "✅ バックエンドが localhost:8001 で応答する" 
echo "✅ フロントエンドからAPIリクエストが成功する"
echo "✅ ブラウザコンソールにエラーがない"
echo "=========================================="
