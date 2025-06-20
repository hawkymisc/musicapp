// src/services/api.js
import axios from 'axios';

// APIクライアントのベース設定
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',  // 環境変数から取得
  headers: {
    'Content-Type': 'application/json'
  }
});

// リクエストインターセプター - 認証トークンの追加
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// レスポンスインターセプター - エラーハンドリング
apiClient.interceptors.response.use(
  response => response,
  error => {
    // 401エラー（認証エラー）の場合はログイン画面にリダイレクト
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
