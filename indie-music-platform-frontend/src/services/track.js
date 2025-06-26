import apiClient from './api';
import paymentService from './payment';

// API レスポンスキャッシュ用のマップ
const cache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5分間キャッシュ

const getCacheKey = (endpoint, params) => {
  return `${endpoint}?${new URLSearchParams(params).toString()}`;
};

const getCachedData = (key) => {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }
  cache.delete(key);
  return null;
};

const setCachedData = (key, data) => {
  cache.set(key, {
    data,
    timestamp: Date.now()
  });
};

// 新着楽曲を取得
export const getNewReleases = async (limit = 8) => {
  const params = { limit, sort_by: 'created_at', sort_desc: true };
  const cacheKey = getCacheKey('/api/v1/tracks/', params);
  
  const cachedData = getCachedData(cacheKey);
  if (cachedData) {
    return cachedData;
  }
  
  const response = await apiClient.get('/api/v1/tracks/', { params });
  const data = response.data || [];
  setCachedData(cacheKey, data);
  return data;
};

// おすすめアーティストを取得
export const getFeaturedArtists = async (limit = 5) => {
  const params = { limit };
  const cacheKey = getCacheKey('/artists/featured', params);
  
  const cachedData = getCachedData(cacheKey);
  if (cachedData) {
    return cachedData;
  }
  
  const response = await apiClient.get('/artists/featured', { params });
  const data = response.data.data || [];
  setCachedData(cacheKey, data);
  return data;
};

// 楽曲詳細を取得
export const getTrackById = async (trackId) => {
  const response = await apiClient.get(`/api/v1/tracks/${trackId}`);
  return response.data;
};

// 楽曲検索
export const searchTracks = async (params) => {
  const searchParams = {
    search: params.query || '',
    genre: params.genre || '',
    sort_by: params.sort_by || 'created_at',
    sort_desc: params.sort_desc !== false
  };
  
  const response = await apiClient.get('/api/v1/tracks/', { params: searchParams });
  return response.data;
};

// 楽曲のアップロード
export const uploadTrack = async (formData) => {
  const response = await apiClient.post('/music', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  return response.data.id;
};

// 楽曲購入（payment.jsを呼び出す）
export const purchaseTrack = paymentService.purchaseTrack;

// 購入済みかチェック（payment.jsを呼び出す）
export const checkPurchaseStatus = paymentService.checkPurchaseStatus;

// 再生カウント記録
export const recordPlay = async (trackId) => {
  await apiClient.post(`/music/${trackId}/play`);
};