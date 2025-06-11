#!/usr/bin/env python3
"""
Seedデータ作成の実行スクリプト

実行前にデータベースマイグレーションが完了していることを確認してください:
    alembic upgrade head

使用方法:
    python create_seed_data.py
"""

import sys
import os

# プロジェクトルートをPythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from seed_data import create_seed_data

if __name__ == "__main__":
    print("🌱 インディーズミュージックプラットフォーム - Seedデータ作成")
    print("=" * 50)
    
    try:
        create_seed_data()
    except KeyboardInterrupt:
        print("\n⚠️  ユーザーによってキャンセルされました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        sys.exit(1)