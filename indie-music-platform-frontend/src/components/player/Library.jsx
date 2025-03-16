import React, { useState, useEffect, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { FaPlay, FaDownload, FaMusic, FaHeart, FaRegHeart } from 'react-icons/fa';
import { AuthContext } from '../../contexts/AuthContext';
import { PlayerContext } from '../../contexts/PlayerContext';
import { getPurchasedTracks, toggleFavorite } from '../../services/user';
import Header from '../layout/Header';
import Player from './Player';

const Container = styled.div`
  padding: 0 0 70px 0; // プレーヤーの高さ分の下部パディング
`;

const Content = styled.div`
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
`;

const PageTitle = styled.h1`
  margin-bottom: 1.5rem;
  color: #343a40;
`;

const TabsContainer = styled.div`
  display: flex;
  margin-bottom: 2rem;
  border-bottom: 1px solid #dee2e6;
`;

const Tab = styled.button`
  padding: 0.75rem 1.5rem;
  background-color: transparent;
  border: none;
  color: ${props => props.active ? '#007bff' : '#6c757d'};
  font-size: 1rem;
  font-weight: ${props => props.active ? 'bold' : 'normal'};
  cursor: pointer;
  border-bottom: ${props => props.active ? '2px solid #007bff' : 'none'};
  
  &:hover {
    color: ${props => props.active ? '#007bff' : '#343a40'};
  }
  
  &:focus {
    outline: none;
  }
`;

const TracksGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.5rem;
`;

const TrackCard = styled.div`
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-5px);
  }
`;

const TrackCover = styled.div`
  width: 100%;
  aspect-ratio: 1;
  background-color: #868e96;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
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
  
  ${TrackCover}:hover & {
    opacity: 1;
  }
`;

const PlayButton = styled.div`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #212529;
  font-size: 1.2rem;
`;

const TrackDetails = styled.div`
  padding: 1rem;
`;

const TrackTitle = styled(Link)`
  display: block;
  color: #212529;
  font-weight: 600;
  margin-bottom: 0.5rem;
  text-decoration: none;
  
  &:hover {
    color: #007bff;
  }
`;

const ArtistName = styled(Link)`
  color: #6c757d;
  text-decoration: none;
  
  &:hover {
    color: #007bff;
    text-decoration: underline;
  }
`;

const TrackActions = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.75rem;
`;

const DownloadButton = styled.button`
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.3rem 0.6rem;
  font-size: 0.8rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  
  svg {
    margin-right: 0.3rem;
  }
  
  &:hover {
    background-color: #5a6268;
  }
`;

const FavoriteButton = styled.button`
  background: none;
  border: none;
  color: ${props => props.isFavorite ? '#dc3545' : '#6c757d'};
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    color: ${props => props.isFavorite ? '#c82333' : '#343a40'};
  }
  
  &:focus {
    outline: none;
  }
`;

const EmptyMessage = styled.div`
  text-align: center;
  padding: 2rem;
  color: #6c757d;
`;

