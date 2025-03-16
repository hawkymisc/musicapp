// src/services/artist.js
import apiClient from './api';

// アーティストの楽曲取得
export const getArtistTracks = async (artistId) => {
  const response = await apiClient.get(`/artists/${artistId}/music`);
  return response.data;
};

// アーティスト統計取得
export const getArtistStats = async (artistId) => {
  const response = await apiClient.get(`/artists/${artistId}/stats`);
  return response.data;
};

// アーティストプロフィール取得
export const getArtistProfile = async (artistId) => {
  const response = await apiClient.get(`/artists/${artistId}`);
  return response.data;
};