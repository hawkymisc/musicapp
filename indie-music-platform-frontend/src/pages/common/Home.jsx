import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { FaPlay, FaDownload, FaShoppingCart } from 'react-icons/fa';
import { AuthContext } from '../../contexts/AuthContext';
import { PlayerContext } from '../../contexts/PlayerContext';
import { getNewReleases, getFeaturedArtists } from '../../services/track';
import Header from '../../components/layout/Header';
import Player from '../../components/player/Player';
import SkeletonLoader from '../../components/common/SkeletonLoader';

const Container = styled.div`
  padding: 0 0 70px 0; // プレーヤーの高さ分の下部パディング
`;

const Content = styled.div`
  padding: 2rem;
  
  @media (max-width: 768px) {
    padding: 1rem;
  }
`;

const SectionTitle = styled.h2`
  margin-bottom: 1.5rem;
  color: #212529;
  font-size: 1.5rem;
`;

const TracksGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 1rem;
  }
  
  @media (max-width: 480px) {
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
  }
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

const TrackPrice = styled.div`
  color: #6c757d;
  margin-top: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ArtistsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1.5rem;
`;

const ArtistCard = styled.div`
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  text-align: center;
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-5px);
  }
`;

const ArtistAvatar = styled.div`
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background-color: #868e96;
  margin: 0 auto 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
  font-weight: bold;
`;

const ArtistTitle = styled(Link)`
  display: block;
  color: #212529;
  font-weight: 600;
  margin-bottom: 0.5rem;
  text-decoration: none;
  
  &:hover {
    color: #007bff;
  }
`;

const ArtistGenre = styled.div`
  color: #6c757d;
  font-size: 0.9rem;
`;

const BuyButton = styled.button`
  background-color: #28a745;
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
    background-color: #218838;
  }
`;

const Home = () => {
  const [newReleases, setNewReleases] = useState([]);
  const [featuredArtists, setFeaturedArtists] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const { user } = useContext(AuthContext);
  const { setCurrentTrack, setPlaylist } = useContext(PlayerContext);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [releasesData, artistsData] = await Promise.all([
          getNewReleases(),
          getFeaturedArtists()
        ]);
        
        setNewReleases(releasesData);
        setFeaturedArtists(artistsData);
      } catch (error) {
        console.error('Error fetching home data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  const handlePlayTrack = (track) => {
    setCurrentTrack(track);
    setPlaylist(newReleases);
  };
  
  return (
    <Container>
      <Header activePage="home" />
      
      <Content>
        <SectionTitle>新着楽曲</SectionTitle>
        
        <TracksGrid>
          {loading ? (
            <SkeletonLoader type="track-card" count={6} />
          ) : (
            newReleases.map(track => (
              <TrackCard key={track.id}>
                <TrackCover onClick={() => handlePlayTrack(track)}>
                  {track.coverArtUrl ? (
                    <img src={track.coverArtUrl} alt={track.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  ) : (
                    <span style={{ fontSize: '2rem' }}>♪</span>
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
                  <TrackPrice>
                    <span>¥{track.price.toLocaleString()}</span>
                    <BuyButton>
                      <FaShoppingCart />
                      購入
                    </BuyButton>
                  </TrackPrice>
                </TrackDetails>
              </TrackCard>
            ))
          )}
        </TracksGrid>
        
        <SectionTitle>おすすめアーティスト</SectionTitle>
        
        <ArtistsGrid>
          {loading ? (
            <SkeletonLoader type="list-item" count={4} />
          ) : (
            featuredArtists.map(artist => (
              <ArtistCard key={artist.id}>
                <ArtistAvatar>
                  {artist.profileImage ? (
                    <img src={artist.profileImage} alt={artist.displayName} style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '50%' }} />
                  ) : (
                    artist.displayName.charAt(0).toUpperCase()
                  )}
                </ArtistAvatar>
                <ArtistTitle to={`/artists/${artist.id}`}>{artist.displayName}</ArtistTitle>
                <ArtistGenre>{artist.genre || '多ジャンル'}</ArtistGenre>
              </ArtistCard>
            ))
          )}
        </ArtistsGrid>
      </Content>
      
      <Player />
    </Container>
  );
};

export default Home;
