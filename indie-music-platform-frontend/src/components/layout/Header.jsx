import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { FaSearch, FaUser } from 'react-icons/fa';
import { AuthContext } from '../../contexts/AuthContext';

const HeaderContainer = styled.header`
  background-color: #343a40;
  color: white;
  padding: 0 2rem;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  
  @media (max-width: 768px) {
    padding: 0 1rem;
    height: 56px;
  }
`;

const Logo = styled.div`
  font-size: 1.5rem;
  font-weight: bold;
  
  @media (max-width: 768px) {
    font-size: 1.2rem;
  }
`;

const Nav = styled.nav`
  display: flex;
  align-items: center;
  
  @media (max-width: 768px) {
    gap: 0.5rem;
  }
`;

const NavLink = styled(Link)`
  color: ${props => props.active ? '#ffffff' : '#cccccc'};
  text-decoration: none;
  margin: 0 1rem;
  font-size: 1rem;
  white-space: nowrap;
  
  &:hover {
    color: #ffffff;
  }
  
  @media (max-width: 768px) {
    margin: 0 0.5rem;
    font-size: 0.9rem;
  }
  
  @media (max-width: 480px) {
    margin: 0 0.25rem;
    font-size: 0.8rem;
  }
`;

const UserSection = styled.div`
  display: flex;
  align-items: center;
`;

const ArtistBadge = styled.div`
  background-color: #007bff;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: bold;
  margin-right: 1rem;
`;

const UserAvatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #6c757d;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
`;

const Header = ({ activePage }) => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  
  const handleAvatarClick = () => {
    // ユーザーメニューの表示などの処理
    // MVPフェーズではシンプルに実装
    if (window.confirm('ログアウトしますか？')) {
      logout();
      navigate('/login');
    }
  };

  return (
    <HeaderContainer>
      <Logo>INDIE MUSIC</Logo>
      
      <Nav>
        <NavLink to="/" active={activePage === 'home' ? 1 : 0}>ホーム</NavLink>
        <NavLink to="/search" active={activePage === 'search' ? 1 : 0}>検索</NavLink>
        {user?.type === 'artist' ? (
          <NavLink to="/artist/dashboard" active={activePage === 'artist' ? 1 : 0}>
            アーティストパネル
          </NavLink>
        ) : (
          <NavLink to="/library" active={activePage === 'library' ? 1 : 0}>
            マイライブラリ
          </NavLink>
        )}
      </Nav>
      
      <UserSection>
        {user?.type === 'artist' && <ArtistBadge>ARTIST</ArtistBadge>}
        <UserAvatar onClick={handleAvatarClick}>
          {user ? user.displayName?.charAt(0).toUpperCase() : <FaUser />}
        </UserAvatar>
      </UserSection>
    </HeaderContainer>
  );
};

export default Header;
