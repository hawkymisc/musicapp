# indie-music-platform-frontend

## Language

React (vite)

## Structure

```[tree]

indie-music-platform-frontend/
└ src/
  ├── assets/            # 画像、アイコンなどの静的ファイル
  ├── components/        # 再利用可能なUIコンポーネント
  │   ├── common/        # ボタン、入力フィールドなどの共通コンポーネント
  │   ├── layout/        # レイアウト関連コンポーネント（ヘッダー、フッターなど）
  │   ├── player/        # 音楽プレーヤー関連コンポーネント
  │   └── track/         # 楽曲関連コンポーネント
  ├── contexts/          # Reactコンテキスト（認証、プレーヤー状態など）
  ├── hooks/             # カスタムフック
  ├── pages/             # 各ページコンポーネント
  │   ├── auth/          # 認証関連ページ（ログイン、登録）
  │   ├── artist/        # アーティスト向けページ
  │   ├── listener/      # リスナー向けページ
  │   └── common/        # 共通ページ（ホーム、検索など）
  ├── services/          # API通信などのサービス
  │   ├── api.js         # APIクライアント設定
  │   ├── auth.js        # 認証関連サービス
  │   ├── artist.js      # アーティスト関連サービス
  │   ├── track.js       # 楽曲関連サービス
  │   ├── payment.js     # 決済関連サービス
  │   └── user.js        # ユーザー関連サービス
  ├── utils/             # ユーティリティ関数
  ├── App.jsx            # ルート・アプリケーションコンポーネント
  ├── main.jsx           # エントリーポイント（Vite標準）
  └── router.jsx         # ルーティング設定
```

## UserFlow

```[Mermaid]
flowchart TD
    Start([アプリ起動]) --> Login{ログイン済み?}
    Login -->|はい| Home[ホーム画面]
    Login -->|いいえ| Auth[認証画面]
    Auth -->|登録/ログイン| Home
    
    Home --> Search[検索]
    Home --> Browse[閲覧]
    Home --> Profile[プロフィール]
    Home --> Play[楽曲再生]
    
    Search --> Results[検索結果]
    Results --> TrackDetail[楽曲詳細]
    Results --> ArtistProfile[アーティストプロフィール]
    
    Browse --> New[新着]
    Browse --> Popular[人気]
    
    New & Popular --> TrackDetail
    
    TrackDetail --> PlayTrack[再生]
    TrackDetail --> PurchaseTrack[購入]
    
    ArtistProfile --> ViewTracks[楽曲一覧]
    ViewTracks --> TrackDetail
    
    Profile -->|アーティスト| ArtistDashboard[アーティストダッシュボード]
    Profile -->|リスナー| PurchaseHistory[購入履歴]
    
    ArtistDashboard --> UploadTrack[楽曲アップロード]
    ArtistDashboard --> ManageTracks[楽曲管理]
    ArtistDashboard --> ViewEarnings[収益確認]
    
    UploadTrack --> EditMetadata[メタデータ編集]
    UploadTrack --> SetPrice[価格設定]
    UploadTrack --> Publish[公開]
    
    PurchaseTrack --> Checkout[決済処理]
    Checkout --> DownloadTrack[ダウンロード]
    
    PurchaseHistory --> DownloadTrack
```

## Database Design

```[mermaid]
erDiagram
    USERS ||--o{ TRACKS : creates
    USERS ||--o{ PURCHASES : makes
    TRACKS ||--o{ PURCHASES : involved_in
    
    USERS {
        string id PK
        string email
        string passwordHash
        string displayName
        string profileImage
        string userType
        datetime createdAt
        datetime updatedAt
        boolean isVerified
    }
    
    TRACKS {
        string id PK
        string artistId FK
        string title
        string description
        string genre
        string coverArtUrl
        string audioFileUrl
        number duration
        number price
        date releaseDate
        datetime createdAt
        datetime updatedAt
        boolean isPublic
        number playCount
    }
    
    PURCHASES {
        string id PK
        string userId FK
        string trackId FK
        number amount
        datetime purchaseDate
        string paymentMethod
        string transactionId
    }
```
