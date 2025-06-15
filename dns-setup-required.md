# 🚨 緊急: DNS設定が必要です

お名前.comの管理画面で以下のレコードを設定してください：

## 必須TXTレコード（検証用）

### 本番環境検証
- **ホスト名**: @
- **タイプ**: TXT
- **値**: `_u8jjfoahripjlambbqpni8rlz1lg7s6`

### QA環境検証  
- **ホスト名**: qa
- **タイプ**: TXT
- **値**: `_71v6505cmge63kawgtnput26iskmk9z`

## CNAMEレコード（TXT検証完了後）

### 本番環境
- **ホスト名**: @
- **タイプ**: CNAME
- **値**: black-plant-0a082b500.2.azurestaticapps.net

### QA環境
- **ホスト名**: qa
- **タイプ**: CNAME
- **値**: zealous-moss-046c5fa00.1.azurestaticapps.net

### API本番
- **ホスト名**: api
- **タイプ**: CNAME
- **値**: indie-music-api.livelyocean-1fc953f9.japaneast.azurecontainerapps.io

### API QA
- **ホスト名**: api-qa
- **タイプ**: CNAME
- **値**: indie-music-api-qa.livelyocean-1fc953f9.japaneast.azurecontainerapps.io

## 設定手順
1. お名前.comの管理画面にログイン
2. DNS設定画面で上記レコードを追加
3. 設定完了後、私に報告してください

設定が完了すると自動的にSSL証明書が発行され、カスタムドメインが有効になります。