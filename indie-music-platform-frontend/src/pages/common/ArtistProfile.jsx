import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { FaUser, FaMusic, FaCalendar } from 'react-icons/fa';
import Header from '../../components/layout/Header';

const Container = styled.div`
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
`;

const ArtistHeader = styled.div`
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 2rem;
  margin-bottom: 3rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    text-align: center;
  }
`;

const ArtistAvatar = styled.div`
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background-color: #868e96;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 4rem;
  font-weight: bold;
  margin: 0 auto;
`;

const ArtistInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const ArtistName = styled.h1`
  color: #212529;
  margin: 0;
`;

const ArtistMeta = styled.div`
  display: flex;
  gap: 2rem;
  color: #6c757d;
  align-items: center;
  
  @media (max-width: 768px) {
    justify-content: center;
    flex-wrap: wrap;
  }
`;

const MetaItem = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const ArtistBio = styled.div`
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
`;

const SectionTitle = styled.h2`
  color: #212529;
  margin-bottom: 1.5rem;
`;

const TracksGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
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
`;

const TrackInfo = styled.div`
  padding: 1rem;
`;

const TrackTitle = styled.h4`
  margin: 0 0 0.5rem 0;
  color: #212529;
`;

const TrackMeta = styled.div`
  color: #6c757d;
  font-size: 0.9rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
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

const ArtistProfile = () => {
  const { artistId } = useParams();
  const [artist, setArtist] = useState(null);
  const [tracks, setTracks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchArtistData = async () => {
      try {
        setLoading(true);
        
        // アーティスト情報をモックデータで設定
        // 実際のAPIが実装されたら置き換える
        const artistData = {
          id: artistId,
          displayName: 'テストアーティスト',
          profileImage: null,
          biography: 'インディーズシーンで活動するアーティストです。独自のサウンドで多くのファンに愛されています。',
          genre: '多ジャンル',
          trackCount: 5,
          followerCount: 1250,
          joinDate: '2023-01-15'
        };
        
        // 楽曲リストをモックデータで設定
        const tracksData = [
          {
            id: 'track1',
            title: 'サンプル楽曲1',
            genre: 'ポップ',
            duration: 180,
            price: 300,
            coverArtUrl: null
          },
          {
            id: 'track2',
            title: 'サンプル楽曲2',
            genre: 'ロック',
            duration: 200,
            price: 350,
            coverArtUrl: null
          },
          {
            id: 'track3',
            title: 'サンプル楽曲3',
            genre: 'バラード',
            duration: 250,
            price: 400,
            coverArtUrl: null
          }
        ];
        
        setArtist(artistData);
        setTracks(tracksData);
      } catch (error) {
        console.error('アーティスト情報取得エラー:', error);
        setError('アーティスト情報の取得に失敗しました');
      } finally {
        setLoading(false);
      }
    };

    if (artistId) {
      fetchArtistData();
    }
  }, [artistId]);

  const formatDuration = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long'
    });
  };

  if (loading) {
    return (
      <>
        <Header />
        <Container>
          <LoadingMessage>アーティスト情報を読み込み中...</LoadingMessage>
        </Container>
      </>
    );
  }

  if (error || !artist) {
    return (
      <>
        <Header />
        <Container>
          <ErrorMessage>{error || 'アーティストが見つかりませんでした'}</ErrorMessage>
        </Container>
      </>
    );
  }

  return (
    <>
      <Header />
      <Container>
        <ArtistHeader>
          <ArtistAvatar>
            {artist.profileImage ? (
              <img 
                src={artist.profileImage} 
                alt={artist.displayName}
                style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '50%' }}
              />
            ) : (
              artist.displayName.charAt(0).toUpperCase()
            )}
          </ArtistAvatar>

          <ArtistInfo>
            <ArtistName>{artist.displayName}</ArtistName>
            
            <ArtistMeta>
              <MetaItem>
                <FaMusic />
                <span>{artist.trackCount}曲</span>
              </MetaItem>
              <MetaItem>
                <FaUser />
                <span>{artist.followerCount?.toLocaleString()}フォロワー</span>
              </MetaItem>
              <MetaItem>
                <FaCalendar />
                <span>{formatDate(artist.joinDate)}から活動</span>
              </MetaItem>
            </ArtistMeta>
            
            <div>
              <strong>ジャンル:</strong> {artist.genre}
            </div>
          </ArtistInfo>
        </ArtistHeader>

        {artist.biography && (
          <ArtistBio>
            <h3>アーティストについて</h3>
            <p>{artist.biography}</p>
          </ArtistBio>
        )}

        <SectionTitle>楽曲</SectionTitle>
        
        {tracks.length > 0 ? (
          <TracksGrid>
            {tracks.map(track => (
              <TrackCard key={track.id}>
                <TrackCover>
                  {track.coverArtUrl ? (
                    <img 
                      src={track.coverArtUrl} 
                      alt={track.title}
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  ) : (
                    <span>♪</span>
                  )}
                </TrackCover>
                
                <TrackInfo>
                  <TrackTitle>{track.title}</TrackTitle>
                  <TrackMeta>
                    <span>{track.genre} • {formatDuration(track.duration)}</span>
                    <span>¥{track.price?.toLocaleString()}</span>
                  </TrackMeta>
                </TrackInfo>
              </TrackCard>
            ))}
          </TracksGrid>
        ) : (
          <div style={{ textAlign: 'center', color: '#6c757d', marginTop: '2rem' }}>
            まだ楽曲がアップロードされていません
          </div>
        )}
      </Container>
    </>
  );
};

export default ArtistProfile;
