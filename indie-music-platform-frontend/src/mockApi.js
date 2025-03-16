// src/mockApi.js
// MVPフェーズのフロントエンド開発で使用するモックAPIの実装例
// 実際の開発では、バックエンドAPIが準備できるまでの間、このようなモックを使用できます

// モックデータ
const mockUsers = [
  {
    id: 'user1',
    email: 'artist@example.com',
    displayName: '山田太郎',
    userType: 'artist',
    profileImage: '',
    createdAt: '2025-01-15T00:00:00.000Z',
    isVerified: true
  },
  {
    id: 'user2',
    email: 'listener@example.com',
    displayName: '鈴木花子',
    userType: 'listener',
    profileImage: '',
    createdAt: '2025-01-20T00:00:00.000Z',
    isVerified: true
  }
];

const mockTracks = [
  {
    id: 'track1',
    artistId: 'user1',
    artistName: '山田太郎',
    title: '夏の終わりに',
    description: '夏の終わりの切ない気持ちを表現した楽曲です。',
    genre: 'ポップス',
    coverArtUrl: '',
    audioFileUrl: 'https://example.com/audio/track1.mp3',
    duration: 210,
    price: 300,
    releaseDate: '2025-01-25T00:00:00.000Z',
    createdAt: '2025-01-25T00:00:00.000Z',
    updatedAt: '2025-01-25T00:00:00.000Z',
    isPublic: true,
    playCount: 120
  },
  {
    id: 'track2',
    artistId: 'user1',
    artistName: '山田太郎',
    title: '星空のセレナーデ',
    description: '星空の下で奏でるセレナーデをイメージした曲です。',
    genre: 'バラード',
    coverArtUrl: '',
    audioFileUrl: 'https://example.com/audio/track2.mp3',
    duration: 240,
    price: 300,
    releaseDate: '2025-02-05T00:00:00.000Z',
    createdAt: '2025-02-05T00:00:00.000Z',
    updatedAt: '2025-02-05T00:00:00.000Z',
    isPublic: true,
    playCount: 85
  },
  {
    id: 'track3',
    artistId: 'user1',
    artistName: '山田太郎',
    title: '雨の日の窓辺',
    description: '雨の日の静かな窓辺での時間を表現しています。',
    genre: 'ジャズ',
    coverArtUrl: '',
    audioFileUrl: 'https://example.com/audio/track3.mp3',
    duration: 180,
    price: 250,
    releaseDate: '2025-02-15T00:00:00.000Z',
    createdAt: '2025-02-15T00:00:00.000Z',
    updatedAt: '2025-02-15T00:00:00.000Z',
    isPublic: true,
    playCount: 62
  }
];

const mockPurchases = [
  {
    id: 'purchase1',
    userId: 'user2',
    trackId: 'track1',
    amount: 300,
    purchaseDate: '2025-02-10T00:00:00.000Z',
    paymentMethod: 'credit_card',
    transactionId: 'tx123'
  },
  {
    id: 'purchase2',
    userId: 'user2',
    trackId: 'track2',
    amount: 300,
    purchaseDate: '2025-02-20T00:00:00.000Z',
    paymentMethod: 'credit_card',
    transactionId: 'tx456'
  }
];

const mockFavorites = [
  {
    userId: 'user2',
    trackId: 'track1'
  }
];

