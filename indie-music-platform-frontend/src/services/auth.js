import api from './api';

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