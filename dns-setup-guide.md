# musicshelf.jp DNS設定ガイド

## お名前.comでの設定

ドメイン取得後、以下のDNSレコードを設定してください：

### 🎯 必須DNS設定

#### 1. 検証用TXTレコード（最初に設定）
- **ホスト名**: @
- **タイプ**: TXT
- **値**: `_z6waaikkqh043pssji0x2ulb9r2lndq`

#### 2. API検証用TXTレコード
- **ホスト名**: asuid.api
- **タイプ**: TXT  
- **値**: `9F6331029585D59AFB7F40B1A7865198052342DB754F8A198D8C3F0BB5539D00`

- **ホスト名**: asuid.api-qa
- **タイプ**: TXT
- **値**: `9F6331029585D59AFB7F40B1A7865198052342DB754F8A198D8C3F0BB5539D00`

#### 3. CNAMEレコード設定（TXT検証完了後）

**本番フロントエンド (musicshelf.jp)**
- タイプ: CNAME
- ホスト名: @
- 値: black-plant-0a082b500.2.azurestaticapps.net

**QA環境 (qa.musicshelf.jp)**
- タイプ: CNAME
- ホスト名: qa
- 値: zealous-moss-046c5fa00.1.azurestaticapps.net

**API本番 (api.musicshelf.jp)**
- タイプ: CNAME
- ホスト名: api
- 値: indie-music-api.livelyocean-1fc953f9.japaneast.azurecontainerapps.io

**API QA (api-qa.musicshelf.jp)**
- タイプ: CNAME
- ホスト名: api-qa
- 値: indie-music-api-qa.livelyocean-1fc953f9.japaneast.azurecontainerapps.io

### 設定手順
1. お名前.comの管理画面にログイン
2. 「DNS設定/転送設定」→「DNS設定」
3. 対象ドメインを選択
4. 上記のレコードを追加
5. 「確認画面へ進む」→「設定する」

## 次のステップ
DNS設定完了後、Azure側でカスタムドメインの検証と追加を行います。