// APIエンドポイントモック
export const mockApi = {
  // 認証関連
  login: async (email, password) => {
    const user = mockUsers.find(u => u.email === email);
    
    if (!user || password !== 'password') {
      throw new Error('Invalid credentials');
    }
    
    return {
      token: 'mock-jwt-token',
      user: { ...user, password: undefined }
    };
  },
  
  register: async (userData) => {
    const id = `user${mockUsers.length + 1}`;
    const newUser = {
      id,
      ...userData,
      createdAt: new Date().toISOString(),
      isVerified: false
    };
    
    mockUsers.push(newUser);
    
    return {
      token: 'mock-jwt-token',
      user: { ...newUser, password: undefined }
    };
  },
  
  // ユーザー関連
  getUserProfile: async (userId) => {
    const user = mockUsers.find(u => u.id === userId);
    
    if (!user) {
      throw new Error('User not found');
    }
    
    return { ...user, password: undefined };
  },
  
  // 楽曲関連
  getNewReleases: async (limit = 8) => {
    // 日付でソート
    return mockTracks
      .sort((a, b) => new Date(b.releaseDate) - new Date(a.releaseDate))
      .slice(0, limit);
  },
  
  getFeaturedArtists: async (limit = 5) => {
    // アーティストの情報を取得（重複を除去）
    const artistIds = [...new Set(mockTracks.map(track => track.artistId))];
    
    return artistIds
      .map(id => {
        const user = mockUsers.find(u => u.id === id && u.userType === 'artist');
        if (!user) return null;
        
        // 関連する楽曲数をカウント
        const trackCount = mockTracks.filter(t => t.artistId === id).length;
        
        return {
          id: user.id,
          displayName: user.displayName,
          profileImage: user.profileImage,
          trackCount
        };
      })
      .filter(artist => artist !== null)
      .slice(0, limit);
  },
  
  getTrackById: async (trackId) => {
    const track = mockTracks.find(t => t.id === trackId);
    
    if (!track) {
      throw new Error('Track not found');
    }
    
    return track;
  },
  
  searchTracks: async ({ query, genre, sort }) => {
    let results = [...mockTracks];
    
    // クエリでフィルタリング
    if (query) {
      const queryLower = query.toLowerCase();
      results = results.filter(track => 
        track.title.toLowerCase().includes(queryLower) ||
        track.artistName.toLowerCase().includes(queryLower)
      );
    }
    
    // ジャンルでフィルタリング
    if (genre) {
      results = results.filter(track => track.genre === genre);
    }
    
    // ソート
    switch (sort) {
      case 'newest':
        results.sort((a, b) => new Date(b.releaseDate) - new Date(a.releaseDate));
        break;
      case 'popular':
        results.sort((a, b) => b.playCount - a.playCount);
        break;
      case 'priceAsc':
        results.sort((a, b) => a.price - b.price);
        break;
      case 'priceDesc':
        results.sort((a, b) => b.price - a.price);
        break;
      default:
        // デフォルトは新着順
        results.sort((a, b) => new Date(b.releaseDate) - new Date(a.releaseDate));
    }
    
    return {
      tracks: results,
      total: results.length
    };
  },
  
  uploadTrack: async (formData) => {
    // 新しい楽曲IDを生成
    const id = `track${mockTracks.length + 1}`;
    
    // フォームデータから必要な情報を抽出
    const artistId = formData.get('artistId') || 'user1'; // デモ用に固定
    const artist = mockUsers.find(u => u.id === artistId);
    
    const newTrack = {
      id,
      artistId,
      artistName: artist?.displayName || 'Unknown Artist',
      title: formData.get('title') || 'Untitled',
      description: formData.get('description') || '',
      genre: formData.get('genre') || 'その他',
      coverArtUrl: '',
      audioFileUrl: 'https://example.com/audio/mock.mp3',
      duration: parseInt(formData.get('duration')) || 180,
      price: parseInt(formData.get('price')) || 300,
      releaseDate: new Date().toISOString(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      isPublic: formData.get('isPublic') === 'true',
      playCount: 0
    };
    
    mockTracks.push(newTrack);
    
    return { id };
  },
  
  // 購入関連
  purchaseTrack: async (userId, trackId) => {
    const user = mockUsers.find(u => u.id === userId);
    const track = mockTracks.find(t => t.id === trackId);
    
    if (!user || !track) {
      throw new Error('User or track not found');
    }
    
    // 購入IDを生成
    const id = `purchase${mockPurchases.length + 1}`;
    
    const newPurchase = {
      id,
      userId,
      trackId,
      amount: track.price,
      purchaseDate: new Date().toISOString(),
      paymentMethod: 'credit_card',
      transactionId: `tx${Math.floor(Math.random() * 1000)}`
    };
    
    mockPurchases.push(newPurchase);
    
    // 実際には決済サービスのセッションIDを返すが、モックでは簡易的な実装
    return { 
      sessionId: 'mock-session-id',
      success: true
    };
  },
  
  checkPurchaseStatus: async (userId, trackId) => {
    const isPurchased = mockPurchases.some(
      p => p.userId === userId && p.trackId === trackId
    );
    
    return { purchased: isPurchased };
  },
  
  // 購入済み楽曲関連
  getPurchasedTracks: async (userId) => {
    const purchases = mockPurchases.filter(p => p.userId === userId);
    
    return purchases.map(purchase => {
      const track = mockTracks.find(t => t.id === purchase.trackId);
      const isFavorite = mockFavorites.some(
        f => f.userId === userId && f.trackId === purchase.trackId
      );
      
      return {
        ...track,
        purchaseDate: purchase.purchaseDate,
        isFavorite
      };
    });
  },
  
  toggleFavorite: async (userId, trackId, isFavorite) => {
    const favoriteExists = mockFavorites.findIndex(
      f => f.userId === userId && f.trackId === trackId
    );
    
    if (isFavorite && favoriteExists === -1) {
      // お気に入りに追加
      mockFavorites.push({ userId, trackId });
    } else if (!isFavorite && favoriteExists !== -1) {
      // お気に入りから削除
      mockFavorites.splice(favoriteExists, 1);
    }
    
    return { success: true };
  },
  
  // アーティスト関連
  getArtistTracks: async (artistId) => {
    const tracks = mockTracks.filter(t => t.artistId === artistId);
    
    // 各楽曲の収益を計算（シンプルに再生回数 × 単価の一部としてモック）
    return tracks.map(track => ({
      ...track,
      revenue: Math.floor(track.playCount * track.price * 0.1)
    }));
  },
  
  getArtistStats: async (artistId) => {
    const tracks = mockTracks.filter(t => t.artistId === artistId);
    
    const totalPlays = tracks.reduce((sum, track) => sum + track.playCount, 0);
    const totalRevenue = tracks.reduce(
      (sum, track) => sum + Math.floor(track.playCount * track.price * 0.1),
      0
    );
    
    return {
      totalPlays,
      totalRevenue,
      trackCount: tracks.length,
      playsTrend: 12, // モック用の固定値
      revenueTrend: 23 // モック用の固定値
    };
  },
  
  recordPlay: async (trackId) => {
    const trackIndex = mockTracks.findIndex(t => t.id === trackId);
    
    if (trackIndex !== -1) {
      mockTracks[trackIndex].playCount += 1;
    }
    
    return { success: true };
  }
};

// モックAPIをインターセプトして使用する方法
export const setupMockApi = () => {
  // 実装例：Axiosのインターセプターを使用してモックAPIにリダイレクト
  // この関数は実際の開発環境で、バックエンドが準備できていない場合に使用できます
  console.log('Mock API has been initialized.');
};
