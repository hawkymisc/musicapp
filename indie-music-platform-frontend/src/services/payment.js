import api from './api';

/**
 * 決済関連のAPI呼び出しを行うサービス
 */
const paymentService = {
  /**
   * 楽曲購入のための決済処理
   * @param {string} userId - ユーザーID
   * @param {string} trackId - 購入する楽曲ID
   * @returns {Promise} 購入結果（セッションID等）
   */
  purchaseTrack: async (userId, trackId) => {
    try {
      const response = await api.post('/purchases', { userId, trackId });
      return response.data;
    } catch (error) {
      console.error('Track purchase error:', error);
      throw error;
    }
  },

  /**
   * 楽曲の購入状態をチェック
   * @param {string} userId - ユーザーID
   * @param {string} trackId - 楽曲ID
   * @returns {Promise<boolean>} 購入済みかどうか
   */
  checkPurchaseStatus: async (userId, trackId) => {
    try {
      const response = await api.get(`/purchases/check`, { 
        params: { userId, trackId } 
      });
      return response.data.purchased;
    } catch (error) {
      console.error('Check purchase status error:', error);
      throw error;
    }
  },

  // 既存の他の関数はそのまま...

  /**
   * ユーザーの購入履歴を取得
   * @param {string} userId - ユーザーID
   * @returns {Promise} 購入履歴
   */
  getPurchaseHistory: async (userId) => {
    try {
      const response = await api.get(`/payments/users/${userId}/history`);
      return response.data;
    } catch (error) {
      console.error('Get purchase history error:', error);
      throw error;
    }
  },

  /**
   * アーティストの収益情報を取得
   * @param {string} artistId - アーティストID
   * @returns {Promise} 収益情報
   */
  getArtistEarnings: async (artistId) => {
    try {
      const response = await api.get(`/payments/artists/${artistId}/earnings`);
      return response.data;
    } catch (error) {
      console.error('Get artist earnings error:', error);
      throw error;
    }
  },

  /**
   * 支払い方法を追加
   * @param {string} userId - ユーザーID
   * @param {Object} paymentMethod - 支払い方法情報
   * @returns {Promise} 追加結果
   */
  addPaymentMethod: async (userId, paymentMethod) => {
    try {
      const response = await api.post(`/payments/users/${userId}/methods`, paymentMethod);
      return response.data;
    } catch (error) {
      console.error('Add payment method error:', error);
      throw error;
    }
  },

  /**
   * 支払い方法一覧を取得
   * @param {string} userId - ユーザーID
   * @returns {Promise} 支払い方法一覧
   */
  getPaymentMethods: async (userId) => {
    try {
      const response = await api.get(`/payments/users/${userId}/methods`);
      return response.data;
    } catch (error) {
      console.error('Get payment methods error:', error);
      throw error;
    }
  },

  /**
   * アーティストへの支払い設定を更新
   * @param {string} artistId - アーティストID
   * @param {Object} payoutSettings - 支払い設定
   * @returns {Promise} 更新結果
   */
  updatePayoutSettings: async (artistId, payoutSettings) => {
    try {
      const response = await api.put(`/payments/artists/${artistId}/payout-settings`, payoutSettings);
      return response.data;
    } catch (error) {
      console.error('Update payout settings error:', error);
      throw error;
    }
  },
};

export default paymentService;