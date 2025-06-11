#!/usr/bin/env python3
"""
開発用データベースリセットスクリプト

注意: このスクリプトは開発環境でのみ使用してください。
本番環境では絶対に実行しないでください。

使用方法:
    python reset_database.py [--with-seed]
"""

import sys
import os
import argparse
from sqlalchemy import text

# プロジェクトルートをPythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.base import Base
from app.db.session import engine
from seed_data import create_seed_data


def reset_database(with_seed: bool = False):
    """データベースをリセット"""
    print("⚠️  データベースリセットを開始します...")
    print("=" * 50)
    
    # 環境変数確認
    env = os.getenv("ENVIRONMENT", "development")
    if env.lower() == "production":
        print("❌ 本番環境ではデータベースリセットは実行できません")
        sys.exit(1)
    
    # 確認プロンプト
    response = input("すべてのデータが削除されます。続行しますか？ (yes/no): ")
    if response.lower() not in ["yes", "y"]:
        print("データベースリセットをキャンセルしました。")
        return
    
    try:
        print("🗑️  既存のテーブルを削除中...")
        
        # すべてのテーブルを削除
        Base.metadata.drop_all(bind=engine)
        print("✅ テーブル削除完了")
        
        print("🏗️  テーブルを再作成中...")
        
        # テーブルを再作成
        Base.metadata.create_all(bind=engine)
        print("✅ テーブル作成完了")
        
        if with_seed:
            print("🌱 Seedデータを作成中...")
            create_seed_data()
        
        print("🎉 データベースリセットが完了しました！")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="開発用データベースリセットスクリプト")
    parser.add_argument(
        "--with-seed", 
        action="store_true", 
        help="リセット後にSeedデータを作成"
    )
    
    args = parser.parse_args()
    reset_database(with_seed=args.with_seed)


if __name__ == "__main__":
    main()