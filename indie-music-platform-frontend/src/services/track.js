import apiClient from './api';
import paymentService from './payment';

// 新着楽曲を取得
export const getNewReleases = async (limit = 8) => {
  const response = await apiClient.get('/api/v1/tracks/', { params: { limit, sort_by: 'created_at', sort_desc: true } });
  return response.data || [];
};

// おすすめアーティストを取得
export const getFeaturedArtists = async (limit = 5) => {
  const response = await apiClient.get('/artists/featured', { params: { limit } });
  return response.data.data || [];
};

// 楽曲詳細を取得
export const getTrackById = async (trackId) => {
  const response = await apiClient.get(`/api/v1/tracks/${trackId}`);
  return response.data;
};

// 楽曲検索
export const searchTracks = async (params) => {
  const response = await apiClient.get('/api/v1/tracks/', { params });
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