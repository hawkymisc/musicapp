import React, { createContext, useState, useEffect } from 'react';
import authService from '../services/auth';
import { getUserProfile } from '../services/user';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // 初期化時に現在のユーザー情報を取得
  useEffect(() => {
    const initAuth = async () => {
      try {
        // ローカルストレージにトークンがあれば現在のユーザー情報を取得
        if (localStorage.getItem('authToken')) {
          const currentUser = await authService.getCurrentUser();
          if (currentUser) {
            setUser(currentUser);
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        // エラー時はトークンを削除
        localStorage.removeItem('authToken');
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const register = async (userData) => {
    try {
      const result = await authService.register(userData);
      
      // トークンをローカルストレージに保存
      localStorage.setItem('authToken', result.token);
      setUser(result.user);
      
      return result.user;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  };

  const login = async (email, password) => {
    try {
      const result = await authService.login(email, password);
      
      // トークンをローカルストレージに保存
      localStorage.setItem('authToken', result.token);
      setUser(result.user);
      
      return result.user;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
      // ローカルストレージからトークンを削除
      localStorage.removeItem('authToken');
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  };

  const value = {
    user,
    loading,
    register,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};