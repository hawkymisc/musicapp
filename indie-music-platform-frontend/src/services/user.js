// src/services/user.js
import apiClient from './api';

// ユーザープロフィール取得
export const getUserProfile = async (userId) => {
  const response = await apiClient.get(`/users/${userId}`);
  return response.data;
};

// ユーザープロフィール作成
export const createUserProfile = async (userData) => {
  const response = await apiClient.post('/users', userData);
  return response.data;
};

// 購入済み楽曲取得
export const getPurchasedTracks = async (userId) => {
  const response = await apiClient.get(`/users/${userId}/purchases`);
  return response.data;
};

// お気に入りの切り替え
export const toggleFavorite = async (userId, trackId, isFavorite) => {
  const response = await apiClient.post(`/users/${userId}/favorites`, { trackId, isFavorite });
  return response.data;
};