const Library = () => {
  const [activeTab, setActiveTab] = useState('purchased');
  const [purchasedTracks, setPurchasedTracks] = useState([]);
  const [favoriteTracks, setFavoriteTracks] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const { user } = useContext(AuthContext);
  const { setCurrentTrack, setPlaylist } = useContext(PlayerContext);
  const navigate = useNavigate();
  
  // ユーザーがログインしていない場合はログイン画面にリダイレクト
  useEffect(() => {
    if (!user) {
      navigate('/login', { state: { returnUrl: '/library' } });
    }
  }, [user, navigate]);
  
  // 購入済み楽曲を取得
  useEffect(() => {
    const fetchPurchasedTracks = async () => {
      if (!user) return;
      
      try {
        setLoading(true);
        const tracksData = await getPurchasedTracks(user.uid);
        
        // 購入済み楽曲とお気に入り楽曲を分類
        const purchased = [];
        const favorites = [];
        
        tracksData.forEach(track => {
          purchased.push(track);
          if (track.isFavorite) {
            favorites.push(track);
          }
        });
        
        setPurchasedTracks(purchased);
        setFavoriteTracks(favorites);
      } catch (error) {
        console.error('Error fetching purchased tracks:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchPurchasedTracks();
  }, [user]);
  
  const handlePlayTrack = (track) => {
    const playlist = activeTab === 'favorites' ? favoriteTracks : purchasedTracks;
    setCurrentTrack(track);
    setPlaylist(playlist);
  };
  
  const handleDownload = (trackId) => {
    // ダウンロード処理
    window.open(`/api/v1/downloads/${trackId}`, '_blank');
  };
  
  const handleToggleFavorite = async (trackId, isFavorite) => {
    try {
      await toggleFavorite(user.uid, trackId, !isFavorite);
      
      // お気に入り状態の更新
      const updateTracksFavoriteStatus = (tracks) => {
        return tracks.map(track => {
          if (track.id === trackId) {
            return { ...track, isFavorite: !isFavorite };
          }
          return track;
        });
      };
      
      setPurchasedTracks(updateTracksFavoriteStatus(purchasedTracks));
      
      // お気に入りタブの内容も更新
      if (isFavorite) {
        // お気に入りから削除
        setFavoriteTracks(favoriteTracks.filter(track => track.id !== trackId));
      } else {
        // お気に入りに追加
        const trackToAdd = purchasedTracks.find(track => track.id === trackId);
        if (trackToAdd) {
          setFavoriteTracks([...favoriteTracks, { ...trackToAdd, isFavorite: true }]);
        }
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };
  
  const renderTracks = () => {
    const tracks = activeTab === 'favorites' ? favoriteTracks : purchasedTracks;
    
    if (loading) {
      return <EmptyMessage>読み込み中...</EmptyMessage>;
    }
    
    if (tracks.length === 0) {
      return (
        <EmptyMessage>
          {activeTab === 'purchased' 
            ? '購入済みの楽曲はありません。'
            : 'お気に入りに追加した楽曲はありません。'
          }
        </EmptyMessage>
      );
    }
    
    return (
      <TracksGrid>
        {tracks.map(track => (
          <TrackCard key={track.id}>
            <TrackCover onClick={() => handlePlayTrack(track)}>
              {track.coverArtUrl ? (
                <img src={track.coverArtUrl} alt={track.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              ) : (
                <FaMusic style={{ fontSize: '2rem', color: 'white' }} />
              )}
              <PlayOverlay>
                <PlayButton>
                  <FaPlay />
                </PlayButton>
              </PlayOverlay>
            </TrackCover>
            
            <TrackDetails>
              <TrackTitle to={`/tracks/${track.id}`}>{track.title}</TrackTitle>
              <ArtistName to={`/artists/${track.artistId}`}>{track.artistName}</ArtistName>
              <TrackActions>
                <DownloadButton onClick={() => handleDownload(track.id)}>
                  <FaDownload />
                  ダウンロード
                </DownloadButton>
                <FavoriteButton 
                  isFavorite={track.isFavorite}
                  onClick={() => handleToggleFavorite(track.id, track.isFavorite)}
                >
                  {track.isFavorite ? <FaHeart /> : <FaRegHeart />}
                </FavoriteButton>
              </TrackActions>
            </TrackDetails>
          </TrackCard>
        ))}
      </TracksGrid>
    );
  };
  
  return (
    <Container>
      <Header activePage="library" />
      
      <Content>
        <PageTitle>マイライブラリ</PageTitle>
        
        <TabsContainer>
          <Tab 
            active={activeTab === 'purchased'} 
            onClick={() => setActiveTab('purchased')}
          >
            購入した楽曲
          </Tab>
          <Tab 
            active={activeTab === 'favorites'} 
            onClick={() => setActiveTab('favorites')}
          >
            お気に入り
          </Tab>
        </TabsContainer>
        
        {renderTracks()}
      </Content>
      
      <Player />
    </Container>
  );
};

export default Library;
