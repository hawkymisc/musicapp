import React, { useState, useEffect, useContext } from 'react';
import styled from 'styled-components';
import { FaPlay, FaDownload, FaHeart } from 'react-icons/fa';
import { AuthContext } from '../../contexts/AuthContext';
import Header from '../../components/layout/Header';

const Container = styled.div`
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
`;

const TabNavigation = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid #dee2e6;
`;

const Tab = styled.button`
  padding: 0.75rem 1.5rem;
  border: none;
  background: none;
  color: ${props => props.active ? '#007bff' : '#6c757d'};
  border-bottom: 2px solid ${props => props.active ? '#007bff' : 'transparent'};
  cursor: pointer;
  font-size: 1rem;
  
  &:hover {
    color: #007bff;
  }
`;

const SectionTitle = styled.h2`
  color: #212529;
  margin-bottom: 1.5rem;
`;

const TracksGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
`;

const TrackCard = styled.div`
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-2px);
  }
`;

const TrackCover = styled.div`
  width: 100%;
  aspect-ratio: 1;
  background-color: #868e96;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
  position: relative;
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

const TrackInfo = styled.div`
  padding: 1rem;
`;

const TrackTitle = styled.h4`
  margin: 0 0 0.5rem 0;
  color: #212529;
`;

const TrackArtist = styled.div`
  color: #6c757d;
  margin-bottom: 0.5rem;
`;

const TrackActions = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0.25rem;
  
  &:hover {
    color: #007bff;
  }
`;

const PlaylistsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
`;

const PlaylistCard = styled.div`
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  text-align: center;
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-2px);
  }
`;

const PlaylistIcon = styled.div`
  width: 80px;
  height: 80px;
  border-radius: 8px;
  background-color: #007bff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
  margin: 0 auto 1rem;
`;

const EmptyState = styled.div`
  text-align: center;
  color: #6c757d;
  margin-top: 3rem;
  
  h3 {
    margin-bottom: 1rem;
  }
