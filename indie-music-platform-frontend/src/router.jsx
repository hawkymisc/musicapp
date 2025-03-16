import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { PlayerProvider } from './contexts/PlayerContext';

// 認証関連
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';

// 共通ページ
import Home from './pages/common/Home';
import Search from './pages/common/Search';
import TrackDetail from './pages/common/TrackDetail';
import ArtistProfile from './pages/common/ArtistProfile';

// リスナー向けページ
import Library from './pages/listener/Library';

// アーティスト向けページ
import ArtistDashboard from './pages/artist/ArtistDashboard';
import TrackUpload from './pages/artist/TrackUpload';
import TrackEdit from './pages/artist/TrackEdit';
import ArtistTracks from './pages/artist/ArtistTracks';

// 認証要求ルート
const ProtectedRoute = ({ children, requiredRole }) => {
  const isAuthenticated = localStorage.getItem('authToken') !== null;
  const userRole = localStorage.getItem('userRole');
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  if (requiredRole && userRole !== requiredRole) {
    return <Navigate to="/" />;
  }
  
  return children;
};

const AppRouter = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <PlayerProvider>
          <Routes>
            {/* 認証ルート */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            {/* 共通ページ */}
            <Route path="/" element={<Home />} />
            <Route path="/search" element={<Search />} />
            <Route path="/tracks/:trackId" element={<TrackDetail />} />
            <Route path="/artists/:artistId" element={<ArtistProfile />} />
            
            {/* リスナー向けページ */}
            <Route 
              path="/library" 
              element={
                <ProtectedRoute>
                  <Library />
                </ProtectedRoute>
              } 
            />
            
            {/* アーティスト向けページ */}
            <Route 
              path="/artist/dashboard" 
              element={
                <ProtectedRoute requiredRole="artist">
                  <ArtistDashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/artist/upload" 
              element={
                <ProtectedRoute requiredRole="artist">
                  <TrackUpload />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/artist/tracks" 
              element={
                <ProtectedRoute requiredRole="artist">
                  <ArtistTracks />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/artist/tracks/:trackId/edit" 
              element={
                <ProtectedRoute requiredRole="artist">
                  <TrackEdit />
                </ProtectedRoute>
              } 
            />
            
            {/* 404ページ */}
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </PlayerProvider>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default AppRouter;
