#!/usr/bin/env python3
"""
フロントエンド・バックエンドAPI対応表とエンドポイント修正提案
"""

def check_api_compatibility():
    """APIエンドポイントの互換性チェック"""
    
    print("🔍 API エンドポイント互換性チェック")
    print("="*60)
    
    # フロントエンドが期待するエンドポイントとバックエンドの実装
    api_mapping = [
        {
            "frontend_expects": "GET /api/v1/music",
            "backend_implements": "GET /api/v1/tracks", 
            "used_in": "getNewReleases()",
            "status": "❌ 不一致",
            "fix": "バックエンドに /music エイリアスを追加"
        },
        {
            "frontend_expects": "GET /api/v1/artists/featured",
            "backend_implements": "GET /api/v1/artists/*",
            "used_in": "getFeaturedArtists()",
            "status": "⚠️ 要確認",
            "fix": "featuredエンドポイント実装が必要"
        },
        {
            "frontend_expects": "GET /api/v1/music/{id}",
            "backend_implements": "GET /api/v1/tracks/{id}",
            "used_in": "getTrackById()",
            "status": "❌ 不一致",
            "fix": "バックエンドに /music/{id} エイリアスを追加"
        },
        {
            "frontend_expects": "GET /api/v1/music/search",
            "backend_implements": "GET /api/v1/tracks/search(?)",
            "used_in": "searchTracks()",
            "status": "❌ 不一致",
            "fix": "バックエンドに /music/search エイリアスを追加"
        },
        {
            "frontend_expects": "POST /api/v1/music",
            "backend_implements": "POST /api/v1/tracks",
            "used_in": "uploadTrack()",
            "status": "❌ 不一致", 
            "fix": "バックエンドに /music POST エイリアスを追加"
        },
        {
            "frontend_expects": "POST /api/v1/music/{id}/play",
            "backend_implements": "POST /api/v1/stream/{id}/play(?)",
            "used_in": "recordPlay()",
            "status": "❌ 不一致",
            "fix": "エンドポイント統一が必要"
        }
    ]
    
    print("📋 API対応表:")
    print()
    
    for mapping in api_mapping:
        print(f"フロントエンド: {mapping['frontend_expects']}")
        print(f"バックエンド:   {mapping['backend_implements']}")
        print(f"使用箇所:     {mapping['used_in']}")
        print(f"ステータス:   {mapping['status']}")
        print(f"修正方法:     {mapping['fix']}")
        print("-" * 60)
    
    print("\n🔧 推奨修正方法:")
    print("="*60)
    
    print("\n1️⃣ バックエンドにエイリアスルートを追加:")
    print("""
# app/api/router.py に追加
# 互換性のためのエイリアスルート
@v1_router.get("/music")
async def get_music_alias():
    # /tracks へのリダイレクトまたはプロキシ
    pass

@v1_router.get("/music/{track_id}")
async def get_music_by_id_alias(track_id: str):
    # /tracks/{track_id} へのリダイレクト
    pass

@v1_router.post("/music")
async def upload_music_alias():
    # /tracks へのプロキシ
    pass
""")
    
    print("\n2️⃣ フロントエンドのエンドポイント変更:")
    print("""
# src/services/track.js を修正
export const getNewReleases = async (limit = 8) => {
  // const response = await apiClient.get('/music', { params: { limit, sort: 'newest' } });
  const response = await apiClient.get('/tracks', { params: { limit, sort: 'newest' } });
  return response.data;
};
""")
    
    print("\n3️⃣ 即座にテストできるエンドポイント:")
    print("✅ GET /api/v1/test - APIテスト")
    print("✅ GET /api/v1/debug - デバッグ情報") 
    print("✅ GET /health - ヘルスチェック")
    print("✅ GET / - ルートエンドポイント")
    print("✅ GET /docs - API ドキュメント")
    
    print("\n🚀 今すぐできるテスト:")
    print("1. バックエンドサーバーを起動")
    print("2. http://localhost:8001/api/v1/test にアクセス")
    print("3. http://localhost:8001/api/v1/debug で利用可能なルートを確認")
    print("4. http://localhost:8001/docs でAPI仕様を確認")

def generate_quick_fix():
    """クイックフィックス用のルーター追加コード生成"""
    
    print("\n" + "="*60)
    print("🛠️ クイックフィックス: バックエンドエイリアス追加")
    print("="*60)
    
    quick_fix_code = '''
# app/api/router.py の v1_router に以下を追加:

# フロントエンド互換性のためのエイリアスルート
@v1_router.get("/music")
async def get_music_compatibility():
    """楽曲一覧取得 (フロントエンド互換性)"""
    try:
        from app.api.v1.tracks import get_tracks
        return await get_tracks()
    except:
        return {
            "data": [
                {
                    "id": "track1",
                    "title": "サンプル楽曲1",
                    "artistName": "テストアーティスト",
                    "artistId": "artist1", 
                    "genre": "ポップ",
                    "price": 300,
                    "duration": 180,
                    "coverArtUrl": null
                }
            ],
            "total": 1
        }

@v1_router.get("/artists/featured") 
async def get_featured_artists_compatibility():
    """おすすめアーティスト取得 (フロントエンド互換性)"""
    return {
        "data": [
            {
                "id": "artist1",
                "displayName": "テストアーティスト",
                "profileImage": null,
                "genre": "多ジャンル"
            }
        ],
        "total": 1
    }
'''
    
    print(quick_fix_code)
    
    return quick_fix_code

if __name__ == "__main__":
    check_api_compatibility()
    generate_quick_fix()
    
    print("\n🎯 次のステップ:")
    print("1. 上記のクイックフィックスをバックエンドに適用")
    print("2. または、フロントエンドのエンドポイントを修正")
    print("3. 両サーバーを起動して統合テスト実行")
