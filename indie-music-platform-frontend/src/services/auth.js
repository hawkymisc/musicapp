import api from './api';

// モック認証フラグ
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

/**
 * 認証関連のAPI呼び出しを行うサービス
 */
const authService = {
  /**
   * ユーザーログイン
   * @param {string} email - ユーザーメールアドレス
   * @param {string} password - パスワード
   * @returns {Promise} ログイン結果
   */
  login: async (email, password) => {
    if (USE_MOCK) {
      // モック認証 - デモ用
      await new Promise(resolve => setTimeout(resolve, 1000)); // 1秒遅延でリアルっぽく
      return {
        user: {
          id: 'mock-user-id',
          email: email,
          display_name: 'テストユーザー',
          user_role: 'listener',
          is_verified: true
        },
        token: 'mock-jwt-token'
      };
    }
    
    try {
      const response = await api.post('/auth/login', { email, password });
      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  /**
   * ユーザー登録
   * @param {Object} userData - ユーザー登録データ
   * @returns {Promise} 登録結果
   */
  register: async (userData) => {
    try {
      const response = await api.post('/auth/register', userData);
      return response.data;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  },

  /**
   * ログアウト処理
   * @returns {Promise} ログアウト結果
   */
  logout: async () => {
    try {
      const response = await api.post('/auth/logout');
      return response.data;
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  },

  /**
   * 現在のユーザー情報を取得
   * @returns {Promise} ユーザー情報
   */
  getCurrentUser: async () => {
    if (USE_MOCK) {
      const token = localStorage.getItem('authToken');
      if (token === 'mock-jwt-token') {
        return {
          id: 'mock-user-id',
          email: 'test@example.com',
          display_name: 'テストユーザー',
          user_role: 'listener',
          is_verified: true
        };
      }
      return null;
    }
    
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      console.error('Get current user error:', error);
      return null;
    }
  },

  /**
   * パスワードリセットリクエスト
   * @param {string} email - ユーザーメールアドレス
   * @returns {Promise} リクエスト結果
   */
  requestPasswordReset: async (email) => {
    try {
      const response = await api.post('/auth/reset-password-request', { email });
      return response.data;
    } catch (error) {
      console.error('Password reset request error:', error);
      throw error;
    }
  },

  /**
   * パスワードリセット
   * @param {string} token - リセットトークン
   * @param {string} newPassword - 新しいパスワード
   * @returns {Promise} リセット結果
   */
  resetPassword: async (token, newPassword) => {
    try {
      const response = await api.post('/auth/reset-password', { token, newPassword });
      return response.data;
    } catch (error) {
      console.error('Password reset error:', error);
      throw error;
    }
  },
};

export default authService;