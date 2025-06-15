# musicshelf.net DNS設定ガイド

## お名前.comでの設定

ドメイン取得後、以下のDNSレコードを設定してください：

### 🎯 必須DNS設定

#### 1. CNAMEレコード設定

**本番フロントエンド (musicshelf.net)**
- タイプ: CNAME
- ホスト名: @
- 値: black-plant-0a082b500.2.azurestaticapps.net

**QA環境 (qa.musicshelf.net)**
- タイプ: CNAME
- ホスト名: qa
- 値: zealous-moss-046c5fa00.1.azurestaticapps.net

**API本番 (api.musicshelf.net)**
- タイプ: CNAME
- ホスト名: api
- 値: indie-music-api.livelyocean-1fc953f9.japaneast.azurecontainerapps.io

**API QA (api-qa.musicshelf.net)**
- タイプ: CNAME
- ホスト名: api-qa
- 値: indie-music-api-qa.livelyocean-1fc953f9.japaneast.azurecontainerapps.io

### 設定手順
1. お名前.comの管理画面にログイン
2. 「DNS設定/転送設定」→「DNS設定」
3. 対象ドメインを選択（musicshelf.net）
4. 上記のレコードを追加
5. 「確認画面へ進む」→「設定する」

### 注意事項
- .netドメインはTXTレコードによる検証は不要です
- DNS設定反映には最大24時間かかる場合があります
- 設定完了後、Azure側でカスタムドメインの追加を行います

## 次のステップ
DNS設定完了後、Azure Static Web AppsとContainer Appsにカスタムドメインを追加します。