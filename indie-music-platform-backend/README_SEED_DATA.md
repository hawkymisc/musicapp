# Seed Data ガイド

MusicShelfプラットフォームの開発・テスト・デモ用のSeedデータ作成ガイドです。

## 📁 利用可能なSeedデータスクリプト

### 1. 🌱 基本Seedデータ (`seed_data.py` / `create_seed_data.py`)
**用途**: 開発・基本テスト用
```bash
python create_seed_data.py
python create_seed_data.py --reset  # データベースリセット付き
```

**特徴**:
- 基本的なアーティスト・リスナー・楽曲データ
- 開発時の動作確認に適したシンプルなデータセット
- 6アーティスト、5リスナー、12楽曲

### 2. 🎵 デモ用Seedデータ (`demo_seed_data.py`)
**用途**: デモンストレーション・プレゼンテーション用
```bash
python demo_seed_data.py
python demo_seed_data.py --reset  # データベースリセット付き
```

**特徴**:
- **魅力的で実用的なデータ**: 実際のインディーズアーティストを模したリアルなプロフィール
- **多様なジャンル**: エレクトロニック、R&B、フォーク、シンセウェーブ、ジャズフュージョン、インディーロック、クラシッククロスオーバー、Lo-Fi Hip Hop
- **リアルな購買行動**: ユーザーの実際の購買パターンを再現
- **プロフェッショナルな楽曲名**: 「Midnight Reflections」「City Lights Serenade」「Synthwave Highway」など
- **8アーティスト、6リスナー、17楽曲**

### 3. 🧪 QA用Seedデータ (`qa_seed_data.py`)
**用途**: QAテスト・E2Eテスト用
```bash
python qa_seed_data.py
python qa_seed_data.py --reset  # データベースリセット付き
```

**特徴**:
- **E2Eテスト対応**: 固定のテストアカウント（`e2e_listener@example.com`、`e2e_artist@example.com`）
- **境界値テスト**: 最小価格（¥100）、高価格（¥2,000）、長いタイトル、特殊文字
- **エラーケーステスト**: 失敗した決済、ペンディング決済、非公開楽曲
- **多言語テスト**: 特殊文字、Emoji、多言語文字のサポート
- **5アーティスト、5リスナー、10楽曲**

### 4. ⚡ 最小限Seedデータ (`minimal_seed_data.py`)
**用途**: 最小限のテスト・動作確認用
```bash
python minimal_seed_data.py
```

**特徴**:
- 1アーティスト、1リスナー、1楽曲、1購入履歴
- 最小限の動作確認用

## 🚀 使用方法

### 基本的な実行
```bash
# デモ用データの作成
cd indie-music-platform-backend
python demo_seed_data.py

# QA用データの作成
python qa_seed_data.py

# データベースリセット付きで実行
python demo_seed_data.py --reset
```

### データベースの完全リセット
```bash
# 既存データを削除して新しいSeedデータを作成
python reset_database.py --with-seed
```

### 環境別の推奨Seedデータ

| 環境 | 推奨スクリプト | 理由 |
|------|----------------|------|
| **本番** | なし | 本番環境ではSeedデータは使用しない |
| **QA** | `qa_seed_data.py` | E2Eテスト、境界値テスト、エラーケーステストに対応 |
| **デモ** | `demo_seed_data.py` | プレゼンテーション、デモンストレーションに最適 |
| **開発** | `seed_data.py` または `demo_seed_data.py` | 開発者の好みに応じて選択 |
| **ローカルテスト** | `minimal_seed_data.py` | 最小限のデータで動作確認 |

## 📊 作成されるデータの概要

### デモ用Seedデータの内容

#### 🎤 アーティスト
- **Moonlight Echo**: 幻想的なエレクトロニックミュージック
- **Urban Soul Collective**: 都市的なR&B・ソウル
- **Acoustic Garden**: 自然系アコースティックフォーク
- **Neon Dreams**: 80年代シンセウェーブ
- **Jazz Fusion Lab**: 実験的ジャズフュージョン
- **Indie Rock Rebels**: エネルギッシュなインディーロック
- **Classical Crossover**: クラシック×現代音楽
- **Lo-Fi Hip Hop Café**: リラックス系Lo-Fiヒップホップ

#### 🎵 楽曲例
- 「Midnight Reflections」（エレクトロニック・¥450）
- 「City Lights Serenade」（R&B・¥380）
- 「Forest Dawn」（フォーク・¥320）
- 「Synthwave Highway」（シンセウェーブ・¥420）
- 「Revolution Anthem」（インディーロック・¥390）

#### 👥 リスナー
- 音楽愛好家 太郎
- インディーズコレクター 花子
- メロディーハンター 次郎
- 他3名のリアルなユーザープロフィール

### QA用Seedデータの特殊ケース

#### 🧪 テスト用固定アカウント
```
E2Eテストリスナー: e2e_listener@example.com
E2Eテストアーティスト: e2e_artist@example.com
```

#### 📏 境界値テストデータ
- **最小価格楽曲**: ¥100
- **高価格楽曲**: ¥2,000
- **長いタイトル**: 「非常に長いタイトルを持つ楽曲で...」
- **特殊文字楽曲**: 「特殊文字楽曲 🎵 ♪ ♫ ♬」
- **多言語楽曲**: 한국어 中文 العربية Русский

#### 💳 決済テストケース
- **成功した購入**: 正常完了
- **失敗した決済**: エラーハンドリングテスト用
- **ペンディング決済**: 処理中状態のテスト用

## 🔧 開発者向け情報

### Seedデータの拡張
新しいSeedデータを追加する場合：

1. `demo_seed_data.py`をベースにコピー
2. `tracks_data`、`artists_data`、`listeners_data`を編集
3. 適切なファイル名で保存（例：`staging_seed_data.py`）

### E2Eテストとの連携
QA用Seedデータは以下のE2Eテストシナリオに対応：

```javascript
// E2Eテストでの使用例
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
  }
};
```

### カスタムドメイン対応
すべてのSeedデータは本番ドメイン（`@musicshelf.net`）に対応しています。

## ⚠️ 注意事項

1. **本番環境では使用禁止**: Seedデータは開発・テスト・デモ環境でのみ使用
2. **データベースバックアップ**: `--reset`オプション使用前は必要に応じてバックアップを取得
3. **メール衝突**: 複数環境で同じSeedデータを使用する場合はメールアドレスの重複に注意
4. **Firebase UID**: 実際のFirebase認証と連携する場合は適切なUIDを設定

## 🆘 トラブルシューティング

### よくある問題と解決方法

**Q: Seedデータの作成が失敗する**
```bash
# データベースマイグレーションを確認
alembic upgrade head

# データベースをリセットして再実行
python demo_seed_data.py --reset
```

**Q: E2Eテストで固定アカウントが見つからない**
```bash
# QA用Seedデータが正しく作成されているか確認
python qa_seed_data.py
```

**Q: 重複エラーが発生する**
```bash
# 既存データをリセットして実行
python demo_seed_data.py --reset
```

---

**最終更新**: 2025年6月16日  
**対応バージョン**: MusicShelf v1.0  
**作成者**: Claude Code Assistant