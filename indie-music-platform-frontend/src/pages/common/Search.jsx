import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import styled from 'styled-components';
import { FaSearch } from 'react-icons/fa';
import { searchTracks } from '../../services/track';
import Header from '../../components/layout/Header';

const Container = styled.div`
  padding: 2rem;
`;

const SearchForm = styled.form`
  display: flex;
  margin-bottom: 2rem;
  max-width: 600px;
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
  }
`;

const SearchButton = styled.button`
  padding: 0.75rem 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  
  &:hover {
    background-color: #0056b3;
  }
`;

const FilterSection = styled.div`
  margin-bottom: 2rem;
`;

const FilterSelect = styled.select`
  margin-right: 1rem;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
`;

const ResultsSection = styled.div`
  margin-top: 2rem;
`;

const ResultsTitle = styled.h2`
  margin-bottom: 1rem;
  color: #212529;
`;

const ResultsList = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
`;

const ResultItem = styled.div`
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-2px);
  }
`;

const NoResults = styled.div`
  text-align: center;
  color: #6c757d;
  margin-top: 2rem;
`;

const LoadingMessage = styled.div`
  text-align: center;
  color: #6c757d;
  margin-top: 2rem;
`;

const Search = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [genre, setGenre] = useState(searchParams.get('genre') || '');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  useEffect(() => {
    const initialQuery = searchParams.get('q');
    const initialGenre = searchParams.get('genre');
    
    if (initialQuery || initialGenre) {
      performSearch(initialQuery || '', initialGenre || '');
    }
  }, []);

  const performSearch = async (searchQuery, selectedGenre) => {
    setLoading(true);
    setHasSearched(true);
    
    try {
      const searchParams = {};
      if (searchQuery) searchParams.q = searchQuery;
      if (selectedGenre) searchParams.genre = selectedGenre;
      
      const searchResults = await searchTracks(searchParams);
      setResults(searchResults.data || []);
    } catch (error) {
      console.error('検索エラー:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // URLパラメータを更新
    const newSearchParams = new URLSearchParams();
    if (query) newSearchParams.set('q', query);
    if (genre) newSearchParams.set('genre', genre);
    setSearchParams(newSearchParams);
    
    performSearch(query, genre);
  };

  const handleGenreChange = (e) => {
    const newGenre = e.target.value;
    setGenre(newGenre);
    
    // ジャンルが変更されたら即座に検索
    if (hasSearched) {
      performSearch(query, newGenre);
    }
  };

  return (
    <>
      <Header activePage="search" />
      <Container>
        <SearchForm onSubmit={handleSubmit}>
          <SearchInput
            type="text"
            placeholder="楽曲、アーティストを検索..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <SearchButton type="submit">
            <FaSearch />
          </SearchButton>
        </SearchForm>

        <FilterSection>
          <FilterSelect value={genre} onChange={handleGenreChange}>
            <option value="">すべてのジャンル</option>
            <option value="pop">ポップ</option>
            <option value="rock">ロック</option>
            <option value="jazz">ジャズ</option>
            <option value="classical">クラシック</option>
            <option value="electronic">エレクトロニック</option>
            <option value="folk">フォーク</option>
            <option value="hiphop">ヒップホップ</option>
            <option value="other">その他</option>
          </FilterSelect>
        </FilterSection>

        {loading && <LoadingMessage>検索中...</LoadingMessage>}

        {!loading && hasSearched && (
          <ResultsSection>
            <ResultsTitle>
              検索結果 ({results.length}件)
            </ResultsTitle>
            
            {results.length > 0 ? (
              <ResultsList>
                {results.map(track => (
                  <ResultItem key={track.id}>
                    <h3>{track.title}</h3>
                    <p>アーティスト: {track.artistName}</p>
                    <p>ジャンル: {track.genre}</p>
                    <p>価格: ¥{track.price?.toLocaleString()}</p>
                  </ResultItem>
                ))}
              </ResultsList>
            ) : (
              <NoResults>
                検索条件に一致する楽曲が見つかりませんでした。
              </NoResults>
            )}
          </ResultsSection>
        )}

        {!hasSearched && (
          <NoResults>
            楽曲やアーティストを検索してください。
          </NoResults>
        )}
      </Container>
    </>
  );
};

export default Search;
