#!/usr/bin/env python3
"""
データベーステーブル初期化スクリプト
SQLiteデータベースに必要なテーブルを作成する
"""
import sys
import os
import logging
from sqlalchemy import create_engine, text

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# プロジェクトルートをsys.pathに追加
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def create_database_tables():
    """データベーステーブルを作成"""
    
    # SQLiteデータベースのURL
    database_url = "sqlite:///./dev.db"
    
    logger.info(f"データベース接続: {database_url}")
    
    try:
        # データベースエンジンを作成
        engine = create_engine(database_url, echo=True)
        
        # テーブル作成SQL
        create_tables_sql = """
        -- ユーザーテーブル
        CREATE TABLE IF NOT EXISTS user (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            display_name TEXT NOT NULL,
            profile_image TEXT,
            user_type TEXT NOT NULL DEFAULT 'listener',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_verified BOOLEAN DEFAULT FALSE
        );

        -- 楽曲テーブル
        CREATE TABLE IF NOT EXISTS track (
            id TEXT PRIMARY KEY,
            artist_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            genre TEXT,
            cover_art_url TEXT,
            audio_file_url TEXT,
            duration INTEGER,
            price DECIMAL(10, 2),
            release_date DATE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_public BOOLEAN DEFAULT TRUE,
            play_count INTEGER DEFAULT 0,
            FOREIGN KEY (artist_id) REFERENCES user (id)
        );

        -- 購入テーブル
        CREATE TABLE IF NOT EXISTS purchase (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            track_id TEXT NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            payment_method TEXT,
            transaction_id TEXT,
            status TEXT DEFAULT 'completed',
            FOREIGN KEY (user_id) REFERENCES user (id),
            FOREIGN KEY (track_id) REFERENCES track (id)
        );

        -- 再生履歴テーブル
        CREATE TABLE IF NOT EXISTS play_history (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            track_id TEXT NOT NULL,
            played_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            duration_played INTEGER,
            FOREIGN KEY (user_id) REFERENCES user (id),
            FOREIGN KEY (track_id) REFERENCES track (id)
        );

        -- インデックス作成
        CREATE INDEX IF NOT EXISTS idx_track_artist_id ON track (artist_id);
        CREATE INDEX IF NOT EXISTS idx_track_public ON track (is_public);
        CREATE INDEX IF NOT EXISTS idx_track_created_at ON track (created_at);
        CREATE INDEX IF NOT EXISTS idx_purchase_user_id ON purchase (user_id);
        CREATE INDEX IF NOT EXISTS idx_purchase_track_id ON purchase (track_id);
        CREATE INDEX IF NOT EXISTS idx_play_history_user_id ON play_history (user_id);
        CREATE INDEX IF NOT EXISTS idx_play_history_track_id ON play_history (track_id);
        """
        
        # テーブルを作成
        with engine.connect() as connection:
            # SQLを分割して実行
            sql_statements = [stmt.strip() for stmt in create_tables_sql.split(';') if stmt.strip()]
            
            for sql in sql_statements:
                logger.info(f"SQL実行: {sql[:50]}...")
                connection.execute(text(sql))
            
            connection.commit()
        
        logger.info("✅ データベーステーブルが正常に作成されました")
        
        # テーブルの確認
        with engine.connect() as connection:
            result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            logger.info(f"作成されたテーブル: {tables}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ データベーステーブル作成エラー: {e}")
        return False

def create_sample_data():
    """サンプルデータを作成"""
    database_url = "sqlite:///./dev.db"
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as connection:
            # サンプルユーザー
            connection.execute(text("""
                INSERT OR IGNORE INTO user (id, email, display_name, user_type) VALUES
                ('user1', 'artist1@example.com', 'Test Artist 1', 'artist'),
                ('user2', 'artist2@example.com', 'Test Artist 2', 'artist'),
                ('user3', 'listener1@example.com', 'Test Listener 1', 'listener')
            """))
            
            # サンプル楽曲
            connection.execute(text("""
                INSERT OR IGNORE INTO track (id, artist_id, title, description, genre, price, duration) VALUES
                ('track1', 'user1', 'Sample Song 1', 'A great test song', 'Pop', 100.00, 180),
                ('track2', 'user1', 'Sample Song 2', 'Another test song', 'Rock', 150.00, 200),
                ('track3', 'user2', 'Sample Song 3', 'Third test song', 'Jazz', 120.00, 220)
            """))
            
            connection.commit()
            
        logger.info("✅ サンプルデータが作成されました")
        return True
        
    except Exception as e:
        logger.error(f"❌ サンプルデータ作成エラー: {e}")
        return False

def main():
    """メイン実行関数"""
    logger.info("=== データベース初期化開始 ===")
    
    # テーブル作成
    if not create_database_tables():
        sys.exit(1)
    
    # サンプルデータ作成
    create_sample_data()
    
    logger.info("=== データベース初期化完了 ===")

if __name__ == "__main__":
    main()
