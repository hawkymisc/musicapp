import React, { useState, useEffect, useContext } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { FaSearch, FaPlay, FaShoppingCart } from 'react-icons/fa';
import { AuthContext } from '../../contexts/AuthContext';
import { PlayerContext } from '../../contexts/PlayerContext';
import { searchTracks } from '../../services/track';
import Header from '../../components/layout/Header';
import Player from '../../components/player/Player';

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

const SearchForm = styled.form`
  display: flex;
  margin-bottom: 2rem;
`;

const SearchInput = styled.input`
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px 0 0 4px;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  }
`;

const SearchButton = styled.button`
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  padding: 0 1.5rem;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  
  svg {
    margin-right: 0.5rem;
  }
  
  &:hover {
    background-color: #0069d9;
  }
`;

const FiltersContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
  gap: 1rem;
`;

const FilterLabel = styled.label`
  margin-right: 0.5rem;
  color: #343a40;
  font-weight: 500;
`;

const FilterSelect = styled.select`
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.9rem;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const ResultsInfo = styled.div`
  margin-bottom: 1.5rem;
  color: #6c757d;
`;

const ResultsGrid = styled.div`
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

const TrackPrice = styled.div`
  color: #6c757d;
  margin-top: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
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

const NoResultsMessage = styled.div`
  color: #6c757d;
  text-align: center;
  padding: 2rem;
  width: 100%;
`;

const Loading = styled.div`
  color: #6c757d;
  text-align: center;
  padding: 2rem;
  width: 100%;
`;

const Search = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const queryParams = new URLSearchParams(location.search);
  
  const [searchQuery, setSearchQuery] = useState(queryParams.get('q') || '');
  const [genre, setGenre] = useState(queryParams.get('genre') || '');
  const [sortBy, setSortBy] = useState(queryParams.get('sort') || 'newest');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [totalResults, setTotalResults] = useState(0);
  
  const { user } = useContext(AuthContext);
  const { setCurrentTrack, setPlaylist } = useContext(PlayerContext);
  
  // URLからの検索パラメータに基づいて検索を実行
  useEffect(() => {
    const q = queryParams.get('q');
    const genreFilter = queryParams.get('genre');
    const sort = queryParams.get('sort');
    
    if (q) {
      setSearchQuery(q);
      
      if (genreFilter) {
        setGenre(genreFilter);
      }
      
      if (sort) {
        setSortBy(sort);
      }
      
      performSearch(q, genreFilter, sort);
    }
  }, [location.search]);
  
  const performSearch = async (query, genreFilter, sort) => {
    if (!query) return;
    
    setLoading(true);
    
    try {
      const searchResults = await searchTracks({
        query,
        genre: genreFilter || '',
        sort: sort || 'newest'
      });
      
      setResults(searchResults.tracks);
      setTotalResults(searchResults.total);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleSearch = (e) => {
    e.preventDefault();
    
    // 検索パラメータをURLに反映
    const params = new URLSearchParams();
    if (searchQuery) params.set('q', searchQuery);
    if (genre) params.set('genre', genre);
    if (sortBy) params.set('sort', sortBy);
    
    navigate(`/search?${params.toString()}`);
  };
  
  const handlePlayTrack = (track) => {
    setCurrentTrack(track);
    setPlaylist(results);
  };
  
  const handleBuyClick = (trackId) => {
    navigate(`/tracks/${trackId}`);
  };
  
  // ジャンルオプション
  const genreOptions = [
    { value: '', label: 'すべてのジャンル' },
    { value: 'ポップス', label: 'ポップス' },
    { value: 'ロック', label: 'ロック' },
    { value: 'ジャズ', label: 'ジャズ' },
    { value: 'クラシック', label: 'クラシック' },
    { value: 'ヒップホップ', label: 'ヒップホップ' },
    { value: 'エレクトロニック', label: 'エレクトロニック' },
    { value: 'フォーク', label: 'フォーク' },
    { value: 'その他', label: 'その他' }
  ];
  
  // ソートオプション
  const sortOptions = [
    { value: 'newest', label: '新着順' },
    { value: 'popular', label: '人気順' },
    { value: 'priceAsc', label: '価格（安い順）' },
    { value: 'priceDesc', label: '価格（高い順）' }
  ];
  
  return (
    <Container>
      <Header activePage="search" />
      
      <Content>
        <PageTitle>楽曲を検索</PageTitle>
        
        <SearchForm onSubmit={handleSearch}>
          <SearchInput
            type="text"
            placeholder="アーティスト名や楽曲タイトルで検索..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <SearchButton type="submit">
            <FaSearch />
            検索
          </SearchButton>
        </SearchForm>
        
        <FiltersContainer>
          <div>
            <FilterLabel htmlFor="genre">ジャンル:</FilterLabel>
            <FilterSelect
              id="genre"
              value={genre}
              onChange={(e) => setGenre(e.target.value)}
            >
              {genreOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </FilterSelect>
          </div>
          
          <div>
            <FilterLabel htmlFor="sortBy">並び替え:</FilterLabel>
            <FilterSelect
              id="sortBy"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              {sortOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </FilterSelect>
          </div>
        </FiltersContainer>
        
        {searchQuery && (
          <ResultsInfo>
            「{searchQuery}」の検索結果: {totalResults}件
          </ResultsInfo>
        )}
        
        {loading ? (
          <Loading>検索中...</Loading>
        ) : results.length === 0 ? (
          <NoResultsMessage>
            {searchQuery ? '検索結果が見つかりませんでした。' : '検索キーワードを入力してください。'}
          </NoResultsMessage>
        ) : (
          <ResultsGrid>
            {results.map(track => (
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
                    <BuyButton onClick={() => handleBuyClick(track.id)}>
                      <FaShoppingCart />
                      購入
                    </BuyButton>
                  </TrackPrice>
                </TrackDetails>
              </TrackCard>
            ))}
          </ResultsGrid>
        )}
      </Content>
      
      <Player />
    </Container>
  );
};

export default Search;