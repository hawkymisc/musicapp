import React, { useState, useEffect, useContext } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { FaPlay, FaPause, FaShoppingCart, FaDownload, FaUser, FaMusic } from 'react-icons/fa';
import { AuthContext } from '../../contexts/AuthContext';
import { PlayerContext } from '../../contexts/PlayerContext';
import { getTrackById, purchaseTrack, checkPurchaseStatus } from '../../services/track';
import { loadStripe } from '@stripe/stripe-js';
import Header from '../layout/Header';
import Player from '../player/Player';

// Stripeの初期化（実際の使用時は環境変数から読み込むこと）
const stripePromise = loadStripe('pk_test_YOUR_PUBLISHABLE_KEY');

const Container = styled.div`
  padding: 0 0 70px 0; // プレーヤーの高さ分の下部パディング
`;

const Content = styled.div`
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
`;

const TrackHeader = styled.div`
  display: flex;
  margin-bottom: 2rem;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const CoverArt = styled.div`
  width: 300px;
  height: 300px;
  background-color: #868e96;
  margin-right: 2rem;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  overflow: hidden;
  
  @media (max-width: 768px) {
    width: 100%;
    margin-right: 0;
    margin-bottom: 1.5rem;
  }
`;

const CoverImage = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
`;

const PlayButton = styled.button`
  position: absolute;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.6);
  border: none;
  color: white;
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s;
  
  &:hover {
    transform: scale(1.1);
  }
  
  &:focus {
    outline: none;
  }
`;

const TrackInfo = styled.div`
  flex: 1;
`;

const TrackTitle = styled.h1`
  margin-bottom: 0.5rem;
  color: #212529;
`;

const ArtistName = styled(Link)`
  display: block;
  color: #6c757d;
  text-decoration: none;
  font-size: 1.25rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  
  svg {
    margin-right: 0.5rem;
  }
  
  &:hover {
    color: #007bff;
  }
`;

const TrackMeta = styled.div`
  margin-bottom: 1.5rem;
  color: #6c757d;
  font-size: 0.9rem;
  
  span {
    margin-right: 1rem;
  }
`;

const TrackPrice = styled.div`
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  font-weight: bold;
  color: #212529;
`;

const ButtonGroup = styled.div`
  display: flex;
  margin-bottom: 1.5rem;
  
  @media (max-width: 576px) {
    flex-direction: column;
  }
`;

const Button = styled.button`
  background-color: ${props => props.primary ? '#28a745' : '#6c757d'};
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  margin-right: 1rem;
  
  svg {
    margin-right: 0.5rem;
  }
  
  &:hover {
    background-color: ${props => props.primary ? '#218838' : '#5a6268'};
  }
  
  &:disabled {
    background-color: #6c757d;
    opacity: 0.65;
    cursor: not-allowed;
  }
  
  @media (max-width: 576px) {
    margin-right: 0;
    margin-bottom: 0.5rem;
  }
`;

const DescriptionSection = styled.div`
  margin-bottom: 2rem;
`;

const DescriptionTitle = styled.h2`
  margin-bottom: 1rem;
  color: #343a40;
  font-size: 1.25rem;
`;

const Description = styled.p`
  color: #212529;
  line-height: 1.6;
`;

const Loading = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: #6c757d;
  font-size: 1.25rem;
