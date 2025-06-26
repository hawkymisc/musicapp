import React, { useState, useEffect, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { FaMusic, FaUpload, FaChartLine, FaEdit } from 'react-icons/fa';
import { AuthContext } from '../../contexts/AuthContext';
import { getArtistTracks, getArtistStats } from '../../services/artist';
import Header from '../../components/layout/Header';
import SkeletonLoader from '../../components/common/SkeletonLoader';
import RevenueChart from '../../components/analytics/RevenueChart';
import TrackStats from '../../components/analytics/TrackStats';

const Container = styled.div`
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const Sidebar = styled.div`
  width: 220px;
  background-color: #212529;
  color: white;
  padding-top: 60px; // ヘッダーの高さ分の調整
  
  @media (max-width: 768px) {
    width: 100%;
    padding-top: 0;
    order: 2;
  }
`;

const SidebarMenu = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const SidebarMenuItem = styled.li`
  padding: 0;
  
  a {
    display: block;
    padding: 1rem 1.5rem;
    color: ${props => props.active ? 'white' : '#adb5bd'};
    text-decoration: none;
    background-color: ${props => props.active ? '#343a40' : 'transparent'};
    display: flex;
    align-items: center;
    
    svg {
      margin-right: 0.75rem;
    }
    
    &:hover {
      background-color: #343a40;
      color: white;
    }
  }
`;

const Content = styled.div`
  flex: 1;
  padding: 80px 2rem 2rem; // ヘッダーの高さ分のトップパディング
  
  @media (max-width: 768px) {
    padding: 80px 1rem 1rem;
    order: 1;
  }
`;

const PageTitle = styled.h1`
  margin-bottom: 1.5rem;
  color: #343a40;
`;

const WelcomeCard = styled.div`
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  padding: 1.5rem;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const WelcomeText = styled.div`
  h2 {
    margin-bottom: 0.5rem;
    color: #212529;
  }
  
  p {
    color: #6c757d;
    margin-bottom: 0;
  }
`;

const UploadButton = styled(Link)`
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 0.75rem 1.5rem;
  text-decoration: none;
  display: flex;
  align-items: center;
  
  svg {
    margin-right: 0.5rem;
  }
  
  &:hover {
    background-color: #0069d9;
    color: white;
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const StatCard = styled.div`
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
`;

const StatTitle = styled.div`
  color: #6c757d;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
`;

const StatValue = styled.div`
  color: #212529;
  font-size: 1.75rem;
  font-weight: bold;
  display: flex;
  align-items: center;
`;

const StatTrend = styled.span`
  font-size: 0.9rem;
  margin-left: 0.5rem;
  color: ${props => props.positive ? '#28a745' : '#dc3545'};
`;

const SectionTitle = styled.h2`
  margin-bottom: 1.5rem;
  color: #343a40;
  font-size: 1.25rem;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const TableHeader = styled.thead`
  background-color: #f8f9fa;
`;

const TableHeaderCell = styled.th`
  padding: 1rem;
  text-align: left;
  border-bottom: 2px solid #dee2e6;
  color: #212529;
  font-weight: 600;
`;

const TableBody = styled.tbody``;

const TableRow = styled.tr`
  &:not(:last-child) {
    border-bottom: 1px solid #dee2e6;
  }
  
  &:hover {
    background-color: #f8f9fa;
  }
`;

const TableCell = styled.td`
  padding: 1rem;
  color: #212529;
`;

const ActionButton = styled(Link)`
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.3rem 0.6rem;
  font-size: 0.8rem;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  
  svg {
    margin-right: 0.3rem;
  }
  
  &:hover {
    background-color: #5a6268;
    color: white;
  }
`;

const ArtistDashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [tracks, setTracks] = useState([]);
  const [stats, setStats] = useState({
    totalPlays: 0,
    totalRevenue: 0,
    trackCount: 0,
    playsTrend: 0,
    revenueTrend: 0
  });
  const [loading, setLoading] = useState(true);
  
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();
  
  useEffect(() => {
    if (!user || user.type !== 'artist') {
      navigate('/login');
      return;
    }
    
    const fetchData = async () => {
      try {
        const [tracksData, statsData] = await Promise.all([
          getArtistTracks(user.uid),
          getArtistStats(user.uid)
        ]);
        
        setTracks(tracksData);
        setStats(statsData);
      } catch (error) {
        console.error('Error fetching artist data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [user, navigate]);
  
  return (
    <>
      <Header activePage="artist" />
      
      <Container>
        <Sidebar>
          <SidebarMenu>
            <SidebarMenuItem active={activeTab === 'dashboard'}>
              <Link to="/artist/dashboard" onClick={() => setActiveTab('dashboard')}>
                <FaChartLine />
                ダッシュボード
              </Link>
            </SidebarMenuItem>
            <SidebarMenuItem active={activeTab === 'tracks'}>
              <Link to="/artist/tracks" onClick={() => setActiveTab('tracks')}>
                <FaMusic />
                楽曲管理
              </Link>
            </SidebarMenuItem>
            <SidebarMenuItem active={activeTab === 'upload'}>
              <Link to="/artist/upload" onClick={() => setActiveTab('upload')}>
                <FaUpload />
                楽曲アップロード
              </Link>
            </SidebarMenuItem>
          </SidebarMenu>
        </Sidebar>
        
        <Content>
          <PageTitle>アーティストダッシュボード</PageTitle>
          
          <WelcomeCard>
            <WelcomeText>
              <h2>こんにちは、{user?.displayName || 'アーティスト'}さん</h2>
              <p>今週の再生回数は先週比{stats.playsTrend > 0 ? '+' : ''}{stats.playsTrend}%です。新曲のアップロードを検討してみませんか？</p>
            </WelcomeText>
            <UploadButton to="/artist/upload">
              <FaUpload />
              楽曲をアップロード
            </UploadButton>
          </WelcomeCard>
          
          <StatsGrid>
            <StatCard>
              <StatTitle>総再生回数</StatTitle>
              <StatValue>
                {loading ? '読み込み中...' : stats.totalPlays.toLocaleString()}
                {stats.playsTrend !== 0 && (
                  <StatTrend positive={stats.playsTrend > 0}>
                    {stats.playsTrend > 0 ? '+' : ''}{stats.playsTrend}%
                  </StatTrend>
                )}
              </StatValue>
            </StatCard>
            
            <StatCard>
              <StatTitle>今月の収益</StatTitle>
              <StatValue>
                {loading ? '読み込み中...' : `¥${stats.totalRevenue.toLocaleString()}`}
                {stats.revenueTrend !== 0 && (
                  <StatTrend positive={stats.revenueTrend > 0}>
                    {stats.revenueTrend > 0 ? '+' : ''}{stats.revenueTrend}%
                  </StatTrend>
                )}
              </StatValue>
            </StatCard>
            
            <StatCard>
              <StatTitle>公開中の楽曲</StatTitle>
              <StatValue>
                {loading ? '読み込み中...' : stats.trackCount}
              </StatValue>
            </StatCard>
          </StatsGrid>
          
          {/* 収益分析チャート */}
          <RevenueChart artistId={user?.uid} />
          
          {/* 楽曲統計 */}
          <TrackStats artistId={user?.uid} />
          
          <SectionTitle>あなたの楽曲</SectionTitle>
          
          {loading ? (
            <SkeletonLoader type="dashboard" />
          ) : tracks.length === 0 ? (
            <div>
              <p>まだ楽曲がありません。「楽曲をアップロード」ボタンから、最初の楽曲をアップロードしましょう。</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <tr>
                  <TableHeaderCell>タイトル</TableHeaderCell>
                  <TableHeaderCell>ジャンル</TableHeaderCell>
                  <TableHeaderCell>再生回数</TableHeaderCell>
                  <TableHeaderCell>収益</TableHeaderCell>
                  <TableHeaderCell>リリース日</TableHeaderCell>
                  <TableHeaderCell>アクション</TableHeaderCell>
                </tr>
              </TableHeader>
              <TableBody>
                {tracks.map(track => (
                  <TableRow key={track.id}>
                    <TableCell>{track.title}</TableCell>
                    <TableCell>{track.genre}</TableCell>
                    <TableCell>{track.playCount}</TableCell>
                    <TableCell>¥{track.revenue.toLocaleString()}</TableCell>
                    <TableCell>{new Date(track.releaseDate).toLocaleDateString('ja-JP')}</TableCell>
                    <TableCell>
                      <ActionButton to={`/artist/tracks/${track.id}/edit`}>
                        <FaEdit />
                        編集
                      </ActionButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </Content>
      </Container>
    </>
  );
};

export default ArtistDashboard;
