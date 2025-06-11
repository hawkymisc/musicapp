"""
開発用データベース作成スクリプト
"""
from app.db.session import create_tables

if __name__ == "__main__":
    print("データベーステーブルを作成しています...")
    create_tables()
    print("データベーステーブルの作成が完了しました。")
