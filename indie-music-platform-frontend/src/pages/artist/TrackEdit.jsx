import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';

const TrackEdit = () => {
  const navigate = useNavigate();
  const { trackId } = useParams();

  return (
    <div style={{ padding: '2rem' }}>
      <h1>楽曲編集</h1>
      <p>楽曲ID: {trackId}</p>
      <p>この機能は現在開発中です。</p>
      <button onClick={() => navigate('/artist/dashboard')}>
        ダッシュボードに戻る
      </button>
    </div>
  );
};

export default TrackEdit;
