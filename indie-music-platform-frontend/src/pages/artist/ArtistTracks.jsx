import React from 'react';
import { useNavigate } from 'react-router-dom';

const ArtistTracks = () => {
  const navigate = useNavigate();

  return (
    <div style={{ padding: '2rem' }}>
      <h1>楽曲管理</h1>
      <p>アップロードした楽曲の一覧を表示します。</p>
      <p>この機能は現在開発中です。</p>
      <button onClick={() => navigate('/artist/dashboard')}>
        ダッシュボードに戻る
      </button>
    </div>
  );
};

export default ArtistTracks;