`;

const Library = () => {
  const [activeTab, setActiveTab] = useState('purchased');
  const [purchasedTracks, setPurchasedTracks] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [playlists, setPlaylists] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const { user } = useContext(AuthContext);

  useEffect(() => {
    const fetchLibraryData = async () => {
      try {
        setLoading(true);
        
        // モックデータで設定 - 実際のAPIが実装されたら置き換える
        const mockPurchasedTracks = [
          {
            id: 'track1',
            title: '購入済み楽曲1',
            artistName: 'アーティスト1',
            genre: 'ポップ',
            duration: 180,
            purchaseDate: '2024-12-01',
            coverArtUrl: null
          },
          {
            id: 'track2',
            title: '購入済み楽曲2',
            artistName: 'アーティスト2',
            genre: 'ロック',
            duration: 200,
            purchaseDate: '2024-11-28',
            coverArtUrl: null
          }
        ];
        
        const mockFavorites = [
          {
            id: 'track3',
            title: 'お気に入り楽曲1',
            artistName: 'アーティスト3',
            genre: 'ジャズ',
            duration: 220,
            coverArtUrl: null
          }
        ];
        
        const mockPlaylists = [
          {
            id: 'playlist1',
            name: 'お気に入りミックス',
            trackCount: 15,
            createdDate: '2024-11-15'
          },
          {
            id: 'playlist2',
            name: 'ドライブ用BGM',
            trackCount: 8,
            createdDate: '2024-12-05'
          }
        ];
        
        setPurchasedTracks(mockPurchasedTracks);
        setFavorites(mockFavorites);
        setPlaylists(mockPlaylists);
      } catch (error) {
        console.error('ライブラリデータ取得エラー:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchLibraryData();
  }, []);

  const handlePlayTrack = (track) => {
    // 再生機能を実装
    console.log('Playing track:', track.title);
  };

  const handleDownloadTrack = (track) => {
    // ダウンロード機能を実装
    console.log('Downloading track:', track.title);
  };

  const formatDuration = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const renderPurchasedTracks = () => (
    <>
      <SectionTitle>購入済み楽曲</SectionTitle>
      {purchasedTracks.length > 0 ? (
        <TracksGrid>
          {purchasedTracks.map(track => (
            <TrackCard key={track.id}>
              <TrackCover onClick={() => handlePlayTrack(track)}>
                {track.coverArtUrl ? (
                  <img 
                    src={track.coverArtUrl} 
                    alt={track.title}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                ) : (
                  <span>♪</span>
                )}
                <PlayOverlay>
                  <PlayButton>
                    <FaPlay />
                  </PlayButton>
                </PlayOverlay>
              </TrackCover>
              
              <TrackInfo>
                <TrackTitle>{track.title}</TrackTitle>
                <TrackArtist>{track.artistName}</TrackArtist>
                <div style={{ fontSize: '0.9rem', color: '#6c757d' }}>
                  {track.genre} • {formatDuration(track.duration)}
                </div>
                
                <TrackActions>
                  <ActionButton onClick={() => handlePlayTrack(track)}>
                    <FaPlay />
                  </ActionButton>
                  <ActionButton onClick={() => handleDownloadTrack(track)}>
                    <FaDownload />
                  </ActionButton>
                </TrackActions>
              </TrackInfo>
            </TrackCard>
          ))}
        </TracksGrid>
      ) : (
        <EmptyState>
          <h3>購入済み楽曲がありません</h3>
          <p>楽曲を購入すると、ここに表示されます。</p>
        </EmptyState>
      )}
    </>
  );

  const renderFavorites = () => (
    <>
      <SectionTitle>お気に入り</SectionTitle>
      {favorites.length > 0 ? (
        <TracksGrid>
          {favorites.map(track => (
            <TrackCard key={track.id}>
              <TrackCover onClick={() => handlePlayTrack(track)}>
                {track.coverArtUrl ? (
                  <img 
                    src={track.coverArtUrl} 
                    alt={track.title}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                ) : (
                  <span>♪</span>
                )}
                <PlayOverlay>
                  <PlayButton>
                    <FaPlay />
                  </PlayButton>
                </PlayOverlay>
              </TrackCover>
              
              <TrackInfo>
                <TrackTitle>{track.title}</TrackTitle>
                <TrackArtist>{track.artistName}</TrackArtist>
                <div style={{ fontSize: '0.9rem', color: '#6c757d' }}>
                  {track.genre} • {formatDuration(track.duration)}
                </div>
                
                <TrackActions>
                  <ActionButton onClick={() => handlePlayTrack(track)}>
                    <FaPlay />
                  </ActionButton>
                  <ActionButton>
                    <FaHeart />
                  </ActionButton>
                </TrackActions>
              </TrackInfo>
            </TrackCard>
          ))}
        </TracksGrid>
      ) : (
        <EmptyState>
          <h3>お気に入りがありません</h3>
          <p>楽曲をお気に入りに追加すると、ここに表示されます。</p>
        </EmptyState>
      )}
    </>
  );

  const renderPlaylists = () => (
    <>
      <SectionTitle>プレイリスト</SectionTitle>
      {playlists.length > 0 ? (
        <PlaylistsGrid>
          {playlists.map(playlist => (
            <PlaylistCard key={playlist.id}>
              <PlaylistIcon>
                <FaPlay />
              </PlaylistIcon>
              <h4>{playlist.name}</h4>
              <p style={{ color: '#6c757d', margin: '0.5rem 0' }}>
                {playlist.trackCount}曲
              </p>
            </PlaylistCard>
          ))}
        </PlaylistsGrid>
      ) : (
        <EmptyState>
          <h3>プレイリストがありません</h3>
          <p>プレイリストを作成すると、ここに表示されます。</p>
        </EmptyState>
      )}
    </>
  );

  if (loading) {
    return (
      <>
        <Header activePage="library" />
        <Container>
          <div style={{ textAlign: 'center', color: '#6c757d', marginTop: '2rem' }}>
            ライブラリを読み込み中...
          </div>
        </Container>
      </>
    );
  }

  return (
    <>
      <Header activePage="library" />
      <Container>
        <TabNavigation>
          <Tab 
            active={activeTab === 'purchased'} 
            onClick={() => setActiveTab('purchased')}
          >
            購入済み
          </Tab>
          <Tab 
            active={activeTab === 'favorites'} 
            onClick={() => setActiveTab('favorites')}
          >
            お気に入り
          </Tab>
          <Tab 
            active={activeTab === 'playlists'} 
            onClick={() => setActiveTab('playlists')}
          >
            プレイリスト
          </Tab>
        </TabNavigation>

        {activeTab === 'purchased' && renderPurchasedTracks()}
        {activeTab === 'favorites' && renderFavorites()}
        {activeTab === 'playlists' && renderPlaylists()}
      </Container>
    </>
  );
};

export default Library;
