// src/services/api.js
import axios from 'axios';
import logger from '../utils/logger';

// APIクライアントのベース設定
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',  // 環境変数から取得
  headers: {
    'Content-Type': 'application/json'
  }
});

// リクエストインターセプター - 認証トークンの追加とログ
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    // API リクエストのログ
    logger.debug(`API Request: ${config.method?.toUpperCase()} ${config.url}`, {
      params: config.params,
      headers: config.headers
    });
    
    return config;
  },
  error => {
    logger.error('API Request Error', error);
    return Promise.reject(error);
  }
);

// レスポンスインターセプター - エラーハンドリングとログ
apiClient.interceptors.response.use(
  response => {
    // 成功レスポンスのログ
    logger.debug(`API Response: ${response.status} ${response.config.url}`, {
      status: response.status,
      data: response.data
    });
    return response;
  },
  error => {
    const { response, config } = error;
    
    // API エラーのログ
    logger.apiError(
      config?.url || 'unknown',
      response?.status || 'network_error',
      error,
      {
        data: response?.data,
        config: {
          method: config?.method,
          params: config?.params
        }
      }
    );
    
    // 401エラー（認証エラー）の場合はログイン画面にリダイレクト
    if (response && response.status === 401) {
      logger.warn('Authentication failed, redirecting to login');
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    
    // 403エラー（認可エラー）
    if (response && response.status === 403) {
      logger.warn('Access forbidden');
    }
    
    // 500エラー（サーバーエラー）
    if (response && response.status >= 500) {
      logger.error('Server error occurred');
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
