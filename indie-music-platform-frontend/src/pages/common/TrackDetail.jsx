import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import styled from 'styled-components';
import { FaPlay, FaPause, FaDownload, FaShoppingCart } from 'react-icons/fa';
import { getTrackById } from '../../services/track';
import Header from '../../components/layout/Header';

const Container = styled.div`
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
`;

const TrackInfo = styled.div`
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const CoverArt = styled.div`
  width: 300px;
  height: 300px;
  background-color: #868e96;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 3rem;
  position: relative;
  cursor: pointer;
  
  @media (max-width: 768px) {
    width: 100%;
    max-width: 300px;
    margin: 0 auto;
  }
`;

const PlayOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  border-radius: 8px;
  
  ${CoverArt}:hover & {
    opacity: 1;
  }
`;

const PlayButton = styled.div`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #212529;
  font-size: 2rem;
`;

const Details = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const Title = styled.h1`
  color: #212529;
  margin: 0;
`;

const ArtistName = styled(Link)`
  color: #007bff;
  text-decoration: none;
  font-size: 1.2rem;
  font-weight: 500;
  
  &:hover {
    text-decoration: underline;
  }
`;

const MetaInfo = styled.div`
  display: flex;
  gap: 2rem;
  color: #6c757d;
`;

const Price = styled.div`
  font-size: 1.5rem;
  font-weight: bold;
  color: #28a745;
`;

const Description = styled.div`
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-top: 1rem;
`;

const Actions = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
`;

const ActionButton = styled.button`
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.2s;
`;

const PurchaseButton = styled(ActionButton)`
  background-color: #28a745;
  color: white;
  
  &:hover {
    background-color: #218838;
  }
`;

const PlayControlButton = styled(ActionButton)`
  background-color: #007bff;
  color: white;
  
  &:hover {
    background-color: #0056b3;
  }
`;

const LoadingMessage = styled.div`
  text-align: center;
  color: #6c757d;
  margin-top: 2rem;
`;

const ErrorMessage = styled.div`
  text-align: center;
  color: #dc3545;
  margin-top: 2rem;
`;

const TrackDetail = () => {
  const { trackId } = useParams();
  const [track, setTrack] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    const fetchTrack = async () => {
      try {
        setLoading(true);
        const trackData = await getTrackById(trackId);
        setTrack(trackData);
      } catch (error) {
        console.error('楽曲詳細取得エラー:', error);
        setError('楽曲情報の取得に失敗しました');
      } finally {
        setLoading(false);
      }
    };

    if (trackId) {
      fetchTrack();
    }
  }, [trackId]);

  const handlePlayToggle = () => {
    setIsPlaying(!isPlaying);
    // ここで実際の再生制御を実装
  };

  const handlePurchase = () => {
    // 購入処理を実装
    alert('購入機能は開発中です');
  };

  const formatDuration = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <>
        <Header />
        <Container>
          <LoadingMessage>楽曲情報を読み込み中...</LoadingMessage>
        </Container>
      </>
    );
  }

  if (error || !track) {
    return (
      <>
        <Header />
        <Container>
          <ErrorMessage>{error || '楽曲が見つかりませんでした'}</ErrorMessage>
        </Container>
      </>
    );
  }

  return (
    <>
      <Header />
      <Container>
        <TrackInfo>
          <CoverArt onClick={handlePlayToggle}>
            {track.coverArtUrl ? (
              <img 
                src={track.coverArtUrl} 
                alt={track.title}
                style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '8px' }}
              />
            ) : (
              <span>♪</span>
            )}
            <PlayOverlay>
              <PlayButton>
                {isPlaying ? <FaPause /> : <FaPlay />}
              </PlayButton>
            </PlayOverlay>
          </CoverArt>

          <Details>
            <Title>{track.title}</Title>
            <ArtistName to={`/artists/${track.artistId}`}>
              {track.artistName}
            </ArtistName>
            
            <MetaInfo>
              <span>ジャンル: {track.genre}</span>
              <span>再生時間: {formatDuration(track.duration)}</span>
            </MetaInfo>
            
            <Price>¥{track.price?.toLocaleString()}</Price>
            
            <Actions>
              <PlayControlButton onClick={handlePlayToggle}>
                {isPlaying ? <FaPause /> : <FaPlay />}
                {isPlaying ? '一時停止' : '再生'}
              </PlayControlButton>
              
              <PurchaseButton onClick={handlePurchase}>
                <FaShoppingCart />
                購入
              </PurchaseButton>
            </Actions>
          </Details>
        </TrackInfo>

        {track.description && (
          <Description>
            <h3>楽曲について</h3>
            <p>{track.description}</p>
          </Description>
        )}
      </Container>
    </>
  );
};

export default TrackDetail;
