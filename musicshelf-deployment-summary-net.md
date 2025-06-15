# 🎵 MusicShelf.net デプロイメント完了サマリー

## 環境URL構成

### 🌟 本番環境
- **Webサイト**: https://musicshelf.net (DNS設定後)
- **API**: https://api.musicshelf.net (DNS設定後)
- **現在のURL（DNS設定前）**: 
  - Web: https://black-plant-0a082b500.2.azurestaticapps.net
  - API: https://indie-music-api.livelyocean-1fc953f9.japaneast.azurecontainerapps.io

### 🧪 QA環境
- **Webサイト**: https://qa.musicshelf.net (DNS設定後)
- **API**: https://api-qa.musicshelf.net (DNS設定後)
- **現在のURL（DNS設定前）**:
  - Web: https://zealous-moss-046c5fa00.1.azurestaticapps.net
  - API: https://indie-music-api-qa.livelyocean-1fc953f9.japaneast.azurecontainerapps.io

## DNS設定要項

### CNAMEレコード
- **@** → black-plant-0a082b500.2.azurestaticapps.net
- **qa** → zealous-moss-046c5fa00.1.azurestaticapps.net  
- **api** → indie-music-api.livelyocean-1fc953f9.japaneast.azurecontainerapps.io
- **api-qa** → indie-music-api-qa.livelyocean-1fc953f9.japaneast.azurecontainerapps.io

## 次のステップ

1. **お名前.comでドメイン取得完了**
2. **DNS設定** - 上記のCNAMEレコードを設定
3. **SSL証明書自動発行** - Azure側で自動的に処理
4. **動作確認** - 各環境の動作テスト

## 技術スタック

- **フロントエンド**: React + Vite (Azure Static Web Apps)
- **バックエンド**: FastAPI + PostgreSQL (Azure Container Apps)
- **ドメイン**: musicshelf.net (お名前.com)
- **SSL**: 自動発行（Let's Encrypt）
- **環境**: 本番・QA完全分離

## 費用概算
- Azure: 約¥9,500/月
- ドメイン: 0円/初年度（2年目以降 ¥1,628/年）
- **合計**: 約¥9,500/月（初年度）