`;

const TrackDetail = () => {
  const { trackId } = useParams();
  const [track, setTrack] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPurchased, setIsPurchased] = useState(false);
  const [purchaseLoading, setPurchaseLoading] = useState(false);
  
  const { user } = useContext(AuthContext);
  const { currentTrack, setCurrentTrack } = useContext(PlayerContext);
  const navigate = useNavigate();
  
  useEffect(() => {
    const fetchTrack = async () => {
      try {
        const trackData = await getTrackById(trackId);
        setTrack(trackData);
        
        // ログイン中かつ購入済みか確認
        if (user) {
          const purchased = await checkPurchaseStatus(user.uid, trackId);
          setIsPurchased(purchased);
        }
      } catch (error) {
        console.error('Error fetching track:', error);
        setError('楽曲の取得に失敗しました。');
      } finally {
        setLoading(false);
      }
    };
    
    fetchTrack();
  }, [trackId, user]);
  
  // 現在のトラックとの一致を確認して再生状態を更新
  useEffect(() => {
    if (currentTrack && currentTrack.id === trackId) {
      setIsPlaying(true);
    } else {
      setIsPlaying(false);
    }
  }, [currentTrack, trackId]);
  
  const handlePlayToggle = () => {
    if (isPlaying) {
      // すでに再生中なら何もしない（プレーヤーで制御）
    } else {
      // 再生開始
      setCurrentTrack(track);
      setIsPlaying(true);
    }
  };
  
  const handlePurchase = async () => {
    if (!user) {
      navigate('/login', { state: { returnUrl: `/tracks/${trackId}` } });
      return;
    }
    
    try {
      setPurchaseLoading(true);
      
      // StripeのチェックアウトセッションIDを取得
      const { sessionId } = await purchaseTrack(user.uid, trackId);
      
      // Stripeのチェックアウトに遷移
      const stripe = await stripePromise;
      const { error } = await stripe.redirectToCheckout({ sessionId });
      
      if (error) {
        console.error('Error redirecting to checkout:', error);
        setError('決済画面への遷移に失敗しました。後ほど再度お試しください。');
      }
    } catch (error) {
      console.error('Purchase error:', error);
      setError('購入処理に失敗しました。後ほど再度お試しください。');
    } finally {
      setPurchaseLoading(false);
    }
  };
  
  const handleDownload = async () => {
    // ダウンロード処理
    // MVPフェーズでは簡易的な実装
    window.open(`/api/v1/downloads/${trackId}`, '_blank');
  };
  
  if (loading) {
    return (
      <Container>
        <Header />
        <Content>
          <Loading>読み込み中...</Loading>
        </Content>
      </Container>
    );
  }
  
  if (error || !track) {
    return (
      <Container>
        <Header />
        <Content>
          <div>エラーが発生しました。{error}</div>
          <Link to="/">ホームに戻る</Link>
        </Content>
      </Container>
    );
  }
  
  return (
    <Container>
      <Header />
      
      <Content>
        <TrackHeader>
          <CoverArt>
            {track.coverArtUrl ? (
              <CoverImage src={track.coverArtUrl} alt={track.title} />
            ) : (
              <FaMusic style={{ fontSize: '4rem', color: 'white' }} />
            )}
            <PlayButton onClick={handlePlayToggle}>
              {isPlaying ? <FaPause /> : <FaPlay />}
            </PlayButton>
          </CoverArt>
          
          <TrackInfo>
            <TrackTitle>{track.title}</TrackTitle>
            <ArtistName to={`/artists/${track.artistId}`}>
              <FaUser />
              {track.artistName}
            </ArtistName>
            
            <TrackMeta>
              <span>ジャンル: {track.genre}</span>
              <span>リリース日: {new Date(track.releaseDate).toLocaleDateString('ja-JP')}</span>
              <span>再生回数: {track.playCount}</span>
            </TrackMeta>
            
            <TrackPrice>¥{track.price.toLocaleString()}</TrackPrice>
            
            <ButtonGroup>
              {isPurchased ? (
                <Button onClick={handleDownload}>
                  <FaDownload />
                  ダウンロード
                </Button>
              ) : (
                <Button primary onClick={handlePurchase} disabled={purchaseLoading}>
                  <FaShoppingCart />
                  {purchaseLoading ? '処理中...' : '購入する'}
                </Button>
              )}
              <Button onClick={handlePlayToggle}>
                {isPlaying ? <FaPause /> : <FaPlay />}
                {isPlaying ? '一時停止' : '再生'}
              </Button>
            </ButtonGroup>
          </TrackInfo>
        </TrackHeader>
        
        <DescriptionSection>
          <DescriptionTitle>楽曲について</DescriptionTitle>
          <Description>
            {track.description || 'この楽曲に説明はありません。'}
          </Description>
        </DescriptionSection>
      </Content>
      
      <Player />
    </Container>
  );
};

export default TrackDetail;
