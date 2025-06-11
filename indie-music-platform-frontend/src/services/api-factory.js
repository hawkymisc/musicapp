// src/services/api-factory.js
/**
 * API切り替え用ファクトリー
 * 
 * このファイルは、モックAPIと実際のAPIを環境変数に基づいて切り替えるための
 * ファクトリー関数を提供します。開発中はモックAPIを使用し、
 * バックエンドが整備されたら実際のAPIに切り替えることができます。
 */

import { mockApi } from '../mockApi';
import authService from './auth';
import userService from './user';
import trackService from './track';
import artistService from './artist';
import paymentService from './payment';

// 環境変数でモックAPIを使用するかどうかを決定
// VITE_USE_MOCK=true の場合はモックを使用
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

/**
 * Auth関連APIの取得
 * @returns {Object} 認証関連のAPI
 */
export const getAuthService = () => {
  console.log(`Using ${USE_MOCK ? 'mock' : 'real'} auth service`);
  return USE_MOCK ? mockApi : authService;
};

/**
 * User関連APIの取得
 * @returns {Object} ユーザー関連のAPI
 */
export const getUserService = () => {
  return USE_MOCK ? mockApi : userService;
};

/**
 * Track関連APIの取得
 * @returns {Object} 楽曲関連のAPI
 */
export const getTrackService = () => {
  return USE_MOCK ? mockApi : trackService;
};

/**
 * Artist関連APIの取得
 * @returns {Object} アーティスト関連のAPI
 */
export const getArtistService = () => {
  return USE_MOCK ? mockApi : artistService;
};

/**
 * Payment関連APIの取得
 * @returns {Object} 決済関連のAPI
 */
export const getPaymentService = () => {
  return USE_MOCK ? mockApi : paymentService;
};

/**
 * モックAPIと実APIの両方をサポートするラッパー関数
 * 実APIでエラーが発生した場合、モックAPIにフォールバック
 * @param {Function} realApiFunc - 実APIの関数
 * @param {Function} mockApiFunc - モックAPIの同等関数
 * @param {Array} args - API関数に渡す引数
 * @returns {Promise} API呼び出し結果
 */
export const withFallback = async (realApiFunc, mockApiFunc, ...args) => {
  if (USE_MOCK) {
    return mockApiFunc(...args);
  }
  
  try {
    return await realApiFunc(...args);
  } catch (error) {
    console.warn('実APIの呼び出しに失敗したためモックにフォールバックします', error);
    return mockApiFunc(...args);
  }
};
