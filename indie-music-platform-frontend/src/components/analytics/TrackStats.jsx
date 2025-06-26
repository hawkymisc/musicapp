import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaPlay, FaDownload, FaHeart, FaShare } from 'react-icons/fa';

const StatsContainer = styled.div`
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 1.5rem;
`;

const StatsTitle = styled.h3`
  margin-bottom: 1.5rem;
  color: #343a40;
  font-size: 1.1rem;
`;

const TrackList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const TrackItem = styled.div`
  display: flex;
  align-items: center;
  padding: 1rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: #f8f9fa;
  }
`;

const TrackCover = styled.div`
  width: 60px;
  height: 60px;
  background-color: #e9ecef;
  border-radius: 4px;
  margin-right: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  font-size: 1.5rem;
`;

const TrackInfo = styled.div`
  flex: 1;
  margin-right: 1rem;
`;

const TrackTitle = styled.div`
  font-weight: 600;
  color: #212529;
  margin-bottom: 0.25rem;
`;

const TrackMeta = styled.div`
  font-size: 0.85rem;
  color: #6c757d;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  gap: 1rem;
  margin-left: 1rem;
`;

const StatItem = styled.div`
  text-align: center;
  padding: 0.5rem;
`;

const StatIcon = styled.div`
  color: #007bff;
  margin-bottom: 0.25rem;
  font-size: 1.1rem;
`;

const StatValue = styled.div`
  font-weight: 600;
  color: #212529;
  font-size: 0.9rem;
  margin-bottom: 0.1rem;
`;

const StatLabel = styled.div`
  font-size: 0.7rem;
  color: #6c757d;
`;

const FilterControls = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
`;

const FilterButton = styled.button`
  padding: 0.5rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  background: ${props => props.active ? '#007bff' : 'white'};
  color: ${props => props.active ? 'white' : '#495057'};
  cursor: pointer;
  font-size: 0.85rem;
  
  &:hover {
    background: ${props => props.active ? '#0056b3' : '#f8f9fa'};
  }
`;

const SortSelect = styled.select`
  padding: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  background: white;
  color: #495057;
  cursor: pointer;
`;

const TrackStats = ({ artistId }) => {
  const [tracks, setTracks] = useState([]);
  const [period, setPeriod] = useState('30d');
  const [sortBy, setSortBy] = useState('plays');
  const [loading, setLoading] = useState(true);

  // モックデータ生成
  const generateMockTracks = () => {
    const trackNames = [
      'Summer Vibes',
      'Midnight Dreams',
      'City Lights',
      'Ocean Waves',
      'Mountain High',
      'Rain Dance',
      'Sunset Boulevard',
      'Electric Nights'
    ];

    return trackNames.map((name, index) => ({
      id: index + 1,
      title: name,
      releaseDate: new Date(2024, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28)),
      duration: Math.floor(Math.random() * 120 + 180), // 3-5分
      stats: {
        plays: Math.floor(Math.random() * 10000 + 500),
        downloads: Math.floor(Math.random() * 500 + 50),
        likes: Math.floor(Math.random() * 1000 + 100),
        shares: Math.floor(Math.random() * 200 + 20),
        revenue: Math.floor(Math.random() * 50000 + 5000)
      }
    }));
  };

  useEffect(() => {
    const fetchTrackStats = async () => {
      setLoading(true);
      
      // 実際のAPIコールに置き換え
      await new Promise(resolve => setTimeout(resolve, 800));
      
      const mockTracks = generateMockTracks();
      
      // ソート処理
      const sortedTracks = [...mockTracks].sort((a, b) => {
        switch (sortBy) {
          case 'plays':
            return b.stats.plays - a.stats.plays;
          case 'downloads':
            return b.stats.downloads - a.stats.downloads;
          case 'revenue':
            return b.stats.revenue - a.stats.revenue;
          case 'likes':
            return b.stats.likes - a.stats.likes;
          default:
            return b.stats.plays - a.stats.plays;
        }
      });
      
      setTracks(sortedTracks);
      setLoading(false);
    };
    
    fetchTrackStats();
  }, [period, sortBy, artistId]);

  const formatDuration = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  if (loading) {
    return (
      <StatsContainer>
        <StatsTitle>楽曲統計</StatsTitle>
        <div>読み込み中...</div>
      </StatsContainer>
    );
  }

  return (
    <StatsContainer>
      <StatsTitle>楽曲統計</StatsTitle>
      
      <FilterControls>
        <FilterButton 
          active={period === '7d'} 
          onClick={() => setPeriod('7d')}
        >
          7日間
        </FilterButton>
        <FilterButton 
          active={period === '30d'} 
          onClick={() => setPeriod('30d')}
        >
          30日間
        </FilterButton>
        <FilterButton 
          active={period === '90d'} 
          onClick={() => setPeriod('90d')}
        >
          90日間
        </FilterButton>
        
        <SortSelect value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
          <option value="plays">再生数順</option>
          <option value="downloads">ダウンロード数順</option>
          <option value="revenue">収益順</option>
          <option value="likes">お気に入り数順</option>
        </SortSelect>
      </FilterControls>

      <TrackList>
        {tracks.map((track, index) => (
          <TrackItem key={track.id}>
            <TrackCover>
              ♪
            </TrackCover>
            
            <TrackInfo>
              <TrackTitle>{track.title}</TrackTitle>
              <TrackMeta>
                {formatDuration(track.duration)} • {track.releaseDate.toLocaleDateString('ja-JP')}
              </TrackMeta>
            </TrackInfo>
            
            <StatsGrid>
              <StatItem>
                <StatIcon><FaPlay /></StatIcon>
                <StatValue>{formatNumber(track.stats.plays)}</StatValue>
                <StatLabel>再生</StatLabel>
              </StatItem>
              
              <StatItem>
                <StatIcon><FaDownload /></StatIcon>
                <StatValue>{formatNumber(track.stats.downloads)}</StatValue>
                <StatLabel>DL</StatLabel>
              </StatItem>
              
              <StatItem>
                <StatIcon><FaHeart /></StatIcon>
                <StatValue>{formatNumber(track.stats.likes)}</StatValue>
                <StatLabel>いいね</StatLabel>
              </StatItem>
              
              <StatItem>
                <StatIcon><FaShare /></StatIcon>
                <StatValue>{formatNumber(track.stats.shares)}</StatValue>
                <StatLabel>シェア</StatLabel>
              </StatItem>
            </StatsGrid>
          </TrackItem>
        ))}
      </TrackList>
    </StatsContainer>
  );
};

export default TrackStats;